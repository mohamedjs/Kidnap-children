#!/usr/bin/env python3
"""Create ./.env from .env.example with random dev secrets. Never overwrites, never prints values."""
import pathlib
import secrets
import sys

root = pathlib.Path(__file__).resolve().parent.parent
env = root / ".env"
if env.exists():
    print(".env already exists - leaving it alone")
    sys.exit(0)

tok = secrets.token_urlsafe
pg = tok(18)
text = (root / ".env.example").read_text()
for old, new in {
    "POSTGRES_PASSWORD=__generate__": f"POSTGRES_PASSWORD={pg}",
    "__POSTGRES_PASSWORD__": pg,
    "S3_ACCESS_KEY=__generate__": f"S3_ACCESS_KEY=dev{secrets.token_hex(8)}",
    "S3_SECRET_KEY=__generate__": f"S3_SECRET_KEY={tok(30)}",
    "JWT_SECRET=__generate__": f"JWT_SECRET={tok(40)}",
    "ADMIN_SEED_PASSWORD=__generate__": f"ADMIN_SEED_PASSWORD={tok(12)}",
}.items():
    text = text.replace(old, new)
env.write_text(text)
env.chmod(0o600)
print("wrote .env (values not printed)")
