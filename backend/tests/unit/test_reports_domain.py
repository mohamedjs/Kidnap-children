from datetime import UTC, date, datetime
from uuid import uuid4

import pytest

from app.modules.reports.domain.report import (
    HIDDEN,
    MAX_PHOTOS,
    OPEN,
    RESOLVED,
    Photo,
    Report,
    ReportDraft,
    build_criteria,
    validate_draft,
)
from app.shared.domain.errors import Forbidden, Invalid
from app.shared.domain.principal import ROLE_ADMIN, Principal

TODAY = date(2026, 11, 13)


def draft(**kw: object) -> ReportDraft:
    base: dict[str, object] = dict(kind="missing", description="Last seen near the market wearing a red coat.",
                                   city="Cairo", child_name="Demo Child", gender="female", age=7)
    base.update(kw)
    return ReportDraft(**base)  # type: ignore[arg-type]


def report(**kw: object) -> Report:
    base: dict[str, object] = dict(id=uuid4(), owner_id=uuid4(), kind="missing", status=OPEN,
                                   description="x" * 20, city="Cairo")
    base.update(kw)
    return Report(**base)  # type: ignore[arg-type]


def test_valid_missing_report_is_normalised() -> None:
    d = validate_draft(draft(child_name="  Demo   Child ", city=" Giza  "), TODAY)
    assert d.child_name == "Demo Child" and d.city == "Giza"


def test_legacy_kinds_map_to_v2() -> None:
    assert validate_draft(draft(kind="missed"), TODAY).kind == "missing"
    assert validate_draft(draft(kind="founded", child_name=None), TODAY).kind == "found"


@pytest.mark.parametrize(("change", "code"), [
    ({"child_name": None}, "child_name"),
    ({"kind": "lost"}, "kind"),
    ({"age": 18}, "age"),
    ({"age": -1}, "age"),
    ({"gender": "x"}, "gender"),
    ({"description": "short"}, "description"),
    ({"city": ""}, "city"),
    ({"lat": 30.0}, "location"),
    ({"lat": 95.0, "lng": 31.0}, "location"),
    ({"seen_on": date(2026, 12, 1)}, "seen_on"),
])
def test_invalid_drafts(change: dict[str, object], code: str) -> None:
    with pytest.raises(Invalid) as e:
        validate_draft(draft(**change), TODAY)
    assert e.value.code == code


def test_found_report_may_have_no_name() -> None:
    assert validate_draft(draft(kind="found", child_name=None), TODAY).child_name is None


def test_only_owner_or_admin_edits_and_sees_hidden() -> None:
    r = report()
    owner, stranger, admin = Principal(r.owner_id), Principal(uuid4()), Principal(uuid4(), ROLE_ADMIN)
    assert r.can_edit(owner) and r.can_edit(admin) and not r.can_edit(stranger) and not r.can_edit(None)
    with pytest.raises(Forbidden):
        r.require_editor(stranger)
    r.hide("duplicate")
    assert not r.visible_to(stranger) and not r.visible_to(None) and r.visible_to(owner)


def test_status_lifecycle() -> None:
    r = report()
    r.resolve(datetime.now(UTC))
    assert r.status == RESOLVED and r.resolved_at is not None and not r.matchable
    with pytest.raises(Invalid):
        r.resolve(datetime.now(UTC))
    r.reopen()
    assert r.status == OPEN and r.resolved_at is None and r.matchable
    with pytest.raises(Invalid):
        r.reopen()


def test_hide_and_unhide_restore_previous_status() -> None:
    r = report(status=RESOLVED)
    with pytest.raises(Invalid):
        r.hide("  ")
    r.hide("fake report")
    assert r.status == HIDDEN and r.hidden_reason == "fake report"
    r.unhide()
    assert r.status == RESOLVED and r.hidden_reason is None


def test_kind_cannot_change_on_edit() -> None:
    with pytest.raises(Invalid):
        report().apply(validate_draft(draft(kind="found"), TODAY))


def test_photo_limit_and_positions() -> None:
    r = report()
    r.add_photos([Photo(uuid4(), f"k{i}", 0) for i in range(3)])
    assert [p.position for p in r.photos] == [0, 1, 2]
    removed = r.remove_photos({r.photos[1].id})
    assert removed == ["k1"] and len(r.photos) == 2
    with pytest.raises(Invalid):
        r.add_photos([Photo(uuid4(), "x", 0) for _ in range(MAX_PHOTOS - 1)])


def test_search_criteria_v1_filters() -> None:
    c = build_criteria(q="  red   coat ", kind="missed", gender="female", age_from=12, age_to=5)
    assert c.q == "red coat" and c.kind == "missing" and (c.age_from, c.age_to) == (5, 12)
    assert build_criteria(age=7).age_from == 7 == build_criteria(age=7).age_to
    assert build_criteria(age_to=40).age_to == 17
    assert build_criteria(gender="other").gender is None
    assert build_criteria().statuses == (OPEN, RESOLVED)


def test_hidden_listing_is_admin_only() -> None:
    with pytest.raises(Forbidden):
        build_criteria(status="hidden", viewer=Principal(uuid4()))
    assert build_criteria(status="hidden", viewer=Principal(uuid4(), ROLE_ADMIN)).statuses == ("hidden",)
