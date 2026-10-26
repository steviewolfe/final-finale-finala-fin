"""Per-agent screenshots from real runs in the app. Server must be running on :8000.

Traced run: sample 04 with the private note, all four profiles, primary 'parent'.
  extractor      -> underlined quotes in the document
  quote checker  -> Run details trace: 'Quote check: rejected N of M'
  scorer         -> rail score and category breakdown
  drafter        -> 'Ask about' cards
  privacy guard  -> Run details trace: 'Privacy guard: N rewritten, M blocked'
Input checks: sample 05 (contains a hidden instruction), Run details trace line.
    ./.venv/bin/python evals/agent_screenshots.py
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "screenshots"
CACHE = ROOT / "logs" / "cache"
NOTES = "I have ADHD and two kids"

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    pg.goto("http://localhost:8000"); pg.wait_for_selector("#posting")

    # --- Traced run: sample 04 with a private note. Clear the cache first so every agent runs.
    for f in CACHE.glob("extract_*.json"):
        f.unlink()
    pg.select_option("select[aria-label='Load a sample posting']", "04_onsite_shift_coordinator.txt")
    pg.click("button:has-text('Add private notes')")
    pg.fill("#notes-compose", NOTES)
    with pg.expect_response(lambda r: r.url.endswith("/api/analyze") and r.request.method == "POST", timeout=180000) as info:
        pg.click("button.primary:has-text('Check this posting')")
    traced = info.value.json()
    pg.wait_for_selector(".summary", timeout=120000)
    assert not traced["cache_hit"], "traced run must be a cold run"
    (ROOT / "evals" / "traced_run.json").write_text(json.dumps({
        "sample": "04_onsite_shift_coordinator.txt",
        "private_note_used": True,
        "trace": traced["trace"],
        "cache_hit": traced["cache_hit"],
        "evidence_count": len(traced["evidence"]),
        "rejected": len(traced["rejected"]),
        "questions_kept": len([q for q in traced["questions"] if q["action"] != "blocked"]),
        "scores": {s["profile_id"]: s["overall"] for s in traced["scores"]},
        "by_agent": traced["usage"]["rows"],
        "calls": traced["usage"]["calls"],
        "total_tokens": traced["usage"]["input_tokens"] + traced["usage"]["output_tokens"],
        "cost_usd": traced["usage"]["cost_usd"],
    }, indent=2), encoding="utf-8")
    pg.wait_for_timeout(500)

    # Extractor: first underlined quotes in the document
    pg.locator("mark.seg").first.scroll_into_view_if_needed()
    pg.wait_for_timeout(300)
    doc = pg.locator(".paper").bounding_box()
    pg.screenshot(path=str(OUT / "agent_1_extractor.png"),
                  clip={"x": doc["x"], "y": 0, "width": doc["width"], "height": 900})

    # Quote checker and privacy guard: Run details trace
    pg.click(".topbar button:has-text('Run details')")
    pg.wait_for_selector(".drawer")
    pg.wait_for_timeout(300)
    pg.locator(".drawer").screenshot(path=str(OUT / "agent_3_quote_checker_and_guard_trace.png"))
    pg.click(".drawer button:has-text('Close')")

    # Scorer: rail score and category breakdown
    pg.locator("summary:has-text('Category breakdown')").click()
    pg.wait_for_timeout(700)
    pg.locator(".rail").screenshot(path=str(OUT / "agent_4_scorer.png"))

    # Drafter: the Ask about cards
    pg.locator(".group[aria-label='Ask about']").screenshot(path=str(OUT / "agent_5_drafter.png"))

    # --- Input checks: sample 05 with the hidden instruction
    pg.click(".topbar button:has-text('Edit posting')")
    pg.wait_for_selector("#posting")
    pg.select_option("select[aria-label='Load a sample posting']", "05_marketing_coordinator.txt")
    pg.click("button.primary:has-text('Check this posting')")
    pg.wait_for_selector(".summary", timeout=120000)
    pg.click(".topbar button:has-text('Run details')")
    pg.wait_for_selector(".drawer")
    pg.wait_for_timeout(300)
    pg.locator(".drawer").screenshot(path=str(OUT / "agent_0_input_checks.png"))
    b.close()

print("wrote:", sorted(f.name for f in OUT.glob("agent_*.png")))
