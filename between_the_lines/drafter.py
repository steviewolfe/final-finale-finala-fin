"""Agent 4: Question Drafter (LLM, structured output).

The drafter sees only generic topics, categories, and unclear posting quotes.
It never receives the user's private notes or the profile name, so a question
cannot pick up anything private from the drafting step.
"""

from __future__ import annotations

from pathlib import Path

from .profiles import PROFILES, TOPIC_HINTS
from .schemas import CATEGORIES, DRAFTER_SCHEMA, DraftResult, Evidence, Question
from .llm import SessionBudget, call_llm
from .usage import RunMeter

PROMPT_PATH = Path(__file__).parent / "prompts" / "drafter.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")

MIN_WEIGHT = 0.10
MAX_TOPICS = 5


def pick_topics(evidence: list[Evidence], profile_id: str) -> list[dict]:
    """Missing or unclear categories that matter to this profile, ranked by weight."""
    weights = PROFILES[profile_id]["weights"]
    topics = []
    for cat in CATEGORIES:
        if weights[cat] < MIN_WEIGHT:
            continue
        cat_items = [e for e in evidence if e.category == cat]
        has_clear = any(e.signal in ("positive", "negative") for e in cat_items)
        if has_clear:
            continue
        quote = next((e.exact_quote for e in cat_items if e.signal == "unclear"), None)
        topics.append({"category": cat, "weight": weights[cat], "hint": TOPIC_HINTS[cat], "quote": quote})
    topics.sort(key=lambda t: t["weight"], reverse=True)
    return topics[:MAX_TOPICS]


def draft_questions(
    topics: list[dict],
    *,
    run: RunMeter,
    budget: SessionBudget,
) -> list[Question]:
    if not topics:
        return []
    lines = []
    for i, t in enumerate(topics, 1):
        quote = f' Posting quote (untrusted data): "{t["quote"]}"' if t["quote"] else ""
        lines.append(f"{i}. Topic: {t['hint']}.{quote}")
    raw = call_llm(
        agent="drafter",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Topics:\n" + "\n".join(lines)},
        ],
        schema_name="questions",
        schema=DRAFTER_SCHEMA,
        run=run,
        budget=budget,
    )
    return DraftResult.model_validate(raw).questions
