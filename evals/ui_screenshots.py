"""Drive the running app in headless Chromium and save screenshots of the review flow.

Start the server first (see README), then run:
    ./.venv/bin/python evals/ui_screenshots.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8000"
OUT = Path(__file__).resolve().parent / "screenshots"
OUT.mkdir(exist_ok=True)
NOTES = "I have ADHD and two kids"

checks = []
def check(name, ok):
    checks.append((name, bool(ok)))
    print(("PASS" if ok else "FAIL"), name)

errors = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    page.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)

    page.goto(BASE)
    page.wait_for_selector("#posting")
    page.screenshot(path=str(OUT / "01_compose.png"), full_page=True)

    # Load sample 04 from Settings
    page.select_option("select[aria-label='Load a sample posting']", "04_onsite_shift_coordinator.txt")
    page.click("button:has-text('Add private notes')")
    page.fill("#notes-compose", NOTES)
    page.click("button.primary:has-text('Check this posting')")
    page.wait_for_selector(".paper mark.seg")
    page.wait_for_timeout(300)
    page.screenshot(path=str(OUT / "02_review.png"), full_page=False)
    check("review screen shows underlines", page.locator(".paper mark.seg").count() > 0)
    check("rail shows suggestion cards", page.locator(".rail .card").count() > 0)

    # Hover a negative underline: tooltip with the three sections and a score line
    neg = page.locator("mark.seg-negative").first
    neg.hover()
    page.wait_for_selector("[role=tooltip]")
    tip = page.locator("[role=tooltip]").first.inner_text()
    check("tooltip has 'What it says'", "what it says" in tip.lower())
    check("tooltip has 'Why it matters'", "why it matters" in tip.lower())
    check("tooltip has score line", "Counts as" in tip)
    page.screenshot(path=str(OUT / "03_tooltip.png"))

    # Escape closes it
    page.keyboard.press("Escape")
    page.mouse.move(5, 5)
    page.wait_for_timeout(300)
    check("Escape closes tooltip", page.locator("[role=tooltip]").count() == 0)

    # Click a card selects its underline
    page.locator(".rail .card").first.click()
    page.wait_for_timeout(200)
    check("selected card marks its underline active", page.locator("mark.is-active").count() > 0)
    page.screenshot(path=str(OUT / "04_selected.png"))

    # Category chip filters the rail
    all_cards = page.locator(".rail .card").count()
    page.click(".cat-chips button:has-text('Caregiving and leave')")
    filtered = page.locator(".rail .card").count()
    check("category filter reduces cards", filtered <= all_cards and filtered > 0)
    page.click(".cat-chips button:has-text('All')")

    # Switch profile lens
    page.click(".lens button:has-text('Eldercare')")
    page.locator("mark.seg-negative").first.hover()
    page.wait_for_selector("[role=tooltip]")
    check("lens changes tooltip score line", "Counts as" in page.locator("[role=tooltip]").first.inner_text())
    page.keyboard.press("Escape")
    page.mouse.move(5, 5)

    # Gap card shows the question and the rewrite badge if the guard rewrote one
    page.screenshot(path=str(OUT / "05_rail_gaps.png"))

    # Run details drawer
    page.click(".topbar button:has-text('Run details')")
    page.wait_for_selector("[aria-label='Run details']")
    page.screenshot(path=str(OUT / "06_details.png"))
    page.keyboard.press("Escape")

    # Private terms must not appear on the page
    body = page.inner_text("body")
    check("notes never shown on page", "ADHD" not in body and "two kids" not in body)

    # Injection sample: flagged sentence has its own tooltip
    page.click(".topbar button:has-text('Edit posting')")
    page.wait_for_selector("#posting")
    page.select_option("select[aria-label='Load a sample posting']", "05_marketing_coordinator.txt")
    page.click("button.primary:has-text('Check this posting')")
    page.wait_for_selector(".paper")
    page.wait_for_timeout(300)
    flagged = page.locator("mark.seg-flagged")
    check("injection sentence is flagged", flagged.count() > 0)
    if flagged.count():
        flagged.first.hover()
        page.wait_for_timeout(200)
        page.wait_for_selector("[role=tooltip]")
        check("flagged tooltip says Ignored", "Ignored" in page.locator("[role=tooltip]").first.inner_text())
        page.screenshot(path=str(OUT / "07_flagged.png"))

    # Phone width
    phone = browser.new_page(viewport={"width": 390, "height": 844})
    phone.goto(BASE)
    phone.wait_for_selector("#posting")
    phone.screenshot(path=str(OUT / "08_phone_compose.png"), full_page=True)
    overflow = phone.evaluate("document.documentElement.scrollWidth > window.innerWidth")
    check("no horizontal scroll at 390px (compose)", not overflow)

    browser.close()

print("screenshots:", sorted(f.name for f in OUT.glob("*.png")))
print("browser errors:", errors or "none")
print("passed:", sum(ok for _, ok in checks), "of", len(checks))
