"""Output contracts for each LLM agent.

Each agent has two pieces: a strict JSON schema sent to the model, and a
pydantic model that validates what comes back. Strict mode requires every
property to be listed as required and additionalProperties to be false.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

CATEGORIES = [
    "schedule_flexibility",
    "remote_policy",
    "communication_style",
    "pace_and_pressure",
    "work_environment",
    "interview_process",
    "caregiving_and_leave",
    "role_clarity",
]

TAGS = [
    "fixed_hours",
    "flexible_hours",
    "on_call",
    "after_hours_expected",
    "travel_required",
    "remote_ok",
    "onsite_required",
    "open_office",
    "phone_heavy",
    "async_friendly",
    "vague_pace_language",
    "clear_expectations",
    "unstructured_interview",
    "generous_leave",
    "unclear_leave",
]

SIGNALS = ["positive", "negative", "unclear"]
ASK_WHO = ["recruiter", "hiring_manager", "team_member"]
VERDICTS = ["safe", "leaks", "infers"]
FACT_TYPES = ["diagnosis", "health", "children", "family", "other", "none"]


# ---------- Agent 1: Evidence Extractor ----------

EXTRACTOR_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["evidence"],
    "properties": {
        "evidence": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["category", "exact_quote", "signal", "tags", "note"],
                "properties": {
                    "category": {"type": "string", "enum": CATEGORIES},
                    "exact_quote": {"type": "string"},
                    "signal": {"type": "string", "enum": SIGNALS},
                    "tags": {"type": "array", "items": {"type": "string", "enum": TAGS}},
                    "note": {"type": "string"},
                },
            },
        }
    },
}


class Evidence(BaseModel):
    category: Literal[
        "schedule_flexibility",
        "remote_policy",
        "communication_style",
        "pace_and_pressure",
        "work_environment",
        "interview_process",
        "caregiving_and_leave",
        "role_clarity",
    ]
    exact_quote: str = Field(max_length=250)
    signal: Literal["positive", "negative", "unclear"]
    tags: list[str]
    note: str = Field(max_length=160)


class ExtractionResult(BaseModel):
    evidence: list[Evidence]


# ---------- Agent 4: Question Drafter ----------

DRAFTER_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["questions"],
    "properties": {
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["category", "question", "ask_who"],
                "properties": {
                    "category": {"type": "string", "enum": CATEGORIES},
                    "question": {"type": "string"},
                    "ask_who": {"type": "string", "enum": ASK_WHO},
                },
            },
        }
    },
}


class Question(BaseModel):
    category: str
    question: str = Field(max_length=200)
    ask_who: Literal["recruiter", "hiring_manager", "team_member"]


class DraftResult(BaseModel):
    questions: list[Question]


# ---------- Agent 5: Privacy Guard (LLM layer) ----------

GUARD_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["results"],
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "verdict", "fact_type", "rewrite"],
                "properties": {
                    "id": {"type": "integer"},
                    "verdict": {"type": "string", "enum": VERDICTS},
                    "fact_type": {"type": "string", "enum": FACT_TYPES},
                    "rewrite": {"type": ["string", "null"]},
                },
            },
        }
    },
}


class GuardVerdict(BaseModel):
    id: int
    verdict: Literal["safe", "leaks", "infers"]
    fact_type: Literal["diagnosis", "health", "children", "family", "other", "none"]
    rewrite: Optional[str] = None


class GuardResult(BaseModel):
    results: list[GuardVerdict]
