"""Split the posting into highlighted and plain segments.

Each highlighted segment carries the ids of the evidence items it belongs to,
so a suggestion card can point at its underline and back. The API returns
segments as data; the React app renders each one as text, never as markup.
"""

from __future__ import annotations

import re

from .security import contains_injection, split_sentences

_QUOTE_CLASS = {"'": "['‘’]", '"': "[\"“”]", "-": "[-–—]"}
SEVERITY = {"flagged": 4, "negative": 3, "unclear": 2, "positive": 1}


def _quote_pattern(quote: str) -> re.Pattern:
    """Build a whitespace- and case-tolerant pattern for one quote."""
    parts = []
    for ch in quote.split():
        parts.append("".join(_QUOTE_CLASS.get(c, re.escape(c)) for c in ch))
    return re.compile(r"\s+".join(parts), re.IGNORECASE)


def posting_segments(posting: str, quotes: list[tuple[int, str, str]]) -> list[dict]:
    """quotes is a list of (evidence_id, quote_text, signal).

    Returns [{"text", "kind", "ids"}] where kind is plain, positive, unclear,
    negative or flagged. Identical or overlapping spans merge into one segment
    that keeps every id. The segment takes the most severe kind among them.
    """
    raw: list[tuple[int, int, str, list[int]]] = []

    for sent in split_sentences(posting):
        if contains_injection(sent):
            start = posting.find(sent)
            if start >= 0:
                raw.append((start, start + len(sent), "flagged", []))

    for eid, quote, signal in quotes:
        if not quote.strip():
            continue
        for m in _quote_pattern(quote).finditer(posting):
            raw.append((m.start(), m.end(), signal, [eid]))

    # Earlier starts first; longer spans first at the same start.
    raw.sort(key=lambda s: (s[0], -(s[1] - s[0])))

    chosen: list[dict] = []
    for start, end, kind, ids in raw:
        if chosen and start < chosen[-1]["end"]:
            # Overlaps the last merged span: attach ids and keep the more severe kind.
            last = chosen[-1]
            last["ids"].extend(i for i in ids if i not in last["ids"])
            if SEVERITY[kind] > SEVERITY[last["kind"]]:
                last["kind"] = kind
            continue
        chosen.append({"start": start, "end": end, "kind": kind, "ids": list(ids)})

    segments: list[dict] = []
    pos = 0
    for span in chosen:
        if span["start"] > pos:
            segments.append({"text": posting[pos:span["start"]], "kind": "plain", "ids": []})
        segments.append({
            "text": posting[span["start"]:span["end"]],
            "kind": span["kind"],
            "ids": span["ids"],
        })
        pos = span["end"]
    if pos < len(posting):
        segments.append({"text": posting[pos:], "kind": "plain", "ids": []})
    return segments
