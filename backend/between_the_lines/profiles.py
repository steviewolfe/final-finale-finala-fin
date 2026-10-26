"""Need profiles: category weights, tag overrides, and drafter topic hints.

Weights follow the order in CATEGORIES and must sum to 1.0 (tests check this).
Tag overrides replace the base signal value for an item that carries the tag.
If several overrides match, the lowest value wins.

Topic hints are condition-free. They describe what to ask about, never why.
"""

from __future__ import annotations

from .schemas import CATEGORIES

PROFILES: dict[str, dict] = {
    "parent": {
        "label": "Working parent or caregiver",
        "weights": dict(zip(CATEGORIES, [.21, .17, .04, .11, .06, .06, .25, .05, .05])),
        "tag_overrides": {
            "after_hours_expected": 0,
            "on_call": 10,
            "travel_required": 15,
            "flexible_hours": 100,
            "mandatory_social_events": 20,
        },
    },
    "neurodivergent": {
        "label": "Neurodivergent",
        "weights": dict(zip(CATEGORIES, [.09, .09, .18, .15, .13, .09, .04, .15, .08])),
        "tag_overrides": {
            "open_office": 10,
            "phone_heavy": 15,
            "vague_pace_language": 20,
            "unstructured_interview": 15,
            "async_friendly": 100,
            "clear_expectations": 100,
            "mandatory_social_events": 15,
        },
    },
    "chronic_illness": {
        "label": "Chronic illness or disability",
        "weights": dict(zip(CATEGORIES, [.22, .18, .04, .13, .07, .05, .18, .03, .10])),
        "tag_overrides": {
            "onsite_required": 10,
            "travel_required": 10,
            "on_call": 10,
            "remote_ok": 100,
            "generous_leave": 100,
            "mandatory_social_events": 30,
        },
    },
    "eldercare": {
        "label": "Eldercare or sandwich-generation caregiver",
        "weights": dict(zip(CATEGORIES, [.23, .15, .04, .10, .04, .06, .28, .05, .05])),
        "tag_overrides": {
            "on_call": 5,
            "travel_required": 15,
            "after_hours_expected": 15,
            "onsite_required": 25,
            "unclear_leave": 20,
            "mandatory_social_events": 20,
        },
    },
    "deaf_hard_of_hearing": {
        "label": "Deaf or hard of hearing",
        "weights": dict(zip(CATEGORIES, [.06, .12, .26, .08, .10, .14, .04, .08, .12])),
        "tag_overrides": {
            "phone_heavy": 5,
            "open_office": 25,
            "unstructured_interview": 20,
            "async_friendly": 100,
            "clear_expectations": 100,
        },
    },
    "religious_observance": {
        "label": "Religious observance",
        "weights": dict(zip(CATEGORIES, [.30, .08, .04, .08, .20, .06, .14, .04, .06])),
        "tag_overrides": {
            "after_hours_expected": 10,
            "on_call": 15,
            "mandatory_social_events": 10,
            "travel_required": 20,
            "flexible_hours": 100,
        },
    },
    "students_part_time": {
        "label": "Students and part-time workers",
        "weights": dict(zip(CATEGORIES, [.30, .14, .04, .12, .04, .06, .18, .08, .04])),
        "tag_overrides": {
            "fixed_hours": 25,
            "after_hours_expected": 5,
            "on_call": 10,
            "unclear_leave": 25,
            "flexible_hours": 100,
        },
    },
    "career_returners": {
        "label": "Career returners",
        "weights": dict(zip(CATEGORIES, [.10, .12, .08, .12, .10, .16, .06, .20, .06])),
        "tag_overrides": {
            "unstructured_interview": 15,
            "vague_pace_language": 25,
            "clear_expectations": 100,
        },
    },
}

# The compare view starts with these four. The server accepts up to MAX_PROFILES_PER_RUN.
DEFAULT_COMPARE = ["parent", "neurodivergent", "chronic_illness", "eldercare"]

# Generic, condition-free prompts for the drafter. Used for every profile.
TOPIC_HINTS: dict[str, str] = {
    "schedule_flexibility": "how working hours are set and how schedule changes are communicated",
    "remote_policy": "where and how often people work, and how location arrangements are decided",
    "communication_style": "how the team communicates day to day and how much is live versus written",
    "pace_and_pressure": "typical workload, how priorities change, and how deadlines are handled",
    "work_environment": "the physical and social setting, travel, and team events",
    "interview_process": "the stages of the interview and what each stage involves",
    "caregiving_and_leave": "how time off, short-notice absences, and leave requests are handled",
    "role_clarity": "what a typical week looks like and how success is measured",
    "inclusion_and_accommodation": "what adjustments to the hiring process or the role are available, and how to ask for them",
}

FLAG_WEIGHT = 0.15
FLAG_SCORE = 35
