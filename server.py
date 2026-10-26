"""HTTP API for Between the Lines. Serves the built React app at /.

Run from the repo folder (after building the frontend once):
    ./.venv/bin/uvicorn server:app --port 8000

The session token budget is held in this process. The app is meant to run
on one machine for one user, so this is one budget per running server.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from between_the_lines.config import MAX_NOTES_CHARS, MAX_POSTING_CHARS, SESSION_TOKEN_BUDGET
from between_the_lines.explain import FLAGGED_WHY, profile_why, tag_why
from between_the_lines.highlight import posting_segments
from between_the_lines.llm import SessionBudget
from between_the_lines.pipeline import RunResult, run_pipeline
from between_the_lines.privacy_guard import note_terms
from between_the_lines.privacy_lexicon import redact
from between_the_lines.profiles import PROFILES
from between_the_lines.schemas import CATEGORIES
from between_the_lines.scorer import item_value
from between_the_lines.security import PostingTooLong

REPO_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = REPO_DIR / "sample_postings"
DIST_DIR = REPO_DIR / "frontend" / "dist"

# Production: no interactive API docs are published.
app = FastAPI(title="Between the Lines", version="1.0.0", docs_url=None, redoc_url=None, openapi_url=None)

_CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; font-src 'self'; connect-src 'self'; "
    "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = _CSP
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}
budget = SessionBudget(limit=SESSION_TOKEN_BUDGET)


class AnalyzeRequest(BaseModel):
    posting: str = Field(max_length=MAX_POSTING_CHARS + 2000)
    profiles: list[str] = Field(min_length=1)
    primary: str
    notes: str = Field(default="", max_length=MAX_NOTES_CHARS)


def _sample_names() -> list[str]:
    return sorted(p.name for p in SAMPLE_DIR.glob("*.txt"))


def _budget_json() -> dict:
    return {"used": budget.used, "limit": budget.limit}


def _evidence_json(eid: int, e, profile_ids: list[str]) -> dict:
    """One evidence item, with its explanation and its score impact per profile."""
    impact = []
    for pid in profile_ids:
        weight = PROFILES[pid]["weights"][e.category]
        impact.append({
            "profile_id": pid,
            "value": item_value(e, PROFILES[pid]["tag_overrides"]),
            "weight": weight,
            "profile_why": profile_why(pid, e.category),
        })
    return {
        "id": eid,
        "category": e.category,
        "exact_quote": e.exact_quote,
        "signal": e.signal,
        "note": e.note,
        "tags": e.tags,
        "why": tag_why(e.tags, e.signal),
        "impact": impact,
    }


def _gaps_json(result: RunResult, questions: list[dict], notes: str) -> list[dict]:
    """Categories with no kept evidence, or only unclear evidence, per the shown profiles."""
    by_cat_question = {q["category"]: q for q in questions if q["action"] != "blocked"}
    original_by_cat = {q["category"]: q["original"] for q in questions if q["action"] == "rewritten"}
    dropped = {q["category"] for q in questions if q["action"] == "blocked"}
    gaps = []
    for cat in CATEGORIES:
        items = [e for e in result.evidence if e.category == cat]
        if items and any(e.signal in ("positive", "negative") for e in items):
            continue
        state = "unclear" if items else "missing"
        q = by_cat_question.get(cat)
        gaps.append({
            "category": cat,
            "state": state,
            "question": q["final"] if q else None,
            "question_rewritten": bool(q and q["action"] == "rewritten"),
            "question_original": original_by_cat.get(cat),
            "question_dropped": cat in dropped and q is None,
            "weights": [
                {"profile_id": pid, "weight": PROFILES[pid]["weights"][cat]}
                for pid in result.profile_ids
            ],
        })
    return gaps


def _serialize(result: RunResult, notes: str) -> dict:
    qc = result.quote_check
    terms = note_terms(notes)

    scores = []
    for pid in result.profile_ids:
        s = result.scores[pid]
        scores.append({
            "profile_id": s.profile_id,
            "label": s.label,
            "overall": s.overall,
            "band": s.band,
            "coverage": s.coverage,
            "red_flags": s.red_flags,
            "categories": [
                {
                    "category": cat,
                    "score": s.categories[cat].score,
                    "weight": s.categories[cat].weight,
                    "item_count": s.categories[cat].item_count,
                    "red_flag": s.categories[cat].red_flag,
                }
                for cat in CATEGORIES
            ],
        })

    questions = []
    if result.guard:
        for q in result.guard.questions:
            questions.append({
                "index": q.index,
                "category": q.category,
                "ask_who": q.ask_who,
                "action": q.action,
                "layer": q.layer,
                "fact_type": q.fact_type,
                "final": q.final,
                # Redacted copy of the drafted question, used only for the "what changed" list.
                "original": redact(q.original, terms),
            })

    m = result.meter
    return {
        "run_id": result.run_id,
        "error": result.error,
        "trace": result.trace,
        "cache_hit": result.cache_hit,
        "flagged": result.flagged,
        "segments": [
            {**seg, "why": FLAGGED_WHY} if seg["kind"] == "flagged" else seg
            for seg in posting_segments(
                result.posting,
                [(i, e.exact_quote, e.signal) for i, e in enumerate(result.evidence)],
            )
        ],
        "scores": scores,
        "evidence": [_evidence_json(i, e, result.profile_ids) for i, e in enumerate(result.evidence)],
        "gaps": _gaps_json(result, questions, notes),
        "rejected": [
            {"category": r.category, "quote": r.quote, "reason": r.reason}
            for r in (qc.rejected if qc else [])
        ],
        "questions": questions,
        "usage": {
            "calls": m.calls,
            "input_tokens": m.input_tokens,
            "output_tokens": m.output_tokens,
            "cached_input_tokens": m.cached_input_tokens,
            "cost_usd": round(m.cost_usd, 6),
            "rows": [
                {"agent": r["agent"], "input_tokens": r["input_tokens"],
                 "cached_input_tokens": r["cached_input_tokens"],
                 "output_tokens": r["output_tokens"],
                 "cost_usd": round(r["cost_usd_estimate"], 6)}
                for r in m.rows
            ],
        },
        "budget": _budget_json(),
    }


@app.get("/api/profiles")
def list_profiles() -> list[dict]:
    return [{"id": pid, "label": p["label"]} for pid, p in PROFILES.items()]


@app.get("/api/limits")
def limits() -> dict:
    return {"max_posting_chars": MAX_POSTING_CHARS, "max_notes_chars": MAX_NOTES_CHARS}


@app.get("/api/samples")
def list_samples() -> list[str]:
    return _sample_names()


@app.get("/api/samples/{name}")
def get_sample(name: str) -> dict:
    if name not in _sample_names():
        raise HTTPException(status_code=404, detail="Unknown sample")
    return {"name": name, "text": (SAMPLE_DIR / name).read_text(encoding="utf-8")}


@app.get("/api/budget")
def get_budget() -> dict:
    return _budget_json()


@app.post("/api/budget/reset")
def reset_budget() -> dict:
    budget.used = 0
    return _budget_json()


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest) -> dict:
    unknown = [p for p in req.profiles if p not in PROFILES]
    if unknown or req.primary not in PROFILES:
        raise HTTPException(status_code=400, detail="Unknown profile")
    try:
        result = run_pipeline(
            req.posting, req.profiles, req.primary, req.notes, budget=budget,
        )
    except PostingTooLong as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _serialize(result, req.notes)


if not DIST_DIR.exists():
    @app.get("/")
    def not_built() -> dict:
        return {"detail": "The web app is not built yet. Run `yarn build` in frontend/ and restart the server."}

if DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")

    @app.get("/{path:path}")
    def spa(path: str) -> FileResponse:
        target = (DIST_DIR / path).resolve()
        inside = DIST_DIR.resolve() in target.parents
        if path and inside and target.is_file():
            return FileResponse(target)
        return FileResponse(DIST_DIR / "index.html")
