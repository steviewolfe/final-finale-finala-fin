"""Layout and usability checks for the running app (http://localhost:8000).

These measure where things sit and how big they are, not only whether they exist.
Each check maps to a finding from the audit. Exits non-zero if any check fails.
    ./.venv/bin/python eval/ui_layout_check.py
"""
import sys
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8000"
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def small_controls(pg):
    """Visible buttons, links and fields under 44px in either direction."""
    return pg.evaluate("""() => [...document.querySelectorAll('button, a, select, input, textarea, [role=tab]')]
      .filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && (r.height < 44 || r.width < 44) })
      .map(e => (e.innerText || e.getAttribute('aria-label') || e.id || e.tagName).trim().slice(0, 36))""")


with sync_playwright() as p:
    browser = p.chromium.launch()

    # 1. Paste box and Check button are visible without scrolling on common screens.
    for vw, vh in [(1280, 720), (1440, 900), (390, 844)]:
        pg = browser.new_page(viewport={"width": vw, "height": vh})
        pg.goto(BASE)
        pg.wait_for_selector("#posting")
        ta = pg.locator("#posting").bounding_box()
        btn = pg.locator("button.primary").bounding_box()
        check(f"paste box visible at {vw}x{vh}", ta["y"] >= 0 and ta["y"] + 120 <= vh, f"top {round(ta['y'])}")
        check(f"Check button visible at {vw}x{vh}", btn["y"] + btn["height"] <= vh, f"bottom {round(btn['y'] + btn['height'])}")
        check(f"no sideways scroll at {vw}px", not pg.evaluate("document.documentElement.scrollWidth > innerWidth"))
        pg.close()

    # 2. Targets are at least 44px on compose.
    pg = browser.new_page(viewport={"width": 1440, "height": 900})
    pg.goto(BASE)
    pg.wait_for_selector("#posting")
    small = small_controls(pg)
    check("compose: every control is 44px or more", not small, f"{len(small)} small: {small[:5]}")
    check("compose: no 'Settings' label left", pg.locator("text=Settings").count() == 0)
    check("compose: 'The problem' tab present", pg.locator("[role=tab]:has-text('The problem')").count() == 1)
    pg.click("[role=tab]:has-text('The problem')")
    check("problem tab explains the problem", pg.locator(".problem").count() == 1)
    pg.click("[role=tab]:has-text('Check a posting')")

    # 3. Notes are optional and shown only on request; no duplicate inputs.
    check("notes hidden by default", pg.locator("#notes-compose").count() == 0)
    pg.click("button:has-text('Add private notes')")
    check("notes appear on request", pg.locator("#notes-compose").count() == 1)
    check("notes exist once", pg.locator("input[type=password]").count() == 1)
    pg.click("button:has-text('Hide private notes')")

    # 4. Run a sample and check the review screen.
    pg.select_option("select[aria-label='Load a sample posting']", "04_onsite_shift_coordinator.txt")
    pg.click("button.primary:has-text('Check this posting')")
    pg.wait_for_selector(".summary", timeout=120000)
    small = small_controls(pg)
    check("review: every control is 44px or more", not small, f"{len(small)} small: {small[:5]}")

    # 5. Highlights are real bands sized to each line.
    style = pg.evaluate("""() => { const m = document.querySelector('mark.seg-negative');
        const cs = getComputedStyle(m);
        return { bg: cs.backgroundImage, clone: cs.boxDecorationBreak || cs.webkitBoxDecorationBreak } }""")
    check("highlights use a band gradient", "linear-gradient" in style["bg"], style["bg"][:40])
    check("highlights clone across line breaks", style["clone"] == "clone", style["clone"])

    # 6. Groups are bounded panels.
    border = pg.evaluate("getComputedStyle(document.querySelector('.group')).borderTopWidth")
    check("rail groups are bounded panels", border == "1px", border)

    # 7. Options drawer holds only what belongs there.
    pg.click(".topbar button:has-text('Options')")
    pg.wait_for_selector(".drawer")
    fields = pg.locator(".drawer select, .drawer input, .drawer button").count()
    check("options drawer is short (3 controls or fewer, plus Close)", fields <= 4, f"{fields} controls")
    pg.click(".drawer button:has-text('Close')")

    # 8. Cache message is quiet and not a banner.
    check("no cache banner at the top", pg.locator(".banner:has-text('cache')").count() == 0)

    # 9. Rewritten questions can show their first draft.
    rewritten = pg.locator(".badge-btn")
    if rewritten.count():
        rewritten.first.click()
        check("'changed to protect your notes' shows the first draft", pg.locator(".why-changed").count() == 1)
    pg.close()

    # 10. Phone: the jump link to suggestions is pinned and tappable.
    phone = browser.new_page(viewport={"width": 390, "height": 844})
    phone.goto(BASE)
    phone.wait_for_selector("#posting")
    phone.select_option("select[aria-label='Load a sample posting']", "04_onsite_shift_coordinator.txt")
    phone.click("button.primary:has-text('Check this posting')")
    phone.wait_for_selector(".summary", timeout=120000)
    jump = phone.locator(".jump-rail")
    check("phone: 'See suggestions' is pinned and visible", jump.is_visible())
    check("phone: no sideways scroll on review", not phone.evaluate("document.documentElement.scrollWidth > innerWidth"))
    phone.close()
    browser.close()

passed = sum(ok for _, ok in results)
print(f"\n{passed} of {len(results)} checks pass")
sys.exit(0 if passed == len(results) else 1)
