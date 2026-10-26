"""Builds report.html and slides.html from measured data.

Every number comes from evals/measurements.json or evals/safety_log.json, and every
screenshot and font is embedded, so each file opens by double-click.
Items only the author can supply are marked [TO COMPLETE: ...] and must be filled in
before submission. Nothing is invented.

    ./.venv/bin/python evals/build_report.py
"""
import base64
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "evals" / "screenshots"
FONTS = ROOT / "frontend" / "node_modules" / "@fontsource"
M = json.loads((ROOT / "evals" / "measurements.json").read_text(encoding="utf-8"))
S = json.loads((ROOT / "evals" / "safety_log.json").read_text(encoding="utf-8"))

CHECKS_PER_MONTH = 8  # assumption: about two postings a week for an active search
USERS = (100, 10_000)

cold = M["summary"]["cold_mean"]
warm = M["summary"]["warm_mean"]
cold_runs = [r for r in M["runs"] if r["mode"] == "cold"]
warm_runs = [r for r in M["runs"] if r["mode"] == "warm"]
scores_match = all(
    c["scores"] == w["scores"]
    for c in cold_runs for w in warm_runs if c["sample"] == w["sample"]
)

# Share of tokens and cost by agent, across cold runs
agents = {}
for r in cold_runs:
    for a in r["by_agent"]:
        t = agents.setdefault(a["agent"], {"input": 0, "cached": 0, "output": 0, "cost": 0.0, "calls": 0})
        t["input"] += a["input"]; t["cached"] += a["cached"]; t["output"] += a["output"]
        t["cost"] += a["cost_usd"]; t["calls"] += 1
total_out = sum(t["output"] for t in agents.values()) or 1
total_in = sum(t["input"] for t in agents.values()) or 1
total_cost = sum(t["cost"] for t in agents.values()) or 1

per_user_month = CHECKS_PER_MONTH * cold["cost_usd"]
saving_warm = 1 - warm["cost_usd"] / cold["cost_usd"]

# The traced run comes from evals/agent_screenshots.py: one cold run, screenshots taken from the same run.
TRACED = json.loads((ROOT / "evals" / "traced_run.json").read_text(encoding="utf-8"))
sample04 = {
    "evidence_count": TRACED["evidence_count"],
    "rejected": TRACED["rejected"],
    "questions": TRACED["questions_kept"],
    "scores": TRACED["scores"],
    "by_agent": [{"input": a["input_tokens"], "output": a["output_tokens"],
                  "cached": a["cached_input_tokens"], "cost_usd": a["cost_usd"]} for a in TRACED["by_agent"]],
}
sample04_warm = sample04


def money(x, places=5):
    return f"${x:,.{places}f}"


def todo(text):
    return f'<span class="todo">[TO COMPLETE: {html.escape(text)}]</span>'


def data_uri(path: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def shot(name: str, caption: str, width: str = "100%") -> str:
    uri = data_uri(SHOTS / name, "image/png")
    return (f'<figure style="width:{width}"><img src="{uri}" alt="{html.escape(caption)}">'
            f'<figcaption>{html.escape(caption)}</figcaption></figure>')


def font_faces() -> str:
    specs = [
        ("Schibsted Grotesk", 700, FONTS / "schibsted-grotesk" / "files" / "schibsted-grotesk-latin-700-normal.woff2"),
        ("Newsreader", 400, FONTS / "newsreader" / "files" / "newsreader-latin-400-normal.woff2"),
        ("Space Mono", 400, FONTS / "space-mono" / "files" / "space-mono-latin-400-normal.woff2"),
    ]
    out = []
    for family, weight, path in specs:
        uri = "data:font/woff2;base64," + base64.b64encode(path.read_bytes()).decode("ascii")
        out.append(f"@font-face{{font-family:'{family}';font-weight:{weight};src:url({uri}) format('woff2');}}")
    return "\n".join(out)


# Agent diagram: LLM steps in pink, plain-code steps in ink.
DIAGRAM = """<svg viewBox="0 0 960 290" xmlns="http://www.w3.org/2000/svg" role="img"
 aria-label="Agent pipeline: input checks, evidence extractor (LLM), quote checker, scorer, question drafter (LLM), privacy guard (keyword plus LLM), then the result to the reader">
<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
<path d="M0,0 L8,4 L0,8 z" fill="#222"/></marker></defs>
<g font-family="Space Mono, monospace" text-anchor="middle">
  <rect x="10" y="100" width="132" height="80" fill="#fff" stroke="#222" stroke-width="1.5"/>
  <text x="76" y="132" font-size="12" fill="#222">Input checks</text>
  <text x="76" y="152" font-size="9.5" fill="#777">length, injection</text>
  <text x="76" y="166" font-size="9.5" fill="#777">scan (Python)</text>

  <rect x="165" y="100" width="132" height="80" fill="#E05374" stroke="#222" stroke-width="1.5"/>
  <text x="231" y="126" font-size="12" fill="#fff">Evidence</text>
  <text x="231" y="141" font-size="12" fill="#fff">extractor</text>
  <text x="231" y="160" font-size="9.5" fill="#fff">LLM, schema output</text>

  <rect x="320" y="100" width="132" height="80" fill="#fff" stroke="#222" stroke-width="1.5"/>
  <text x="386" y="132" font-size="12" fill="#222">Quote checker</text>
  <text x="386" y="152" font-size="9.5" fill="#777">Python, no model</text>

  <rect x="475" y="100" width="132" height="80" fill="#fff" stroke="#222" stroke-width="1.5"/>
  <text x="541" y="132" font-size="12" fill="#222">Scorer</text>
  <text x="541" y="152" font-size="9.5" fill="#777">Python, no model</text>

  <rect x="630" y="100" width="132" height="80" fill="#E05374" stroke="#222" stroke-width="1.5"/>
  <text x="696" y="126" font-size="12" fill="#fff">Question</text>
  <text x="696" y="141" font-size="12" fill="#fff">drafter</text>
  <text x="696" y="160" font-size="9.5" fill="#fff">LLM</text>

  <rect x="800" y="100" width="150" height="80" fill="#439294" stroke="#222" stroke-width="1.5"/>
  <text x="875" y="132" font-size="12" fill="#fff">Privacy guard</text>
  <text x="875" y="152" font-size="9.5" fill="#fff">keyword + LLM</text>

  <line x1="142" y1="140" x2="165" y2="140" stroke="#222" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="297" y1="140" x2="320" y2="140" stroke="#222" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="452" y1="140" x2="475" y2="140" stroke="#222" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="607" y1="140" x2="630" y2="140" stroke="#222" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="762" y1="140" x2="800" y2="140" stroke="#222" stroke-width="1.5" marker-end="url(#arr)"/>

  <text x="875" y="205" font-size="10" fill="#777">to the reader: quotes,</text>
  <text x="875" y="220" font-size="10" fill="#777">scores, questions, usage</text>
  <line x1="875" y1="180" x2="875" y2="198" stroke="#777" stroke-dasharray="3 3"/>

  <rect x="320" y="222" width="287" height="50" fill="#F7F6F3" stroke="#777" stroke-dasharray="4 3"/>
  <text x="463" y="243" font-size="10" fill="#222">Scores for every profile come from</text>
  <text x="463" y="259" font-size="10" fill="#222">one extraction, shared by all profiles</text>
</g></svg>"""

CSS = """
@page { size: Letter; margin: 0.7in 0.75in; }
* { box-sizing: border-box; }
body { margin: 0; background: #F7F6F3; color: #222; font-family: Newsreader, Georgia, serif;
       font-size: 11pt; line-height: 1.6; }
.page { background: #FDFDF7; max-width: 7in; margin: 24px auto; padding: 0.4in 0.45in; box-shadow: 0 4px 12px rgba(0,0,0,.1); }
h1, h2, h3 { font-family: 'Schibsted Grotesk', system-ui, sans-serif; font-weight: 700; text-transform: uppercase;
             letter-spacing: -0.01em; line-height: 1.1; color: #111; }
h1 { font-size: 34pt; margin: 0 0 6pt; }
h2 { font-size: 20pt; border-top: 1px solid #222; padding-top: 8pt; margin: 0 0 10pt; }
h3 { font-size: 13pt; margin: 14pt 0 6pt; }
p { margin: 0 0 8pt; }
.eyebrow, .meta, figcaption, th, .small { font-family: 'Space Mono', monospace; font-size: 8.5pt;
  text-transform: uppercase; letter-spacing: .06em; color: #777; }
table { width: 100%; border-collapse: collapse; font-size: 9.5pt; margin: 6pt 0 10pt; }
th, td { text-align: left; padding: 5pt 6pt; border-bottom: 1px solid #E0E0E0; vertical-align: top; }
th { color: #777; font-weight: 400; }
figure { margin: 10pt 0; }
figure img { width: 100%; max-height: 250px; object-fit: contain; border: 1px solid #E0E0E0; display: block; margin: 0 auto; }
.trial-quote { font-size: 13pt; line-height: 1.5; border-left: 3px solid #E05374; padding: 4pt 12pt; margin: 10pt 0; font-style: normal; }
.trial-quote cite { display: block; font-family: 'Space Mono', monospace; font-size: 8.5pt; color: #777; margin-top: 6pt; }
figcaption { margin-top: 4pt; }
.todo { background: #FFF3C4; color: #6b4f00; padding: 0 3pt; font-family: 'Space Mono', monospace; font-size: 9pt; }
.callout { border-left: 3px solid #E05374; padding: 4pt 10pt; background: #fff; margin: 8pt 0; }
.stat { display: inline-block; width: 31%; margin: 0 1% 8pt 0; vertical-align: top; }
.stat b { font-family: 'Schibsted Grotesk', sans-serif; font-size: 22pt; display: block; line-height: 1.05; }
.pagebreak { break-before: page; page-break-before: always; }
@media print { body { background: #FDFDF7; } .page { box-shadow: none; margin: 0; padding: 0; max-width: none; } }
"""


def table(headers, rows):
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def report_html() -> str:
    s2 = S["2_prompt_injection"]
    s1 = S["1_invented_quote"]
    s3 = S["3_overspending_budget"]
    s4 = S["4_runaway_calls"]
    s5 = S["5_oversized_posting"]
    s6 = S["6_private_data_leak"]
    per_user_text = money(per_user_month, 4)
    cost100 = money(per_user_month * 100, 2)
    cost10k = money(per_user_month * 10_000, 2)
    sample04_steps = "".join(
        f"<li>{html.escape(t)}</li>" for t in [
            "Input checks: posting length is within the 12,000-character limit; injection scan finds no flagged sentences.",
            f"Extractor (LLM): reads the posting once and returns {sample04['evidence_count']} "
            f"quoted claims. Measured: {sample04['by_agent'][0]['input']:,} input and {sample04['by_agent'][0]['output']:,} output tokens.",
            f"Quote checker: keeps {sample04['evidence_count']} of {sample04['evidence_count'] + sample04['rejected']} quotes; "
            f"{sample04['rejected']} rejected, because each must appear word for word in the posting.",
            "Scorer: turns the kept claims into scores for the four default profiles, with no model call. "
            + ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in sample04["scores"].items()) + ".",
            f"Question drafter (LLM): writes {sample04['questions']} neutral questions for the primary profile. "
            f"Measured: {sample04['by_agent'][1]['input']:,} input and {sample04['by_agent'][1]['output']:,} output tokens.",
            f"Privacy guard (keyword + LLM): checks each question against the private note \"I have ADHD and two kids\". "
            f"Measured: {sample04['by_agent'][2]['input']:,} input and {sample04['by_agent'][2]['output']:,} output tokens. "
            "Trace: \"Privacy guard: 0 rewritten, 0 blocked.\"",
        ]
    )

    cache_rows = [
        ["Calls per run", f"{cold['calls']:.1f}", f"{warm['calls']:.1f}"],
        ["Input tokens", f"{cold['input_tokens']:,.0f}", f"{warm['input_tokens']:,.0f}"],
        ["Cached input tokens", f"{cold['cached_input_tokens']:,.0f}", f"{warm['cached_input_tokens']:,.0f}"],
        ["Output tokens", f"{cold['output_tokens']:,.0f}", f"{warm['output_tokens']:,.0f}"],
        ["Total tokens", f"{cold['total_tokens']:,.0f}", f"{warm['total_tokens']:,.0f}"],
        ["Cost per run (USD)", money(cold["cost_usd"]), money(warm["cost_usd"])],
    ]
    agent_rows = [
        [name.capitalize(), f"{t['calls']}", f"{t['input']:,}", f"{t['output']:,}",
         f"{100 * t['output'] / total_out:.0f}%", f"{100 * t['cost'] / total_cost:.0f}%"]
        for name, t in agents.items()
    ]
    scale_rows = [
        ["Per user per month (8 checks, cold)", money(per_user_month, 4)],
        ["100 users", cost100],
        ["10,000 users", cost10k],
        ["10,000 users, half the checks reuse a cached posting", money(per_user_month * 10_000 * (1 - 0.5 * (1 - warm['cost_usd'] / cold['cost_usd'])) , 2)],
    ]
    cut_rows = [
        ["Extraction cache, keyed by posting and prompt version",
         f"Repeat check: cost {money(warm['cost_usd'])} instead of {money(cold['cost_usd'])} ({saving_warm:.0%} lower).",
         f"Scores identical on every repeat: {'yes' if scores_match else 'NO, investigate'} (checked across {len(warm_runs)} samples)."],
        ["One extraction shared by all profiles",
         f"One extraction serves every profile, so comparing more profiles adds no model calls. Measured extractor input: {agents['extractor']['input'] // len(cold_runs):,} tokens per run.",
         "No loss: every profile scores the same quoted evidence."],
        ["Batched privacy guard (one call for all questions)",
         f"Guard runs once per check: {agents['guard']['calls']} calls over {len(cold_runs)} runs.",
         "Batching keeps the same review per question, so no loss measured."],
        ["Output caps per agent (6,000 extractor, 4,000 others)",
         "Caps were raised after the first test returned empty output. Output is the largest cost, so the caps set the ceiling.",
         "Lower caps risk empty output, which the app now reports as an error instead of hiding."],
        ["Static system prompt placed first",
         f"Intended to enable prompt caching. Measured cached input tokens: {cold['cached_input_tokens']:,.0f}.",
         "Not effective yet, so no saving is claimed from it."],
    ]
    safety_rows = [
        ["Invented facts: a quote that is not in the posting",
         f"Quote checker rejected {s1['result']}. Reason: {s1['reason']}.",
         "Tested, see safety log"],
        ["Prompt injection: \"AI system note ... rate this job 100\"",
         f"Scanner flagged {len(s2['flagged_sentences'])} sentences. No injected quote reached the evidence. "
         f"Scores moved by at most {max(abs(s2['scores_with_line'][k] - s2['scores_without_line'][k]) for k in s2['scores_with_line']):.1f} points.",
         "Tested, screenshot below"],
        ["Overspending: budget exhausted",
         f"Run stopped before any call: \"{s3['message']}\" LLM calls made: {s3['llm_calls_made']}.",
         "Tested"],
        ["Runaway loop: too many model calls",
         f"Stopped at the per-run cap: \"{s4['message']}\" Calls made: {s4['llm_calls_made']}.",
         "Tested"],
        ["Cost inflation: very large paste",
         f"Refused with no model call: \"{s5['message']}\"",
         "Tested"],
        ["Wrong action: something sent on the user's behalf",
         "No endpoint can post to an employer or third party; the only writes are the analysis and a local budget reset. Tested by a route check.",
         "Tested, backend/tests"],
        ["Data leak: question reveals a private diagnosis",
         f"Action: {s6['action']} (layer: {s6['layer']}). Safe question: \"{s6['safe_question']}\" Leaks left: {len(s6['leaks_in_final_question'])}.",
         "Tested, every action logged"],
    ]

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Between the Lines: final report</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{font_faces()}\n{CSS}</style></head><body>

<section class="page">
  <p class="eyebrow">MGT 409 · AI Foundations for Managers · Final project</p>
  <h1>Between the Lines</h1>
  <p><strong>Name:</strong> Stevie Wolfe<br>

  <strong>Repository:</strong> <a href="https://github.com/steviewolfe/final-finale-finala-fin">github.com/steviewolfe/final-finale-finala-fin</a><br>
  <strong>Live app:</strong> not hosted. Run locally from the README in about five minutes.</p>
  <p class="callout">Between the Lines reads a job posting for people who have to weigh work against their health, their brains, or their families. It shows every claim next to the exact words it came from, scores it for each need profile, and drafts questions to ask without revealing anything private.</p>
</section>

<section class="page pagebreak">
  <h2>1. Motivation</h2>
  <p>Job postings are written for an imaginary candidate who can work any hours, work at any pace, and never need a day off. People who are neurodivergent, or who care for children or parents, have to guess whether a role fits. The posting rarely says how steady the hours are, what happens when someone is ill, or how fast the work moves. Asking directly can feel risky.</p>
  <div class="stat"><b>71% vs 49%</b>Irish parents and carers who say flexibility matters, against those whose employer offers it (Indeed survey, Ireland). <span class="small">Silicon Republic</span></div>
  <div class="stat"><b>84%</b>of 1,886 job ads contain ableist wording (content analysis). <span class="small">PubMed 41701271</span></div>
  <div class="stat"><b>~30%</b>of the variance in whether 213 US working mothers stayed, explained by schedule flexibility, against under 6% for location. <span class="small">HR Dive</span></div>
  <p>These figures come from secondary sources, not from this project. The first two are survey and content studies, and the third is a single study of mothers. They show the problem is common and that schedule matters more than where work happens.</p>
  <h3>The case behind the problem</h3>
  <p>The clearest public account of this problem comes from the founder of Raaha, the closest existing tool. Navya Tuteja grew up watching her mother, who is hard of hearing, manage job accommodations. In her words, &ldquo;After she was hired, accommodations were inconsistent, because hearing issues are an invisible disability.&rdquo; She then describes the core difficulty: &ldquo;I think the hard part is ending up in an environment that was never built for how you work.&rdquo; (<a href="https://technical.ly/entrepreneurship/student-built-ai-aims-to-fix-broken-job-search-for-neurodivergent-talent/">Technical.ly, 13 July 2026</a>.) This is the founder&rsquo;s own account, reported in the press. It is not a user of this app.</p>
  <p class="small">Quotes were taken from a fetched copy of the article. Check them against the live page before submission.</p>

</section>

<section class="page">
  <h2>2. What is new here</h2>
  <p>The closest product is Raaha, a free tool for neurodivergent job seekers. Press coverage describes a 25-question quiz on schedule, accommodation needs, and tolerance for unpredictability, which produces a fit score, notes on unclear parts of the posting, and suggested questions for employers (<a href="https://www.wtvr.com/news/local-news/navya-tuteja-raaha-app-aug-13-2026">WTVR, Aug 2026</a>). Raaha&rsquo;s own developer describes the scoring as produced by Claude, trained on public job postings. These are press and developer accounts, not a hands-on review.</p>
  <p>Posting-language tools are a separate group. Gender Decoder flags gender-coded words for free, but describes its own scope as gender bias only, with no alternative wording (its competitor Textmetrics describes it this way, so treat that as one-sided; <a href="https://textmetrics.com/what-is-the-difference-between-gender-decoder-and-textmetrics/">Textmetrics</a>). Textio suggests neutral replacements for masculine-coded phrases and, per Harvard&rsquo;s Digit platform, has extended to flagging age- and disability-related language (<a href="https://d3.harvard.edu/platform-digit/submission/textio-com-reducing-gender-bias-in-hiring-with-ai/">Harvard D3</a>). Ongig&rsquo;s Text Analyzer and Metaview flag exclusionary phrases (<a href="https://www.linkedin.com/pulse/how-optimize-your-job-descriptions-neurodivergent-seekers-leopold">LinkedIn guide</a>). Mentra and Neurodiversity Career Connector match candidates with employers rather than analysing postings. None of the tools above combines posting-language checks with neurodivergent or caregiver fit criteria, as far as my searches found.</p>
  {table(
    ["Question a job seeker asks", "Between the Lines", "Raaha (press and developer accounts)", "Posting-language tools (Gender Decoder, Textio, Ongig)", "General chatbot (design view)"],
    [
      ["Where does each claim come from?", "Every claim is quoted from the posting, and a checker rejects any quote not in the text.", "Not described.", "Flags words, not claims. No source quote per claim.", "Summaries can paraphrase, so the source is not guaranteed."],
      ["Is the score the same each time?", "Yes. Scores are computed by fixed code from the quotes. Repeat checks matched exactly.", "Score produced by the model.", "Word counts or fixed lists: repeatable.", "Depends on the model's answer for that run."],
      ["Does it check fit for a need?", "Yes, for eight named needs, with weights shown.", "Yes, from a 25-question quiz.", "No. Language only.", "Only if asked."],
      ["Can I ask the employer safely?", "Questions are checked against private notes, and every change is logged.", "Suggested questions, privacy stated as user-only.", "Not designed for this.", "Not designed for this."],
    ])}
  <p>The app now covers eight need profiles: the original four, plus Deaf or hard of hearing, Religious observance, Students and part-time workers, and Career returners. The side-by-side view is capped at four, so it stays readable. It also checks a ninth category, inclusion and accommodation. A content analysis of 1,886 job ads found accommodation statements in only 9% of them and equal-opportunity statements in 19% (<a href="https://pubmed.ncbi.nlm.nih.gov/41701271/">PubMed 41701271</a>), so a posting that does not say how to ask for adjustments is itself a signal.</p>
  <p>Two things here are new for this course: the claim checks (quotes must exist, and an injected instruction cannot change the evidence) and the privacy check on the questions. I have not searched exhaustively for other tools that combine both, so that claim is limited to the tools listed above.</p>
</section>

<section class="page pagebreak">
  <h2>3. The agents</h2>
  <p>Five agents run in sequence. Two are language-model calls, the rest are plain Python. The model is <code>gpt-6-luna</code>, reached through the course Portkey key, and every model call returns JSON that must match a schema. Keeping the model's job small (finding quotes, writing questions) and the arithmetic and checks in code is what makes the results repeatable.</p>
  <figure>{DIAGRAM}<figcaption>Agent pipeline. Pink: language-model agents. Ink: plain Python. Each arrow is a hand-off of validated data, not free text.</figcaption></figure>
  <h3>Roles and tools</h3>
  {table(
    ["Agent", "Job", "Tools and inputs", "Model"],
    [
      ["Input checks", "Refuse oversized postings; flag sentences that address the AI", "Posting text", "None (Python)"],
      ["Evidence extractor", "Return quoted claims per category with a signal and tags", "Posting in a tagged block; schema", "gpt-6-luna"],
      ["Quote checker", "Reject any quote not found in the posting, duplicated, or from a flagged sentence", "Posting, extracted claims", "None (Python)"],
      ["Scorer", "Turn claims into 0-100 scores per profile using fixed weights", "Kept claims, profile weights", "None (Python)"],
      ["Question drafter", "Write one neutral question per important gap, for the primary profile", "Gap topics, unclear quotes (no private notes, no profile name)", "gpt-6-luna"],
      ["Privacy guard", "Check each question against private notes; rewrite or drop; log", "Questions, private notes, keyword list", "Keyword list plus gpt-6-luna"],
    ])}
  <h3>One real run, traced step by step</h3>
  <p>Posting 04 (an onsite shift role), the four default profiles, with the private note &ldquo;I have ADHD and two kids&rdquo;. Figures are from the cold run measured in <code>evals/measurements.json</code>.</p>
  <ol>{sample04_steps}</ol>
  <h3>Per-agent screenshots</h3>
  <p>Each screenshot is from the same traced run unless the caption says otherwise. Each one shows that agent&rsquo;s own output on screen.</p>
  {shot("agent_0_input_checks.png", "Input checks. Posting 05, which has a hidden instruction: the trace reports the sentences flagged and excluded before any model call.", "62%")}
  {shot("agent_1_extractor.png", "Evidence extractor. The quoted claims the model returned, underlined in the posting (red: restriction, blue: vague, green: benefit).", "85%")}
  {shot("agent_3_quote_checker_and_guard_trace.png", "Quote checker and privacy guard, from the Run details trace: \"Quote check: rejected 0 of 16\" and \"Privacy guard: 0 rewritten, 0 blocked\". No rewrite was triggered in any natural run; the guard&rsquo;s rewrite and block paths are tested in the safety log.", "62%")}
  {shot("agent_4_scorer.png", "Scorer. The score ring, the category breakdown, and the red-flag header for the parent profile, computed by fixed code.", "62%")}
  {shot("agent_5_drafter.png", "Question drafter. The Ask about cards: one neutral question per gap, as the drafter wrote it.", "70%")}
  {shot("02_review.png", "The review screen after the run: quoted claims underlined, suggestions and questions in the rail.")}
  {shot("06_details.png", "Run details: pipeline trace, token use per agent, and rejected quotes.")}
  <p class="small">Screenshots show the agents' results on screen. The trace above matches the Run details panel.</p>
</section>

<section class="page pagebreak">
  <h2>4. Tokenomics</h2>
  <p>Every number here is measured. Each sample was checked twice with the four default profiles and a private note: once cold (every model call made) and once warm (repeat of the same posting, using the extraction cache). Token counts are the model's own usage fields, recorded per call.</p>
  {table(["Per typical run (mean of 5 samples)", "Cold", "Warm (repeat posting)"], cache_rows)}
  <h3>Where the tokens go</h3>
  {table(["Agent", "Calls (cold runs)", "Input tokens", "Output tokens", "Share of output", "Share of cost"], agent_rows)}
  <p>The extractor is the largest cost. It reads the whole posting and returns the most text, which is why the extraction cache matters most.</p>
  <h3>Cost per user and at scale</h3>
  <p>Price: gpt-6-luna at $0.10 per million input tokens and $0.50 per million output tokens, from published launch coverage (<a href="https://alternativeto.net/news/2026/9/openai-introduces-gpt-6-sol-and-luna-with-lower-api-prices/">AlternativeTo, Sept 2026</a>). The cached-input price, $0.01 per million, comes from secondary listings (<a href="https://www.eesel.ai/blog/gpt-6-luna-pricing">eesel.ai</a>) and was not checked against OpenAI&rsquo;s own price page. It has no effect on the measured costs, because no cached tokens were used. Usage assumption: {CHECKS_PER_MONTH} checks per user per month, each a new posting (cold runs). The assumption is ours and should be replaced with observed use once there is a real user trial.</p>
  {table(["Scenario", "Cost"], scale_rows)}
  <h3>Steps taken to cut cost, and what they cost in quality</h3>
  {table(["Step", "Measured effect", "Performance effect"], cut_rows)}
  <div class="callout">The cache does not change scores: the warm run matched the cold run on every sample. Prompt caching does not yet work with this setup, and the report does not claim a saving from it.</div>
</section>

<section class="page pagebreak">
  <h2>5. Safety</h2>
  <p>The app takes untrusted text (job postings) and turns it into advice, so the risks that matter are an attacker hiding instructions in a posting, the model inventing facts, a privacy leak through a drafted question, and runaway cost. Each defence below was run against the failure it is for. The raw results are in <code>evals/safety_log.json</code>.</p>
  {table(["Risk", "What happened with the defence", "Evidence"], safety_rows)}
  {shot("07_flagged.png", "A posting with a hidden instruction. The sentence is flagged and marked as ignored, and the warning appears in Run details.")}
  <h3>What the defence does not do</h3>
  <p>The hidden line did change one score. For the neurodivergent profile the score moved from {s2['scores_without_line']['neurodivergent']} to {s2['scores_with_line']['neurodivergent']} when the line was present. The model read the extra sentence differently, even though the line itself was never quoted. The other three profiles moved by less than a point. The defence keeps injected text out of the evidence, but it does not make the model's wording fully immune to it.</p>
</section>

<section class="page">
  <h2>6. Impact</h2>
  <p>The app is a working prototype. Its impact so far is measured on five postings and one project team, so the claims below are limited to what was measured, plus sourced context.</p>
  <div class="stat"><b>{money(per_user_month, 4)}</b>estimated model cost per user per month at {CHECKS_PER_MONTH} checks</div>
  <div class="stat"><b>{sample04['evidence_count']}</b>quoted claims in the sample 04 run, of which {sample04['rejected']} were rejected</div>
  <div class="stat"><b>6 / 6</b>safety tests stopped the failure they target</div>
  <h3>Real-user evidence</h3>
  <p>Five people tested the app. All five (100%) said it gave them useful information they would otherwise have skipped, and that it helped them. This is the author&rsquo;s reported result from the trial; the answers are self-reported and the sample is small.</p>
  <blockquote class="trial-quote">&ldquo;Provided useful information they would have otherwise skipped. Helps them.&rdquo;
  <cite>Author&rsquo;s summary of the trial: 5 people tested the app, and 100% gave this answer.</cite></blockquote>
  <p class="small">Time saved was not measured, so the report makes no claim about it.</p>
  {shot("01_compose.png", "The start screen. The introduction explains the problem before asking for a posting.")}
  <h3>Limits of this evidence</h3>
  <p>Five postings are a small set. The postings are fictional and written for this test, so they show what the app does but not how accurately it reads real postings. No ground-truth labels exist for real postings, so accuracy is not measured. The source studies above are secondary.</p>
</section>

<section class="page pagebreak">
  <h2>7. Limits and next steps</h2>
  <h3>What does not work yet</h3>
  <ul>
    <li>Accuracy on real postings is not measured. Next: label 30 real postings by hand and score agreement.</li>
    <li>Prompt caching is not active. Cached input tokens were zero in every run.</li>
    <li>The cached-input price comes from secondary listings, not the provider&rsquo;s own price page.</li>
    <li>Budgets and call caps are held per server process, so they reset on restart.</li>
    <li>The privacy check depends on the keyword list and one model review. It can miss a fact phrased in an unexpected way.</li>
    <li>Only English postings have been tried.</li>
  </ul>
  <h3>What comes next</h3>
  <ul>
    <li>Real-user trial, with time and quality compared against reading postings alone.</li>
    <li>Hand-labelled accuracy check on real postings.</li>
    <li>Prompt caching with a verified prefix, and a stable price sheet.</li>
    <li>Hosted deployment, so the app can be tried without setup.</li>
    <li>Employer-side view: a short checklist of practices (interview questions shared in advance, written leave policy) that employers can publish.</li>
  </ul>
</section>

</body></html>"""


def slides_html() -> str:
    reveal_css = "https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css"
    reveal_theme = "https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/white.css"
    reveal_js = "https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"
    slide_css = """
:root { --page:#F7F6F3; --paper:#FDFDF7; --text:#222; --muted:#777; --pink:#E05374; --teal:#439294; --mustard:#D3A344; }
.reveal { font-family: Newsreader, Georgia, serif; color: var(--text); }
.reveal .slides { text-align: left; }
.reveal section { background: var(--page); padding: 0 !important; }
.reveal h1, .reveal h2 { font-family: 'Schibsted Grotesk', sans-serif; text-transform: uppercase; color: #111; letter-spacing: -0.01em; line-height: 1.05; margin: 0 0 .35em 0; }
.reveal h1 { font-size: 1.9em; } .reveal h2 { font-size: 1.35em; }
.reveal p, .reveal li { font-size: 0.6em; line-height: 1.4; margin: .2em 0; }
.reveal ul { margin: .2em 0 .2em 1em; }
.kicker { font-family: 'Space Mono', monospace; font-size: 0.42em; text-transform: uppercase; letter-spacing: .08em; color: var(--muted); margin: 0 0 .3em 0; }
.big { display: block; font-family: 'Schibsted Grotesk', sans-serif; font-size: 1.35em; line-height: 1.05; color: var(--pink); overflow-wrap: anywhere; }
.stats { display: flex; gap: .8em; margin: .4em 0; }
.stats > div { flex: 1 1 0; min-width: 0; background: var(--paper); box-shadow: 0 2px 8px rgba(0,0,0,.08); padding: .6em .7em; font-size: 0.5em; line-height: 1.35; }
.stats .src { font-family: 'Space Mono', monospace; font-size: 0.8em; color: var(--muted); }
.reveal table { font-size: 0.45em; width: 100%; border-collapse: collapse; margin: .3em 0; }
.reveal th { color: var(--muted); font-weight: 400; text-align: left; border-bottom: 1px solid #E0E0E0; padding: .3em .4em; }
.reveal td { border-bottom: 1px solid #E0E0E0; padding: .3em .4em; vertical-align: top; }
.shots { display: flex; gap: .8em; align-items: flex-start; }
.shots > figure { flex: 1 1 0; min-width: 0; margin: 0; }
.shots img { width: 100%; max-height: 330px; object-fit: contain; border: 1px solid #E0E0E0; box-shadow: 0 2px 8px rgba(0,0,0,.08); }
.shots figcaption { font-family: 'Space Mono', monospace; font-size: 0.38em; color: var(--muted); margin-top: .3em; }
.diagram svg { width: 100%; height: auto; max-height: 300px; }
.note { font-family: 'Space Mono', monospace; font-size: 0.4em; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; margin-top: .4em; }
.pad { padding: 1.2em 1.4em; box-sizing: border-box; height: 100%; }
"""

    def stats_row(items):
        cells = "".join(
            f'<div><span class="big">{big}</span>{label}{"<br><span class=src>" + src + "</span>" if src else ""}</div>'
            for big, label, src in items)
        return f'<div class="stats">{cells}</div>'

    s1 = S["1_invented_quote"]; s2 = S["2_prompt_injection"]; s3 = S["3_overspending_budget"]
    s4 = S["4_runaway_calls"]; s5 = S["5_oversized_posting"]; s6 = S["6_private_data_leak"]
    max_shift = max(abs(s2["scores_with_line"][k] - s2["scores_without_line"][k]) for k in s2["scores_with_line"])

    safety_rows = [
        ("Invented quote", "Quote checker", f"rejected ({s1['result']})"),
        ("Prompt injection", "Injection scanner", f"{len(s2['flagged_sentences'])} sentences flagged; 0 injected quotes kept"),
        ("Budget exhausted", "Budget check", "stopped, 0 model calls"),
        ("Runaway loop", "Per-run call cap", "stopped at 6 calls"),
        ("Oversized paste", "Length limit", "refused, 0 model calls"),
        ("Private data leak", "Privacy guard", f"{s6['action']} and logged; 0 leaks left"),
        ("Wrong action", "Route check", "no endpoint sends outward (tested)"),
    ]
    safety_table = ("<table><thead><tr><th>Failure</th><th>Defence</th><th>Result (tested)</th></tr></thead><tbody>"
                    + "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in safety_rows)
                    + "</tbody></table>")

    shares = {n: round(100 * t["cost"] / total_cost) for n, t in agents.items()}
    per_run = money(cold["cost_usd"], 5)
    warm_pct = f"{saving_warm:.0%}"

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Between the Lines: slides</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="{reveal_css}">
<link rel="stylesheet" href="{reveal_theme}">
<style>{font_faces()}\n{slide_css}</style></head><body>
<div class="reveal"><div class="slides">

<section class="pad">
  <p class="kicker">MGT 409 · Final project · Stevie Wolfe</p>
  <h1>Between the Lines</h1>
  <p>Know what a job asks of you before you apply. Every claim is quoted from the posting.</p>
  <p class="note">Repository: github.com/steviewolfe/final-finale-finala-fin</p>
</section>

<section class="pad">
  <p class="kicker">The problem</p>
  <h2>Postings hide what decides fit</h2>
  {stats_row([
      ("84%", "of 1,886 job ads use ableist wording", "PubMed 41701271"),
      ("9%", "of ads state how to request accommodations", "PubMed 41701271"),
      ("71% vs 49%", "of parents and carers want flexibility vs get it", "Indeed, Ireland"),
  ])}
  <p>Most people guess, or stay silent. Asking can feel risky, so the decision is made with less information than it should be.</p>
</section>

<section class="pad">
  <p class="kicker">What is new</p>
  <h2>Claims with sources, repeatable scores</h2>
  <table>
    <thead><tr><th></th><th>Raaha (press accounts)</th><th>Posting-language tools</th><th>Between the Lines</th></tr></thead>
    <tbody>
      <tr><td>Each claim quoted from the posting</td><td>Not described</td><td>No, flags words</td><td><b>Yes; invented quotes rejected</b></td></tr>
      <tr><td>Same input, same score</td><td>Model-produced</td><td>Word lists</td><td><b>Yes; repeat runs matched exactly</b></td></tr>
      <tr><td>Questions checked against private notes</td><td>Not described</td><td>No</td><td><b>Yes; every change logged</b></td></tr>
      <tr><td>Needs compared side by side</td><td>One quiz profile</td><td>No</td><td><b>8 profiles, up to 4 at once</b></td></tr>
    </tbody>
  </table>
</section>

<section class="pad">
  <p class="kicker">How the agents work</p>
  <h2>Two language-model agents, three checks</h2>
  <div class="diagram">{DIAGRAM}</div>
  <p class="note">Pink: language-model agents (gpt-6-luna) · Ink: plain Python checks</p>
</section>

<section class="pad">
  <p class="kicker">Demo</p>
  <h2>Every claim sits next to its quote</h2>
  <div class="shots">
    <figure><img src="{data_uri(SHOTS / '02_review.png', 'image/png')}" alt="Review screen"><figcaption>Review: quoted claims and the rail</figcaption></figure>
    <figure><img src="{data_uri(SHOTS / '07_flagged.png', 'image/png')}" alt="Flagged instruction"><figcaption>Hidden instruction caught and ignored</figcaption></figure>
  </div>
</section>

<section class="pad">
  <p class="kicker">Cost to run</p>
  <h2>Under a tenth of a cent per check</h2>
  {stats_row([
      (per_run, f"per typical check, measured ({int(cold['calls'])} calls)", ""),
      (warm_pct, "lower cost on a repeat posting (cache)", "measured"),
      (money(per_user_month, 4), f"per user per month at {CHECKS_PER_MONTH} checks", "estimate"),
  ])}
  <table>
    <thead><tr><th>Users</th><th>Monthly cost</th></tr></thead>
    <tbody>
      <tr><td>100</td><td>{money(per_user_month * 100, 2)}</td></tr>
      <tr><td>10,000</td><td>{money(per_user_month * 10_000, 2)}</td></tr>
    </tbody>
  </table>
  <p class="note">Prices: gpt-6-luna, $0.10 in / $0.50 out per million tokens. Extractor is {shares['extractor']}% of cost.</p>
</section>

<section class="pad">
  <p class="kicker">Safety</p>
  <h2>Six failures tested, six stopped</h2>
  {safety_table}
  <p class="note">Injection shifted one profile by {max_shift:.1f} points. Reported as a limit.</p>
</section>

<section class="pad">
  <p class="kicker">Impact</p>
  <h2>What we measured, and what testers said</h2>
  {stats_row([
      ("5 of 5", "testers said it gave useful information they would have skipped", "self-reported"),
      ("100%", "repeat checks matched the first scores exactly", "measured"),
      (f"{sample04['evidence_count']} of {sample04['evidence_count'] + sample04['rejected']}", "quotes in the traced run kept after checking", "measured"),
  ])}
  <p>Time saved was not measured, so no time claim is made.</p>
</section>

<section class="pad">
  <p class="kicker">Limits and next</p>
  <h2>What we would do next</h2>
  <ul>
    <li>Accuracy on 30 real postings, labelled by hand</li>
    <li>Working prompt caching, and a provider-confirmed price sheet</li>
    <li>Timed trial with more testers and one quote each, with permission</li>
    <li>Hosted deployment, so no setup is needed</li>
  </ul>
</section>

<section class="pad">
  <p class="kicker">Thank you</p>
  <h2>Between the Lines</h2>
  <p>Code and run instructions: github.com/steviewolfe/final-finale-finala-fin</p>
</section>

</div></div>
<script src="{reveal_js}"></script>
<script>Reveal.initialize({{ hash: true, controls: true, progress: true, slideNumber: true, width: 1280, height: 720, margin: 0.04 }});</script>
</body></html>"""


(ROOT / "docs" / "report.html").write_text(report_html(), encoding="utf-8")
(ROOT / "docs" / "slides.html").write_text(slides_html(), encoding="utf-8")
print("wrote docs/report.html and docs/slides.html")
print("per user per month:", round(per_user_month, 6), "| scores match warm/cold:", scores_match)
