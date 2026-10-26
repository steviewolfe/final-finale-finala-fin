"""The single funnel for every LLM call.

Before each call: check the per-run call cap and the session token budget.
After each call: log tokens and cost to logs/usage.csv and to the run meter.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass

import openai

from .config import MAX_LLM_CALLS_PER_RUN, MAX_OUTPUT_TOKENS, MODEL, get_client
from .pricing import estimate_cost
from .usage import RunMeter, log_usage, now_iso

_client = None
RETRYABLE = (openai.APIConnectionError, openai.RateLimitError, openai.InternalServerError)


class BudgetExceeded(Exception):
    """Raised before a call that would break a safety limit. Shown to the user as-is."""


@dataclass
class SessionBudget:
    """Tokens spent across all runs in one browser session."""

    limit: int
    used: int = 0


def _get_client():
    global _client
    if _client is None:
        _client = get_client()
    return _client


def estimate_tokens(messages: list[dict]) -> int:
    """Rough pre-call estimate: about 4 characters per token."""
    return sum(len(m["content"]) for m in messages) // 4


def call_llm(
    *,
    agent: str,
    messages: list[dict],
    schema_name: str,
    schema: dict,
    run: RunMeter,
    budget: SessionBudget,
    max_calls: int = MAX_LLM_CALLS_PER_RUN,
) -> dict:
    """Make one structured-output call and return the parsed JSON object."""
    if run.calls >= max_calls:
        raise BudgetExceeded(
            f"Call limit reached: {max_calls} LLM calls per run. "
            "Partial results are shown below."
        )

    max_out = MAX_OUTPUT_TOKENS[agent]
    worst_case = estimate_tokens(messages) + max_out
    if budget.used + worst_case > budget.limit:
        raise BudgetExceeded(
            f"Budget reached: {budget.used:,} / {budget.limit:,} tokens used. "
            "Reset the session to continue."
        )

    response = None
    for attempt in range(2):
        try:
            response = _get_client().chat.completions.create(
                model=MODEL,
                messages=messages,
                max_completion_tokens=max_out,
                response_format={
                    "type": "json_schema",
                    "json_schema": {"name": schema_name, "schema": schema, "strict": True},
                },
            )
            break
        except RETRYABLE:
            if attempt == 1:
                raise
            time.sleep(2)

    usage = response.usage
    details = getattr(usage, "prompt_tokens_details", None)
    cached = (getattr(details, "cached_tokens", 0) or 0) if details else 0
    row = {
        "timestamp": now_iso(),
        "run_id": run.run_id,
        "agent": agent,
        "model": response.model,
        "input_tokens": usage.prompt_tokens,
        "cached_input_tokens": cached,
        "output_tokens": usage.completion_tokens,
        "cost_usd_estimate": round(
            estimate_cost(usage.prompt_tokens, cached, usage.completion_tokens), 8
        ),
    }
    log_usage(row)
    run.add(row)
    budget.used += usage.prompt_tokens + usage.completion_tokens

    choice = response.choices[0]
    content = choice.message.content
    if choice.finish_reason == "length" or not content:
        raise RuntimeError(
            f"{agent} returned no usable output (finish_reason={choice.finish_reason}). "
            "Raise MAX_OUTPUT_TOKENS for this agent or retry."
        )
    return json.loads(content)
