"""Settings, environment loading, and the LLM client factory.

.env is read from the repo folder first, then from the folder one level above
(graders often keep a single .env there). Existing environment variables win.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# backend/between_the_lines/config.py -> project root is three levels up.
PROJECT_DIR = Path(__file__).resolve().parents[2]
PARENT_DIR = PROJECT_DIR.parent
SAMPLE_DIR = PROJECT_DIR / "data" / "sample_postings"

load_dotenv(PROJECT_DIR / ".env", override=False)
load_dotenv(PARENT_DIR / ".env", override=False)

MODEL = "gpt-6-luna"
PORTKEY_BASE_URL = "https://api.portkey.ai/v1"

# Safety limits
MAX_POSTING_CHARS = 12_000
MAX_NOTES_CHARS = 500
MAX_LLM_CALLS_PER_RUN = 6
SESSION_TOKEN_BUDGET = 60_000

# Per-call output caps. These must be generous: the model also spends output
# tokens on internal reasoning, so a 1,500 cap returned empty content in testing.
MAX_OUTPUT_TOKENS = {"extractor": 6000, "drafter": 4000, "guard": 4000}

USAGE_LOG = PROJECT_DIR / "logs" / "usage.csv"
PRIVACY_LOG = PROJECT_DIR / "logs" / "privacy_log.csv"
CACHE_DIR = PROJECT_DIR / "logs" / "cache"


def get_client() -> OpenAI:
    """Return an OpenAI-compatible client.

    PORTKEY_API_KEY routes through Portkey (course key). OPENAI_API_KEY is the
    fallback for a personal key. Key values are never printed or logged.
    """
    portkey_key = os.getenv("PORTKEY_API_KEY")
    if portkey_key:
        return OpenAI(
            api_key="portkey",
            base_url=PORTKEY_BASE_URL,
            default_headers={
                "x-portkey-api-key": portkey_key,
                "x-portkey-provider": "openai",
            },
        )

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        return OpenAI(api_key=openai_key)

    raise RuntimeError(
        "No API key found. Set PORTKEY_API_KEY or OPENAI_API_KEY in .env "
        "(repo folder or the folder above it)."
    )
