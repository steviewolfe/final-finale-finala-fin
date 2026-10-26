"""Agent 5: Privacy Guard (keyword layer + LLM layer).

Every drafted question is checked against the user's private notes. A
question that leaks or hints at a note is rewritten neutrally, or dropped if
no safe rewrite passes. Private notes are kept in memory only. They are sent
to the guard model for review, and they are never written to any log.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

from .config import PRIVACY_LOG
from .llm import SessionBudget, call_llm
from .privacy_lexicon import lexicon_hits, redact
from .schemas import GUARD_SCHEMA, GuardResult, Question
from .usage import RunMeter, now_iso

PROMPT_PATH = Path(__file__).parent / "prompts" / "guard.md"
GUARD_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")

LOG_FIELDS = ["timestamp", "run_id", "question_index", "action", "layer", "fact_type", "question"]

STOPWORDS = {
    "about", "above", "after", "again", "against", "also", "because", "been", "before",
    "being", "between", "could", "does", "doing", "down", "during", "each", "from",
    "further", "have", "having", "here", "into", "just", "more", "most", "only", "other",
    "over", "same", "should", "some", "such", "than", "that", "their", "them", "then",
    "there", "these", "they", "this", "those", "through", "under", "until", "very",
    "what", "when", "where", "which", "while", "will", "with", "would", "your", "work",
    "working", "job", "team", "role",
}


@dataclass
class GuardedQuestion:
    index: int
    original: str
    final: str | None  # None means dropped
    category: str
    ask_who: str
    action: str  # "kept", "rewritten", or "blocked"
    layer: str  # "", "keyword", or "llm"
    fact_type: str = "none"


@dataclass
class GuardOutcome:
    questions: list[GuardedQuestion] = field(default_factory=list)

    @property
    def safe(self) -> list[GuardedQuestion]:
        return [q for q in self.questions if q.final is not None]

    def count(self, action: str) -> int:
        return sum(1 for q in self.questions if q.action == action)


def note_terms(notes: str) -> set[str]:
    """Distinctive words from the user's notes, lowercased. Used only for matching."""
    words = re.findall(r"[A-Za-z][A-Za-z\-]{3,}", notes or "")
    return {w.lower() for w in words if w.lower() not in STOPWORDS}


def _log(run_id: str, q: GuardedQuestion, terms: set[str]) -> None:
    """Append one privacy log row. Sensitive terms are redacted, and notes are never written."""
    PRIVACY_LOG.parent.mkdir(parents=True, exist_ok=True)
    is_new = not PRIVACY_LOG.exists()
    with PRIVACY_LOG.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=LOG_FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow({
            "timestamp": now_iso(),
            "run_id": run_id,
            "question_index": q.index,
            "action": q.action,
            "layer": q.layer,
            "fact_type": q.fact_type,
            "question": redact(q.original, terms),
        })


def _keyword_blocked(text: str, terms: set[str]) -> bool:
    return bool(lexicon_hits(text, extra_terms=terms))


def guard_questions(
    questions: list[Question],
    notes: str,
    *,
    run: RunMeter,
    budget: SessionBudget,
) -> GuardOutcome:
    terms = note_terms(notes)
    items: list[GuardedQuestion] = []

    # Layer 1: keyword check on every question. Always runs, even with no notes.
    keyword_flags = {}
    for i, q in enumerate(questions):
        keyword_flags[i] = _keyword_blocked(q.question, terms)

    # Layer 2: one batched LLM review, only when the user has entered notes.
    verdicts: dict[int, dict] = {}
    if notes.strip() and questions:
        numbered = "\n".join(f"{i}. {q.question}" for i, q in enumerate(questions))
        user = (
            f"<private_notes>\n{notes.strip()}\n</private_notes>\n\n"
            f"QUESTIONS:\n{numbered}"
        )
        raw = call_llm(
            agent="guard",
            messages=[
                {"role": "system", "content": GUARD_PROMPT},
                {"role": "user", "content": user},
            ],
            schema_name="guard",
            schema=GUARD_SCHEMA,
            run=run,
            budget=budget,
        )
        parsed = GuardResult.model_validate(raw)
        verdicts = {v.id: v.model_dump() for v in parsed.results}

    for i, q in enumerate(questions):
        verdict = verdicts.get(i, {"verdict": "safe", "fact_type": "none", "rewrite": None})
        needs_action = keyword_flags[i] or verdict["verdict"] in ("leaks", "infers")
        if not needs_action:
            items.append(GuardedQuestion(i, q.question, q.question, q.category, q.ask_who, "kept", ""))
            continue

        layer = "keyword" if keyword_flags[i] and verdict["verdict"] == "safe" else "llm"
        fact_type = verdict["fact_type"]
        rewrite = (verdict.get("rewrite") or "").strip() or None

        # Re-check any rewrite with the keyword layer. A failing rewrite is dropped.
        if rewrite and not _keyword_blocked(rewrite, terms) and len(rewrite) <= 200:
            items.append(GuardedQuestion(i, q.question, rewrite, q.category, q.ask_who,
                                         "rewritten", layer, fact_type))
        else:
            items.append(GuardedQuestion(i, q.question, None, q.category, q.ask_who,
                                         "blocked", layer, fact_type))

    for item in items:
        if item.action != "kept":
            _log(run.run_id, item, terms)
    return GuardOutcome(questions=items)
