"""Sensitive-term patterns for the privacy guard's keyword layer.

Patterns are case-insensitive regexes on word boundaries, with stems where a
word has many forms. Terms that come from the user's own notes are added at
runtime by privacy_guard.note_terms().
"""

from __future__ import annotations

import re

SENSITIVE_PATTERNS = [
    r"\badhd\b", r"\bautis\w*", r"\bdyslex\w*", r"\bdyspraxi\w*", r"\bneurodiver\w*",
    r"\bnd\b", r"\banxi\w*", r"\bdepress\w*", r"\bbipolar\b", r"\bptsd\b",
    r"\bdiagnos\w*", r"\bmedic\w*", r"\btherap\w*", r"\bchronic\w*", r"\billness\w*",
    r"\bdisab\w*", r"\bimpair\w*", r"\bpain\b", r"\bfatigue\w*", r"\bflare\w*",
    r"\bsurgery\b", r"\bcancer\b", r"\bdiabet\w*", r"\blupus\b", r"\bsclerosis\b",
    r"\bpregnan\w*", r"\bfertility\b", r"\bivf\b", r"\bpostpartum\b", r"\bmiscarr\w*",
    r"\bkids?\b", r"\bchild\w*", r"\bdaughters?\b", r"\bsons?\b", r"\btoddlers?\b",
    r"\bbabies\b", r"\bbaby\b", r"\bdaycare\b", r"\bnann(y|ies)\b", r"\bschool\s+pick\w*",
    r"\bparent(s|ing)?\b", r"\bcaregiv\w*", r"\belderly\b", r"\baging\b", r"\bdementia\b",
    r"\b(my|our)\s+(mother|father|mom|dad|mum|parents?|husband|wife|spouse|partner)\b",
    r"\bage\b", r"\bretire\w*",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in SENSITIVE_PATTERNS]


def lexicon_hits(text: str, extra_terms: set[str] | None = None) -> list[str]:
    """Return the sensitive terms found in text. Empty list means no hit."""
    hits = [m.group(0).lower() for pat in _COMPILED for m in pat.finditer(text)]
    for term in extra_terms or ():
        if re.search(rf"\b{re.escape(term)}\w*", text, re.IGNORECASE):
            hits.append(term)
    return hits


def redact(text: str, extra_terms: set[str] | None = None) -> str:
    """Replace sensitive terms with [redacted] before text is written to a log."""
    out = text
    for pat in _COMPILED:
        out = pat.sub("[redacted]", out)
    for term in sorted(extra_terms or (), key=len, reverse=True):
        out = re.sub(rf"\b{re.escape(term)}\w*", "[redacted]", out, flags=re.IGNORECASE)
    return out
