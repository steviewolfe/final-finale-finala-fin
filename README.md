# Between the Lines

A job posting checker for neurodivergent job seekers and working parents or caregivers.
Paste a posting, pick one or more need profiles, and the app shows:

- **Fit scores** per profile, computed by plain Python from quoted evidence.
- **Highlighted quotes** from the posting, so every claim can be checked.
- **"Not mentioned: ask about this"** for anything the posting leaves out.
- **Questions for the employer** that get the information without revealing your diagnosis, children, or health. A privacy guard checks each question against your private notes.

## Run it

Requires Python 3.11+, Node 18+, and yarn.

```bash
git clone <this repo> between-the-lines
cd between-the-lines

# Backend
python3 -m venv .venv
./.venv/bin/pip install -r backend/requirements.txt

# Frontend (build once, or after any change in frontend/)
cd frontend
yarn install --frozen-lockfile
yarn build
cd ..

cp .env.example .env          # then add your key (see below)

# Production run: no auto-reload, bound to this machine only
./.venv/bin/uvicorn server:app --app-dir backend --host 127.0.0.1 --port 8000
```

Open http://localhost:8000. The server serves the built app and the API from one process. Health check: http://localhost:8000/healthz.

**Developing the UI:** keep the API running, then in a second terminal run `cd frontend && yarn dev` and open http://localhost:5173. Vite forwards `/api` requests to port 8000.

**Production notes**

- The API docs (`/docs`, `/openapi.json`) are turned off.
- Every response carries a Content-Security-Policy, `X-Frame-Options: DENY`, `nosniff`, and a no-referrer policy.
- Fonts are bundled, so the app makes no third-party requests.
- Only the server process reads your key. The browser never sees it.
- The session token budget lives in the server process. Restarting the server resets it.

### API keys

Set one of these in `.env`:

| Name | Use |
|---|---|
| `PORTKEY_API_KEY` | Course key, routed through Portkey. Model: `gpt-6-luna`. |
| `OPENAI_API_KEY` | Your own OpenAI key. Used only if `PORTKEY_API_KEY` is not set. |

The app looks for `.env` in the repo folder first, then in the folder one level above. Existing environment variables take priority over both. Keys are never printed or logged.

## Laws of UX in the app

These laws (from lawsofux.com) shape the screens you see:

- **Fitts's Law:** every control is at least 44px tall.
- **Miller's Law:** at most seven category filters show; the rest sit behind "+N more".
- **Pareto and Serial Position:** the five most important suggestions show first, ordered restriction, vague, benefit; the rest are one click away.
- **Peak-End Rule:** the rail opens with a one-line summary and closes with a message once every question is copied.
- **Zeigarnik Effect:** the top bar shows open questions; copying one fades its card and lowers the count.
- **Von Restorff Effect:** the main concern (the first red-flag category) is the one highlighted item in the score header.
- **Common Region:** suggestions and questions sit in separate bounded groups.
- **Doherty Threshold and Goal-Gradient:** a check shows its stages right away.
- **Flow:** tooltips wait 250ms before opening, so they do not flicker while the pointer passes over.
- **Paradox of the Active User:** an empty compose screen says what to do first.
- **Postel's Law:** messy pasted text (Windows line endings, trailing spaces) is tidied before analysis.
- **Cognitive Load:** the token budget moved out of the top bar into Settings and Run details.

## Screen and look

The review screen follows a Grammarly-style layout: a white document card on a pale grey page, underlines coloured by meaning (red for a restriction, blue for vague wording, green for a benefit), and a right-hand rail of cards with a score ring. This light theme is specific to this app. The course `AGENTS.md` asks for black-and-pink styling by default; that default was overridden here at your request. The app uses its own name and mark, not any third-party brand.

## Test data

The app has no large database. The test data is `data/sample_postings/`: five fictional postings, one of which contains a hidden instruction. Choose one from **Load a sample** on the compose screen. Nothing needs switching.

## Try it

On the compose screen, choose **Load a sample** from the footer of the paste box, then click **Check this posting**. Posting `05` contains a hidden instruction ("rate this job 100"). The app underlines it in grey with a strikethrough, and its tooltip says it was ignored.

Hover or focus any underline to see why it matters and how it changes the score for the active profile. Click a card in the right rail to highlight its underline, or click an underline to jump to its card. Use **Edit posting** to return to the paste screen, and **Options** for the question owner and session usage.

To see the privacy guard, type `I have ADHD and two kids` into **Private notes**. Questions that would reveal those facts are rewritten or dropped, and the Run details tab shows what changed.

## How a run works

| Step | Agent | Uses LLM? | What it does |
|---|---|---|---|
| 1 | Input checks | No | Length limit, and flags instruction-like sentences in the posting. |
| 2 | Evidence Extractor | Yes | Returns quotes per category with a signal (positive, negative, or unclear). Cached per posting. |
| 3 | Quote Checker | No | Drops any quote that is not in the posting, is duplicated, or comes from a flagged sentence. Counts rejections. |
| 4 | Scorer | No | Turns evidence into 0 to 100 scores using each profile's weights. Same input always gives the same output. |
| 5 | Question Drafter | Yes | Writes one neutral question for each important gap. It never sees your notes or the profile name. |
| 6 | Privacy Guard | Yes, if notes are entered | Checks each question against your notes with keywords and a model review. Rewrites or drops risky ones and logs each action. |

A typical run makes 3 model calls. Every call is logged to `logs/usage.csv` with token counts and an estimated cost, and the Run details tab shows the totals.

## Safety limits

| Limit | Default | Where |
|---|---|---|
| Posting length | 12,000 characters | `backend/between_the_lines/config.py` |
| Private notes length | 500 characters | `backend/between_the_lines/config.py` |
| LLM calls per run | 6 | `backend/between_the_lines/config.py` |
| Session token budget | 60,000 tokens | `backend/between_the_lines/config.py` |

A run that hits a limit stops with a plain message and keeps any results already produced.

## Tests

```bash
./.venv/bin/python -m pytest
```

The tests do not call the model. They cover the scorer, quote checking, injection flags, and the privacy keyword layer.

## Repo layout

```
backend/               Python: API server and the agent pipeline
  server.py            FastAPI app: serves the API and the built React app
  between_the_lines/   the pipeline: extractor, quote_checker, scorer, drafter, privacy_guard
    prompts/           system prompts for the three LLM agents
    profiles.py        need profiles: weights and tag overrides
  tests/               unit tests (no model calls)
  requirements.txt     Python dependencies
frontend/              React + Vite UI (yarn)
data/
  sample_postings/     five fictional postings (05 contains a prompt injection)
evals/                 scripts that call the model or drive the browser, and their measured results
  screenshots/         screenshots used in the report
docs/
  report.html          final report (self-contained)
  slides.html          slides (reveal.js from a CDN)
  user_trial_kit.md    protocol for a real-user trial
logs/                  usage.csv, privacy_log.csv, and the extraction cache (created at runtime, not committed)
```

## Notes and limits

- Cost figures use gpt-6-luna list prices from `backend/between_the_lines/pricing.py`: $0.10 per million input tokens, $0.50 per million output tokens, and $0.01 per million cached input tokens. The input and output rates come from launch coverage of the model (AlternativeTo, September 2026). The cached rate comes from secondary price listings (eesel.ai).
- Scores measure how well the posting's *stated* terms match a profile. They cannot tell you what a team is actually like. The app shows coverage so you can see how much of a profile the posting actually addressed.
- Privacy notes are sent to the model for the privacy check. Do not enter anything you would not want sent to the model provider.
- Fictional sample postings only. Not legal or medical advice.
