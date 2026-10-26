"""Token and cost logging for every LLM call.

Each call appends one row to logs/usage.csv. RunMeter keeps the same rows in
memory so the UI can show per-run totals without re-reading the file.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .config import USAGE_LOG

FIELDS = [
    "timestamp",
    "run_id",
    "agent",
    "model",
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "cost_usd_estimate",
]


def log_usage(row: dict) -> None:
    """Append one usage row, writing the header if the file is new."""
    USAGE_LOG.parent.mkdir(parents=True, exist_ok=True)
    is_new = not USAGE_LOG.exists()
    with USAGE_LOG.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in FIELDS})


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class RunMeter:
    """Per-run totals, shown in the UI's Run details tab."""

    run_id: str
    rows: list[dict] = field(default_factory=list)

    def add(self, row: dict) -> None:
        self.rows.append(row)

    @property
    def calls(self) -> int:
        return len(self.rows)

    @property
    def input_tokens(self) -> int:
        return sum(r["input_tokens"] for r in self.rows)

    @property
    def cached_input_tokens(self) -> int:
        return sum(r["cached_input_tokens"] for r in self.rows)

    @property
    def output_tokens(self) -> int:
        return sum(r["output_tokens"] for r in self.rows)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def cost_usd(self) -> float:
        return sum(r["cost_usd_estimate"] for r in self.rows)
