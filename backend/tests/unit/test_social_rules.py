from datetime import date
from uuid import uuid4

import pytest

from app.modules.engagement.domain.engagement import Comment, clean_comment
from app.modules.identity.domain.user import (
    User,
    check_password,
    clean_birth_date,
    clean_phone,
    normalize_email,
)
from app.modules.messaging.domain.message import check_message
from app.modules.moderation.domain.flag import check_reason, should_auto_hide
from app.modules.notifications.domain.notification import notifications_for
from app.shared.domain.errors import Invalid
from app.shared.domain.principal import ROLE_ADMIN, Principal


# identity
def test_email_and_password_rules() -> None:
    assert normalize_email("  Demo@Example.ORG ") == "demo@example.org"
    with pytest.raises(Invalid):
        normalize_email("not-an-email")
    for bad in ("short1", "onlyletters", "12345678"):
        with pytest.raises(Invalid):
            check_password(bad)
    check_password("letters123")


def test_profile_cleaning() -> None:
    assert clean_phone(" +20 100 000 0000 ") == "+20 100 000 0000"
    assert clean_phone("") is None
    with pytest.raises(Invalid):
        clean_phone("call me")
    with pytest.raises(Invalid):
        clean_birth_date(date(2030, 1, 1), date(2026, 11, 13))


def test_block_and_role_change_revoke_tokens() -> None:
    u = User(uuid4(), "a@b.co", "Demo", "hash")
    u.block()
    assert not u.is_active and u.token_version == 1
    u.set_role(ROLE_ADMIN)
    assert u.role == ROLE_ADMIN and u.token_version == 2
    with pytest.raises(Invalid):
        u.set_role("root")


# engagement
def test_comment_rules() -> None:
    assert clean_comment("  hi  ") == "hi"
    with pytest.raises(Invalid):
        clean_comment("   ")
    owner, author = uuid4(), uuid4()
    c = Comment(uuid4(), uuid4(), author, "x")
    assert c.can_delete(Principal(author), owner)
    assert c.can_delete(Principal(owner), owner)
    assert c.can_delete(Principal(uuid4(), ROLE_ADMIN), owner)
    assert not c.can_delete(Principal(uuid4()), owner)
    assert not c.can_delete(None, owner)


# messaging
def test_message_rules() -> None:
    a, b = uuid4(), uuid4()
    with pytest.raises(Invalid):
        check_message(a, a, "hi", False)
    with pytest.raises(Invalid):
        check_message(a, b, "  ", False)
    assert check_message(a, b, None, True) is None
    assert check_message(a, b, " hi ", False) == "hi"


# moderation
def test_flag_rules() -> None:
    assert check_reason("fake", None) == ("fake", None)
    with pytest.raises(Invalid):
        check_reason("spam!", None)
    with pytest.raises(Invalid):
        check_reason("other", " ")
    assert should_auto_hide(3, False) and not should_auto_hide(2, False) and not should_auto_hide(5, True)


# notifications
def test_who_gets_notified() -> None:
    owner, author = str(uuid4()), str(uuid4())
    [n] = notifications_for("comment.added", {"report_owner_id": owner, "author_id": author, "report_id": "r1"})
    assert n.user_id == owner and n.link == "/reports/r1" and n.actor_id == author
    assert notifications_for("comment.added", {"report_owner_id": owner, "author_id": owner}) == []
    m, f = str(uuid4()), str(uuid4())
    both = notifications_for("match.suggested", {"missing_owner_id": m, "found_owner_id": f, "match_id": "x"})
    assert {n.user_id for n in both} == {m, f}
    [other] = notifications_for("match.confirmed", {"missing_owner_id": m, "found_owner_id": f, "by": m})
    assert other.user_id == f
    assert notifications_for("report.published", {}) == []
