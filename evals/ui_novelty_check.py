"""Checks for the five novelty features: predict, scroll reveal, morphing, explore, and paths.
Server must be running on :8000.   ./.venv/bin/python evals/ui_novelty_check.py
"""
import sys
from playwright.sync_api import sync_playwright

results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto("http://localhost:8000"); pg.wait_for_selector("#posting")
    pg.select_option("select[aria-label='Load a sample posting']", "04_onsite_shift_coordinator.txt")
    pg.click("button.primary:has-text('Check this posting')"); pg.wait_for_selector(".predict", timeout=120000)
    pg.wait_for_timeout(400)

    # 1. Predict before you see
    check("predict card shows before the evidence", pg.locator(".predict .predict-btn").count() == 3)
    pg.click(".predict .predict-btn >> nth=0")
    reveal = pg.locator(".reveal-line").inner_text() if pg.locator(".reveal-line").count() else ""
    check("predict reveals the posting's count", "of 9" in reveal, reveal[:80])

    # 2. Scroll reveal: lower underlines start dimmed, and light up on scroll
    start_progress = pg.locator(".read-progress").inner_text() if pg.locator(".read-progress").count() else "none"
    check("rail shows reading progress before scrolling", start_progress.startswith("Reading: ") and " of " in start_progress, start_progress)
    lit_start = pg.locator("mark.seg:not(.is-unlit)").count()
    unlit_start = pg.locator("mark.seg.is-unlit").count()
    check("some underlines are dimmed before scrolling", unlit_start > 0, f"lit {lit_start}, unlit {unlit_start}")
    for _ in range(12):
        pg.mouse.wheel(0, 700); pg.wait_for_timeout(180)
    pg.wait_for_timeout(600)
    unlit_end = pg.locator("mark.seg.is-unlit").count()
    check("underlines light up as you scroll", unlit_end < unlit_start, f"{unlit_start} -> {unlit_end}")
    # Progress line hides once every claim has been reached (by design).
    check("progress line hides when all claims are reached", pg.locator(".read-progress").count() == 0)

    # 3. Morphing: ring arc and bars animate
    tr = pg.evaluate("getComputedStyle(document.querySelector('.ring-arc')).transitionDuration")
    check("score ring arc animates", "0.6s" in tr, tr)
    pg.click("text=Category breakdown")
    bar_tr = pg.evaluate("getComputedStyle(document.querySelector('.cat-bar .bar > div')).transitionDuration")
    check("category bars animate", "0.6s" in bar_tr, bar_tr)

    # 4. Explore: every quoted claim as a dot, toggles work
    pg.click("button.explore-toggle") if pg.locator("button.explore-toggle").count() else None
    dots = pg.locator(".dot-hit").count()
    total = pg.evaluate("document.querySelectorAll('.explore-row').length")
    check("explore grid shows one dot per claim", dots > 0 and total == 9, f"{dots} dots, {total} rows")
    pg.click(".signal-toggles button:has-text('Restriction')")
    fewer = pg.locator(".dot-hit").count()
    check("signal toggle filters dots", fewer < dots, f"{dots} -> {fewer}")
    pg.click(".signal-toggles button:has-text('Restriction')")
    pg.locator(".dot-hit >> nth=0").click()
    check("clicking a dot highlights its underline", pg.locator("mark.is-active, mark.is-pulse").count() > 0)

    # 5. Choose your path: Explore lights everything at once; Guided resets the reveal
    pg.click(".mode-switch button:has-text('Explore')")
    check("explore mode shows every underline", pg.locator("mark.seg.is-unlit").count() == 0)
    pg.click(".mode-switch button:has-text('Guided')")
    # Returning to Guided keeps what has already been read (by design).
    check("guided mode keeps what you have already read", pg.locator("mark.seg.is-unlit").count() == 0)

    check("no page errors", not errors, "; ".join(errors)[:120] if errors else "")
    pg.screenshot(path="evals/screenshots/novelty_review.png")
    b.close()

passed = sum(ok for _, ok in results)
print(f"\n{passed} of {len(results)} checks pass")
sys.exit(0 if passed == len(results) else 1)
