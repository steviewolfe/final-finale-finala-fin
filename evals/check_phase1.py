"""Phase 1 check: one structured call gets logged; a tiny budget stops the run."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from between_the_lines.llm import BudgetExceeded, SessionBudget, call_llm
from between_the_lines.schemas import GUARD_SCHEMA
from between_the_lines.usage import RunMeter

msgs = [{"role": "user", "content": "Return results with one item: id 0, verdict safe, fact_type none, rewrite null."}]
run = RunMeter("phase1-check")
out = call_llm(agent="guard", messages=msgs, schema_name="guard", schema=GUARD_SCHEMA,
               run=run, budget=SessionBudget(limit=60_000))
print("structured output:", out)
print("run tokens:", run.total_tokens, "calls:", run.calls, "cost:", round(run.cost_usd, 6))

try:
    call_llm(agent="guard", messages=msgs, schema_name="guard", schema=GUARD_SCHEMA,
             run=RunMeter("phase1-tiny"), budget=SessionBudget(limit=10))
    print("FAIL: tiny budget did not stop the call")
except BudgetExceeded as exc:
    print("budget stop OK:", exc)
