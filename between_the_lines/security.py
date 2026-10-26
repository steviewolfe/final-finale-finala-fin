"""Posting input checks and prompt-injection scanning.

Posting text is untrusted data. These checks run before any LLM call and
flag sentences that try to talk to the model or steer the score.
"""

from __future__ import annotations

import re

from .config import MAX_POSTING_CHARS

INJECTION_PATTERNS = [
    r"\bignore\s+(all|any|previous|prior|above|the)\b",
    r"\bsystem\s+(note|prompt|message|instruction)s?\b",
    r"\bAI\b\s*[:,]",
    r"\bas an? (AI|assistant|language model)\b",
    r"\brate this (job|role|posting|listing)\b",
    r"\bscore\b.{0,40}\b(100|10/10)\b",
    r"\bdo not (mention|tell|reveal)\b",
    r"\byou must\b",
    r"\bdisregard\b",
]
_INJECTION_RE = re.compile("|".join(f"(?:{p})" for p in INJECTION_PATTERNS), re.IGNORECASE)
_SENTENCE_RE = re.compile(r"[^.!?\n]+[.!?]?")


class PostingTooLong(Exception):
    """Raised before any LLM call when the posting exceeds the size limit."""


def check_length(text: str) -> None:
    if len(text) > MAX_POSTING_CHARS:
        raise PostingTooLong(
            f"Posting is {len(text):,} characters. The limit is {MAX_POSTING_CHARS:,}. "
            "Trim the posting and try again. No AI calls were made."
        )


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_RE.findall(text) if s.strip()]


def flagged_sentences(text: str) -> list[str]:
    """Return sentences that match an injection pattern."""
    return [s for s in split_sentences(text) if _INJECTION_RE.search(s)]


def contains_injection(text: str) -> bool:
    return bool(_INJECTION_RE.search(text))


def wrap_posting(text: str) -> str:
    """Wrap posting text in tags so the model treats it as data.

    A literal closing tag inside the posting is escaped so it cannot end the block early.
    """
    safe = text.replace("</posting>", "&lt;/posting&gt;")
    return f"<posting>\n{safe}\n</posting>"
