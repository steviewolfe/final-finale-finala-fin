"""Agent 3: Scorer (plain Python, no LLM, no randomness).

Same evidence plus the same profile always gives the same numbers.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .profiles import FLAG_SCORE, FLAG_WEIGHT, PROFILES
from .schemas import CATEGORIES, Evidence

SIGNAL_VALUE = {"positive": 100, "unclear": 40, "negative": 0}


@dataclass
class CategoryScore:
    category: str
    score: float | None  # None means no evidence: "Not mentioned: ask about this"
    weight: float
    item_count: int

    @property
    def scored(self) -> bool:
        return self.score is not None

    @property
    def red_flag(self) -> bool:
        return self.scored and self.weight >= FLAG_WEIGHT and self.score < FLAG_SCORE


@dataclass
class ProfileScore:
    profile_id: str
    label: str
    overall: float | None
    band: str
    coverage: float  # share of profile weight backed by evidence (0 to 1)
    categories: dict[str, CategoryScore] = field(default_factory=dict)

    @property
    def red_flags(self) -> list[str]:
        return [c.category for c in self.categories.values() if c.red_flag]


def item_value(item: Evidence, overrides: dict[str, int]) -> int:
    matched = [overrides[t] for t in item.tags if t in overrides]
    if matched:
        return min(matched)
    return SIGNAL_VALUE[item.signal]


LIMITED_COVERAGE = 0.40


def band_for(score: float | None, coverage: float) -> str:
    # Thin evidence should not read as a verdict on the employer.
    if score is None:
        return "Not enough evidence"
    if coverage < LIMITED_COVERAGE:
        return "Limited evidence"
    if score >= 70:
        return "Good fit"
    if score >= 45:
        return "Mixed"
    return "Concern"


def score_profile(evidence: list[Evidence], profile_id: str) -> ProfileScore:
    profile = PROFILES[profile_id]
    weights = profile["weights"]
    overrides = profile["tag_overrides"]

    categories: dict[str, CategoryScore] = {}
    for cat in CATEGORIES:
        items = [e for e in evidence if e.category == cat]
        if items:
            values = [item_value(e, overrides) for e in items]
            score = sum(values) / len(values)
        else:
            score = None
        categories[cat] = CategoryScore(cat, score, weights[cat], len(items))

    scored = [c for c in categories.values() if c.scored]
    coverage = sum(c.weight for c in scored)
    if coverage:
        overall = sum(c.weight * c.score for c in scored) / coverage
    else:
        overall = None

    return ProfileScore(
        profile_id=profile_id,
        label=profile["label"],
        overall=None if overall is None else round(overall, 1),
        band=band_for(overall, coverage),
        coverage=round(coverage, 3),
        categories=categories,
    )


def score_all(evidence: list[Evidence], profile_ids: list[str]) -> dict[str, ProfileScore]:
    return {pid: score_profile(evidence, pid) for pid in profile_ids}
