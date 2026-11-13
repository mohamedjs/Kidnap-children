from datetime import date
from uuid import uuid4

import pytest

from app.modules.matching.domain.match import CONFIRMED, DISMISSED, Match
from app.modules.matching.domain.scoring import (
    Profile,
    attribute_score,
    best_face_confidence,
    combine,
    cosine,
    face_confidence,
    haversine_km,
    normalize_city,
)
from app.shared.domain.errors import Forbidden, Invalid

TODAY = date(2026, 11, 13)
M = Profile("missing", "male", 6, "Cairo", 30.0444, 31.2357, date(2026, 10, 1))
F = Profile("found", "male", 6, "Cairo", 30.0500, 31.2400, date(2026, 10, 5))


def test_perfect_pair_scores_high() -> None:
    score, reasons = attribute_score(M, F, TODAY)  # type: ignore[misc]
    assert score == 100
    assert {"same_gender", "close_dates", "same_age", "very_near"} <= set(reasons)


def test_kinds_must_be_missing_then_found() -> None:
    assert attribute_score(F, M, TODAY) is None
    assert attribute_score(M, M, TODAY) is None


def test_different_gender_is_impossible() -> None:
    assert attribute_score(M, Profile("found", "female", 6, "Cairo"), TODAY) is None


def test_age_gap_too_large_is_impossible() -> None:
    assert attribute_score(M, Profile("found", "male", 12, "Cairo", seen_on=date(2026, 10, 5)), TODAY) is None


def test_child_grows_between_dates() -> None:
    missing = Profile("missing", "male", 4, "Cairo", seen_on=date(2022, 10, 1))
    found = Profile("found", "male", 8, "Cairo", seen_on=date(2026, 10, 2))
    res = attribute_score(missing, found, TODAY)
    assert res is not None and "same_age" in res[1]


def test_found_long_before_missing_is_impossible() -> None:
    found = Profile("found", "male", 6, "Cairo", seen_on=date(2026, 6, 1))
    assert attribute_score(M, found, TODAY) is None


def test_unknowns_give_partial_credit() -> None:
    res = attribute_score(Profile("missing", city="Giza"), Profile("found", city="giza"), TODAY)
    assert res is not None
    score, reasons = res
    assert 0 < score < 60 and "same_city" in reasons


def test_city_normalisation_handles_arabic_spellings() -> None:
    assert normalize_city("الإسكندرية") == normalize_city("اسكندريه")
    assert normalize_city(" Cairo ") == "cairo"


def test_distance() -> None:
    assert haversine_km(30.0444, 31.2357, 31.2001, 29.9187) == pytest.approx(180, rel=0.05)


def test_cosine_and_v1_confidence_scale() -> None:
    assert cosine([1, 0], [1, 0]) == pytest.approx(1)
    assert cosine([1, 0], [0, 1]) == pytest.approx(0)
    assert face_confidence(1) == 100 and face_confidence(-1) == 0 and face_confidence(0) == 50
    assert best_face_confidence([], [[1.0]]) is None
    assert best_face_confidence([[1, 0], [0, 1]], [[0, 1]]) == pytest.approx(100)


def test_face_is_blended_in() -> None:
    s = combine(M, F, None, TODAY)
    assert s is not None and s.total == 100 and s.face is None and s.suggest
    s2 = combine(M, F, 50.0, TODAY)
    assert s2 is not None and s2.total == pytest.approx(80) and s2.face == 50


def test_match_decisions() -> None:
    m = Match(uuid4(), uuid4(), uuid4(), uuid4(), uuid4(), 80, 80, None, [])
    with pytest.raises(Forbidden):
        m.decide(uuid4(), False, True)
    m.decide(m.found_owner_id, False, True)
    assert m.status == CONFIRMED and m.decided_by == m.found_owner_id
    with pytest.raises(Invalid):
        m.decide(m.missing_owner_id, False, False)
    m2 = Match(uuid4(), uuid4(), uuid4(), uuid4(), uuid4(), 80, 80, None, [])
    m2.decide(uuid4(), True, False)
    assert m2.status == DISMISSED
