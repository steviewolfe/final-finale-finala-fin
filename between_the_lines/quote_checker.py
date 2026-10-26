"""Agent 2: Quote Checker (plain Python, no LLM).

Keeps an evidence item only if its quote really appears in the posting. It
also drops quotes that come from injection-flagged sentences and caps the
number of items per category.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .schemas import Evidence
from .security import contains_injection, flagged_sentences

MAX_PER_CATEGORY = 4

_QUOTE_MAP = str.maketrans(
    {
        "‘": "'", "’": "'", "‚": "'", "‛": "'",
        "“": '"', "”": '"', "„": '"', "‟": '"',
        "–": "-", "—": "-", "−": "-",
        " ": " ",
    }
)


def normalize(text: str) -> str:
    """Canonical form for matching: NFKC, straight quotes, single spaces, lowercase."""
    text = unicodedata.normalize("NFKC", text).translate(_QUOTE_MAP)
    return re.sub(r"\s+", " ", text).strip().casefold()


@dataclass
class Rejection:
    category: str
    quote: str
    reason: str


@dataclass
class QuoteCheckResult:
    kept: list[Evidence]
    rejected: list[Rejection]

    @property
    def rejected_count(self) -> int:
        return len(self.rejected)

    @property
    def total(self) -> int:
        return len(self.kept) + len(self.rejected)


def check_quotes(evidence: list[Evidence], posting: str) -> QuoteCheckResult:
    norm_posting = normalize(posting)
    norm_flagged = [normalize(s) for s in flagged_sentences(posting)]

    kept: list[Evidence] = []
    rejected: list[Rejection] = []
    seen: set[tuple[str, str]] = set()
    per_category: dict[str, int] = {}

    for item in evidence:
        norm_quote = normalize(item.exact_quote)

        if not norm_quote:
            reason = "empty quote"
        elif norm_quote not in norm_posting:
            reason = "quote not found in posting"
        elif any(norm_quote in f for f in norm_flagged) or contains_injection(item.exact_quote):
            reason = "quote comes from an injection-flagged sentence"
        elif (item.category, norm_quote) in seen:
            reason = "duplicate quote"
        elif per_category.get(item.category, 0) >= MAX_PER_CATEGORY:
            reason = f"over {MAX_PER_CATEGORY} items for this category"
        else:
            reason = ""

        if reason:
            rejected.append(Rejection(item.category, item.exact_quote, reason))
            continue

        seen.add((item.category, norm_quote))
        per_category[item.category] = per_category.get(item.category, 0) + 1
        kept.append(item)

    return QuoteCheckResult(kept=kept, rejected=rejected)
