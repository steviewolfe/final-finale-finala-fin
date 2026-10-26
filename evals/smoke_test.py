"""One real LLM call to confirm the key, model, and routing work.

Run from the project root:  ./.venv/bin/python evals/smoke_test.py
Prints the model name and token counts only. Never prints a key.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from between_the_lines.config import MODEL, get_client  # noqa: E402


def main() -> int:
    client = get_client()
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "Reply with exactly: connection works."}],
            max_completion_tokens=20,
        )
    except Exception as exc:  # show the error class and message, not the key
        print(f"FAIL: {type(exc).__name__}: {exc}")
        return 1

    usage = response.usage
    print(f"SUCCESS: model={response.model}")
    print(f"tokens: input={usage.prompt_tokens} output={usage.completion_tokens}")
    print(f"reply: {response.choices[0].message.content!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
