"""Modular-monolith rules, checked on every test run (AST, no imports executed):

1. A module reaches another module only through its package root (`app.modules.<name>`,
   i.e. its __init__.py public API) - never `app.modules.<name>.domain...` etc.
2. domain/ is pure Python: no FastAPI/Starlette/Pydantic/SQLAlchemy/boto3/httpx/OpenCV/numpy,
   no shared infrastructure or presentation, and no other module.
3. application/ uses no web, ORM or SDK libraries and nothing from its own infrastructure/
   or presentation/ layer.
4. Only infrastructure/ layers (module or shared) import SQLAlchemy, psycopg, boto3, httpx or OpenCV.
5. Every module has the four layers and an __init__.py that declares __all__.
"""

import ast
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[1] / "app"
MODULES = APP / "modules"
MODULE_NAMES = sorted(p.name for p in MODULES.iterdir() if p.is_dir() and not p.name.startswith("__"))
LAYERS = ("domain", "application", "infrastructure", "presentation")

FRAMEWORKS = ("fastapi", "starlette", "pydantic", "sqlalchemy", "psycopg", "boto3", "botocore", "httpx", "cv2",
              "numpy", "alembic", "jwt", "argon2")
INFRA_ONLY = ("sqlalchemy", "psycopg", "boto3", "botocore", "httpx", "cv2", "alembic")


def py_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)


def dotted(path: Path) -> str:
    rel = path.relative_to(APP.parent).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    pkg = dotted(path) if path.name == "__init__.py" else dotted(path).rsplit(".", 1)[0]
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = pkg.split(".")
                base = base[: len(base) - (node.level - 1)]
                mod = ".".join(base + ([node.module] if node.module else []))
            else:
                mod = node.module or ""
            out.append(mod)
            # `from app.modules import reports` targets the package root of `reports`
            if mod == "app.modules":
                out += [f"app.modules.{a.name}" for a in node.names]
    return out


def module_of(path: Path) -> str | None:
    try:
        return path.relative_to(MODULES).parts[0]
    except ValueError:
        return None


def layer_of(path: Path) -> str | None:
    parts = path.relative_to(APP).parts
    for layer in LAYERS:
        if layer in parts[:-1]:
            return layer
    return None


def top(name: str) -> str:
    return name.split(".")[0]


ALL_FILES = py_files(APP)


def test_modules_exist() -> None:
    assert {"identity", "media", "reports", "matching"} <= set(MODULE_NAMES)


@pytest.mark.parametrize("name", MODULE_NAMES)
def test_module_shape(name: str) -> None:
    root = MODULES / name
    for layer in LAYERS:
        assert (root / layer).is_dir(), f"{name} lacks {layer}/"
    init = (root / "__init__.py").read_text()
    assert "__all__" in init, f"{name}/__init__.py must declare its public API in __all__"


def test_cross_module_imports_use_public_api() -> None:
    violations = []
    for f in ALL_FILES:
        own = module_of(f)
        for imp in imports(f):
            if not imp.startswith("app.modules."):
                continue
            parts = imp.split(".")
            target = parts[2]
            if target != own and len(parts) > 3:
                violations.append(f"{f.relative_to(APP)} -> {imp}")
    assert violations == []


def test_domain_is_pure() -> None:
    violations = []
    for f in ALL_FILES:
        if layer_of(f) != "domain":
            continue
        own = module_of(f)
        for imp in imports(f):
            bad = (
                top(imp) in FRAMEWORKS
                or imp.startswith(("app.shared.infrastructure", "app.shared.presentation", "app.shared.application"))
                or (imp.startswith("app.modules.") and imp.split(".")[2] != own)
                or any(f".{layer}" in imp for layer in ("application", "infrastructure", "presentation"))
            )
            if bad:
                violations.append(f"{f.relative_to(APP)} -> {imp}")
    assert violations == []


def test_application_has_no_frameworks_or_adapters() -> None:
    violations = []
    for f in ALL_FILES:
        if layer_of(f) != "application":
            continue
        own = module_of(f)
        for imp in imports(f):
            bad = (
                top(imp) in FRAMEWORKS
                or imp.startswith(("app.shared.infrastructure", "app.shared.presentation"))
                or (own is not None and imp.startswith((f"app.modules.{own}.infrastructure",
                                                        f"app.modules.{own}.presentation")))
            )
            if bad:
                violations.append(f"{f.relative_to(APP)} -> {imp}")
    assert violations == []


def test_only_infrastructure_touches_db_storage_and_http_clients() -> None:
    violations = []
    for f in ALL_FILES:
        if layer_of(f) == "infrastructure":
            continue
        for imp in imports(f):
            if top(imp) in INFRA_ONLY:
                violations.append(f"{f.relative_to(APP)} -> {imp}")
    assert violations == []


def test_no_import_cycles_between_modules() -> None:
    graph: dict[str, set[str]] = {m: set() for m in MODULE_NAMES}
    for f in ALL_FILES:
        own = module_of(f)
        if own is None:
            continue
        for imp in imports(f):
            if imp.startswith("app.modules.") and (t := imp.split(".")[2]) != own and t in graph:
                graph[own].add(t)

    seen: dict[str, int] = {}

    def visit(n: str, path: list[str]) -> None:
        if seen.get(n) == 1:
            raise AssertionError("module cycle: " + " -> ".join(path + [n]))
        if seen.get(n) == 2:
            return
        seen[n] = 1
        for nxt in sorted(graph[n]):
            visit(nxt, path + [n])
        seen[n] = 2

    for m in MODULE_NAMES:
        visit(m, [])
