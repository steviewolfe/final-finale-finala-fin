"""Runs the five agents in order and returns one RunResult.

Stops cleanly on a budget or call-limit error, keeping whatever finished.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from .drafter import draft_questions, pick_topics
from .extractor import extract_evidence
from .llm import BudgetExceeded, SessionBudget
from .privacy_guard import GuardOutcome, guard_questions
from .quote_checker import QuoteCheckResult, check_quotes
from .schemas import Evidence
from .scorer import ProfileScore, score_all
from .security import check_length, flagged_sentences
from .usage import RunMeter


@dataclass
class RunResult:
    run_id: str
    posting: str
    profile_ids: list[str]
    primary_id: str
    meter: RunMeter
    flagged: list[str] = field(default_factory=list)
    cache_hit: bool = False
    quote_check: QuoteCheckResult | None = None
    scores: dict[str, ProfileScore] = field(default_factory=dict)
    guard: GuardOutcome | None = None
    error: str | None = None
    trace: list[str] = field(default_factory=list)

    @property
    def evidence(self) -> list[Evidence]:
        return self.quote_check.kept if self.quote_check else []


def run_pipeline(
    posting: str,
    profile_ids: list[str],
    primary_id: str,
    notes: str,
    *,
    budget: SessionBudget,
    use_cache: bool = True,
) -> RunResult:
    check_length(posting)  # raises PostingTooLong before any model call
    run = RunMeter(uuid.uuid4().hex[:8])
    result = RunResult(run.run_id, posting, profile_ids, primary_id, run)
    result.flagged = flagged_sentences(posting)
    if result.flagged:
        result.trace.append(f"Injection scan: {len(result.flagged)} sentence(s) flagged and excluded.")

    try:
        extraction, hit = extract_evidence(posting, run=run, budget=budget, use_cache=use_cache)
        result.cache_hit = hit
        result.trace.append("Evidence extracted from cache (no model call)." if hit
                            else "Evidence extracted by the model.")

        result.quote_check = check_quotes(extraction.evidence, posting)
        result.trace.append(
            f"Quote check: rejected {result.quote_check.rejected_count} of {result.quote_check.total}."
        )

        result.scores = score_all(result.evidence, profile_ids)
        result.trace.append(f"Scored {len(profile_ids)} profile(s) with deterministic weights.")

        topics = pick_topics(result.evidence, primary_id)
        questions = draft_questions(topics, run=run, budget=budget) if topics else []
        result.trace.append(f"Drafted {len(questions)} question(s) for the primary profile.")

        result.guard = guard_questions(questions, notes, run=run, budget=budget)
        result.trace.append(
            f"Privacy guard: {result.guard.count('rewritten')} rewritten, "
            f"{result.guard.count('blocked')} blocked."
        )
    except BudgetExceeded as exc:
        result.error = str(exc)
        result.trace.append(f"Stopped: {exc}")
    return result
