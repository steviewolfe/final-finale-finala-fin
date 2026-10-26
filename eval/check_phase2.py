"""Phase 2 check: extract + quote-check sample postings 01 and 05."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from between_the_lines.config import REPO_DIR
from between_the_lines.extractor import extract_evidence
from between_the_lines.llm import SessionBudget
from between_the_lines.quote_checker import check_quotes
from between_the_lines.security import flagged_sentences
from between_the_lines.usage import RunMeter

budget = SessionBudget(limit=60_000)
for name in ["01_startup_ops_manager.txt", "05_marketing_coordinator.txt"]:
    posting = (REPO_DIR / "sample_postings" / name).read_text(encoding="utf-8")
    run = RunMeter(f"p2-{name[:2]}")
    result, hit = extract_evidence(posting, run=run, budget=budget, use_cache=False)
    qc = check_quotes(result.evidence, posting)
    print(f"\n== {name} | extracted={len(result.evidence)} kept={len(qc.kept)} "
          f"rejected={qc.rejected_count} of {qc.total} | tokens={run.total_tokens} cost=${run.cost_usd:.6f}")
    print("flagged sentences:", flagged_sentences(posting))
    for e in qc.kept:
        print(f"  KEEP [{e.category}] {e.signal}: {e.exact_quote!r}")
    for r in qc.rejected:
        print(f"  REJECT [{r.category}] {r.quote!r} -> {r.reason}")

# Fabricated quote must be rejected
from between_the_lines.schemas import Evidence
fake = [Evidence(category="role_clarity", exact_quote="We offer unlimited nap pods.",
                 signal="positive", tags=[], note="invented")]
print("\nfabricated test:", check_quotes(fake, "Some real posting text.").rejected)
