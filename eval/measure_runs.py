"""Measure real token use and cost for typical runs. Writes eval/measurements.json.

Each sample is checked twice with all four profiles and a private note:
  cold: extraction cache off (every call is made)
  warm: extraction cache on (the second check of the same posting)
Token counts come from the model's own usage fields, via RunMeter.
    ./.venv/bin/python eval/measure_runs.py
"""
import json
import sys
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from between_the_lines.config import REPO_DIR
from between_the_lines.llm import SessionBudget
from between_the_lines.pipeline import run_pipeline
from between_the_lines.pricing import PRICE_SOURCE, PRICE_PER_MTOK
from between_the_lines.profiles import PROFILES

NOTES = "I have ADHD and two kids"
PIDS = list(PROFILES)
budget = SessionBudget(limit=10**9)
samples = sorted((REPO_DIR / "sample_postings").glob("*.txt"))

runs = []
for path in samples:
    text = path.read_text(encoding="utf-8")
    for mode, use_cache in [("cold", False), ("warm", True)]:
        r = run_pipeline(text, PIDS, "parent", NOTES, budget=budget, use_cache=use_cache)
        m = r.meter
        runs.append({
            "sample": path.name,
            "mode": mode,
            "error": r.error,
            "calls": m.calls,
            "input_tokens": m.input_tokens,
            "cached_input_tokens": m.cached_input_tokens,
            "output_tokens": m.output_tokens,
            "total_tokens": m.total_tokens,
            "cost_usd": round(m.cost_usd, 6),
            "by_agent": [
                {"agent": row["agent"], "input": row["input_tokens"],
                 "cached": row["cached_input_tokens"], "output": row["output_tokens"],
                 "cost_usd": round(row["cost_usd_estimate"], 6)}
                for row in m.rows
            ],
            "scores": {pid: r.scores[pid].overall for pid in PIDS},
            "evidence_count": len(r.evidence),
            "rejected": r.quote_check.rejected_count if r.quote_check else 0,
            "questions": len([q for q in (r.guard.questions if r.guard else []) if q.action != "blocked"]),
        })
        print(f"{path.name:36} {mode}: calls={m.calls} in={m.input_tokens} cached={m.cached_input_tokens} "
              f"out={m.output_tokens} cost=${m.cost_usd:.6f}")

cold = [r for r in runs if r["mode"] == "cold"]
warm = [r for r in runs if r["mode"] == "warm"]
summary = {
    "model": "gpt-6-luna",
    "price_per_mtok_usd": PRICE_PER_MTOK,
    "price_source": PRICE_SOURCE,
    "cold_mean": {
        "calls": mean(r["calls"] for r in cold),
        "input_tokens": mean(r["input_tokens"] for r in cold),
        "cached_input_tokens": mean(r["cached_input_tokens"] for r in cold),
        "output_tokens": mean(r["output_tokens"] for r in cold),
        "total_tokens": mean(r["total_tokens"] for r in cold),
        "cost_usd": mean(r["cost_usd"] for r in cold),
    },
    "warm_mean": {
        "calls": mean(r["calls"] for r in warm),
        "input_tokens": mean(r["input_tokens"] for r in warm),
        "cached_input_tokens": mean(r["cached_input_tokens"] for r in warm),
        "output_tokens": mean(r["output_tokens"] for r in warm),
        "total_tokens": mean(r["total_tokens"] for r in warm),
        "cost_usd": mean(r["cost_usd"] for r in warm),
    },
    "errors": [r for r in runs if r["error"]],
}
out = Path(__file__).resolve().parent / "measurements.json"
out.write_text(json.dumps({"runs": runs, "summary": summary}, indent=2), encoding="utf-8")
print("\nsummary:", json.dumps(summary, indent=2)[:900])
print("wrote", out)
