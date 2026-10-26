"""Report evidence: (a) score variance across uncached runs, (b) injection demo.

(a) Runs the extractor 5 times on posting 01 with the cache OFF and reports
    how much the profile scores move. The scorer adds no randomness, so any
    spread comes from the extraction step alone.
(b) Compares posting 05 (with the hidden "rate this job 100" line) against
    the same posting with that line removed. Scores should match closely.
"""
import sys
from pathlib import Path
from statistics import mean, pstdev
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from between_the_lines.config import PROJECT_DIR as REPO_DIR
from between_the_lines.llm import SessionBudget
from between_the_lines.pipeline import run_pipeline
from between_the_lines.profiles import PROFILES

PIDS = list(PROFILES)
budget = SessionBudget(limit=10**9)  # evidence script; the session budget is not the point here
sample = REPO_DIR / "data" / "sample_postings"
p01 = (sample / "01_startup_ops_manager.txt").read_text()
p05 = (sample / "05_marketing_coordinator.txt").read_text()
p05_clean = "\n".join(l for l in p05.splitlines() if "AI system note" not in l).strip()

print("== (a) variance over 5 uncached runs, posting 01")
runs = [run_pipeline(p01, PIDS, "parent", "", budget=budget, use_cache=False) for _ in range(5)]
for pid in PIDS:
    vals = [r.scores[pid].overall for r in runs if r.scores.get(pid) and r.scores[pid].overall is not None]
    if vals:
        print(f"  {pid:16} scores={vals} mean={mean(vals):.1f} sd={pstdev(vals):.2f}")
tok = [r.meter.total_tokens for r in runs]
cost = [r.meter.cost_usd for r in runs]
print(f"  tokens per run: {tok}  mean={mean(tok):.0f}")
print(f"  est. cost per run: mean=${mean(cost):.5f}")

print("\n== (b) injection demo, posting 05 with vs without the hidden line")
a = run_pipeline(p05, PIDS, "parent", "", budget=budget, use_cache=False)
b = run_pipeline(p05_clean, PIDS, "parent", "", budget=budget, use_cache=False)
print(f"  flagged sentences (with line): {len(a.flagged)}  (without: {len(b.flagged)})")
print(f"  rejected quotes (with): {a.quote_check.rejected_count}  (without): {b.quote_check.rejected_count}")
for pid in PIDS:
    sa, sb = a.scores[pid].overall, b.scores[pid].overall
    print(f"  {pid:16} with_line={sa}  without={sb}")
print("  any quote with 'rate this job' or 'AI system note' in evidence:",
      any("rate this job" in e.exact_quote.lower() or "ai system" in e.exact_quote.lower() for e in a.evidence))
