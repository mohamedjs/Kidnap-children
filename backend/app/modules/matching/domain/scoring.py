"""How a missing report and a found report are compared.

Attribute score (0-100) from four signals; each pair that is impossible (different gender,
age too far apart, child found long before going missing) is excluded outright:

    gender    25   same gender (10 when one side is unknown)
    age       30   expected age now vs. reported age (8 when unknown)
    place     25   distance from coordinates, else same city
    time      20   how close the two dates are

When both reports have face embeddings the face similarity is blended in (v1 kept the
0-100 "confidence" scale: (cosine + 1) / 2 * 100).
"""

import math
from dataclasses import dataclass, field
from datetime import date

SUGGEST_THRESHOLD = 60.0
FACE_WEIGHT = 0.4
MAX_AGE_GAP = 4
EARLY_FOUND_TOLERANCE_DAYS = 30


@dataclass(frozen=True)
class Profile:
    """The facts of one report the matcher looks at."""

    kind: str
    gender: str | None = None
    age: int | None = None
    city: str | None = None
    lat: float | None = None
    lng: float | None = None
    seen_on: date | None = None


@dataclass(frozen=True)
class Score:
    total: float
    attributes: float
    face: float | None = None
    reasons: tuple[str, ...] = field(default_factory=tuple)

    @property
    def suggest(self) -> bool:
        return self.total >= SUGGEST_THRESHOLD


def normalize_city(city: str | None) -> str:
    if not city:
        return ""
    s = city.strip().lower()
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ة", "ه"), ("ى", "ي")):
        s = s.replace(a, b)
    return s.removeprefix("ال").replace(" ", "")


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def attribute_score(missing: Profile, found: Profile, today: date) -> tuple[float, list[str]] | None:
    """None when the two reports cannot be the same child."""
    if missing.kind != "missing" or found.kind != "found":
        return None
    score, reasons = 0.0, []

    # gender
    if missing.gender and found.gender:
        if missing.gender != found.gender:
            return None
        score += 25
        reasons.append("same_gender")
    else:
        score += 10

    # dates: a child cannot be found long before it went missing
    if missing.seen_on and found.seen_on:
        early = (missing.seen_on - found.seen_on).days
        if early > EARLY_FOUND_TOLERANCE_DAYS:
            return None
        gap = abs((found.seen_on - missing.seen_on).days)
        if gap <= 30:
            score += 20
            reasons.append("close_dates")
        elif gap <= 365:
            score += 10
        else:
            score += 4
    else:
        score += 6

    # age: the missing child has grown since it was last seen
    if missing.age is not None and found.age is not None:
        ref = found.seen_on or today
        grown = 0
        if missing.seen_on and ref > missing.seen_on:
            grown = (ref - missing.seen_on).days // 365
        diff = abs((missing.age + grown) - found.age)
        if diff > MAX_AGE_GAP:
            return None
        score += {0: 30, 1: 26, 2: 18, 3: 10}.get(diff, 4)
        if diff <= 1:
            reasons.append("same_age")
    else:
        score += 8

    # place
    if None not in (missing.lat, missing.lng, found.lat, found.lng):
        km = haversine_km(missing.lat, missing.lng, found.lat, found.lng)  # type: ignore[arg-type]
        if km <= 5:
            score += 25
            reasons.append("very_near")
        elif km <= 25:
            score += 18
            reasons.append("near")
        elif km <= 100:
            score += 8
    elif normalize_city(missing.city) and normalize_city(missing.city) == normalize_city(found.city):
        score += 18
        reasons.append("same_city")

    return min(score, 100.0), reasons


def cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na > 1e-9 and nb > 1e-9 else 0.0


def face_confidence(cos: float) -> float:
    """v1 scale: cosine in [-1, 1] -> 0..100."""
    return max(0.0, min(100.0, (cos + 1.0) / 2.0 * 100.0))


def best_face_confidence(left: list[list[float]], right: list[list[float]]) -> float | None:
    if not left or not right:
        return None
    return max(face_confidence(cosine(a, b)) for a in left for b in right)


def combine(missing: Profile, found: Profile, face: float | None, today: date) -> Score | None:
    attrs = attribute_score(missing, found, today)
    if attrs is None:
        return None
    attr_score, reasons = attrs
    total = attr_score if face is None else (1 - FACE_WEIGHT) * attr_score + FACE_WEIGHT * face
    if face is not None and face >= 90:
        reasons.append("similar_face")
    return Score(round(total, 1), round(attr_score, 1), None if face is None else round(face, 1), tuple(reasons))
