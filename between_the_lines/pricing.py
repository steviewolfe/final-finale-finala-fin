"""Cost estimates per call, in USD per 1,000,000 tokens.

Input and output prices for gpt-6-luna come from published launch coverage
(AlternativeTo, 2026-09). The cached-input price ($0.01 per million) comes from
several secondary price listings (eesel.ai, devtk.ai, Felo). They could not be
checked against the OpenAI price page directly, so confirm before final submission.
"""

from __future__ import annotations

PRICE_PER_MTOK = {
    "input": 0.10,
    "cached_input": 0.01,   # secondary listings: eesel.ai, devtk.ai
    "output": 0.50,
}
PRICE_SOURCE = "https://alternativeto.net/news/2026/9/openai-introduces-gpt-6-sol-and-luna-with-lower-api-prices/"
CACHED_PRICE_SOURCE = "https://www.eesel.ai/blog/gpt-6-luna-pricing"


def estimate_cost(input_tokens: int, cached_input_tokens: int, output_tokens: int) -> float:
    """Estimate cost for one call. Cached tokens are billed at the cached rate."""
    uncached = max(input_tokens - cached_input_tokens, 0)
    total = (
        uncached * PRICE_PER_MTOK["input"]
        + cached_input_tokens * PRICE_PER_MTOK["cached_input"]
        + output_tokens * PRICE_PER_MTOK["output"]
    )
    return total / 1_000_000
