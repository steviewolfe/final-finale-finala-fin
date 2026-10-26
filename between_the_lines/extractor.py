"""Agent 1: Evidence Extractor (LLM, structured output).

Results are cached by a hash of the posting and prompt version, so the same
posting is not billed twice and scores stay identical across repeat runs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .config import CACHE_DIR
from .llm import SessionBudget, call_llm
from .schemas import EXTRACTOR_SCHEMA, ExtractionResult
from .security import wrap_posting
from .usage import RunMeter

PROMPT_PATH = Path(__file__).parent / "prompts" / "extractor.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")
PROMPT_VERSION = hashlib.sha256(SYSTEM_PROMPT.encode("utf-8")).hexdigest()[:12]


def _cache_path(posting: str) -> Path:
    key = hashlib.sha256(f"{PROMPT_VERSION}\n{posting}".encode("utf-8")).hexdigest()
    return CACHE_DIR / f"extract_{key}.json"


def extract_evidence(
    posting: str,
    *,
    run: RunMeter,
    budget: SessionBudget,
    use_cache: bool = True,
) -> tuple[ExtractionResult, bool]:
    """Return (validated evidence, cache_hit)."""
    path = _cache_path(posting)
    if use_cache and path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return ExtractionResult.model_validate(data), True

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": wrap_posting(posting)},
    ]
    raw = call_llm(
        agent="extractor",
        messages=messages,
        schema_name="evidence",
        schema=EXTRACTOR_SCHEMA,
        run=run,
        budget=budget,
    )
    result = ExtractionResult.model_validate(raw)

    if use_cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return result, False
