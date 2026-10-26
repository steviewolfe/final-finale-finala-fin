"""Plain-language explanations for the review screen.

Static text only. No model calls. The drafter never receives this text, so it
cannot leak into questions. Wording is needs-based and never diagnostic.
"""

from __future__ import annotations

from .profiles import PROFILES
from .schemas import CATEGORIES, TAGS

TAG_WHY: dict[str, str] = {
    "fixed_hours": "Fixed hours leave little room to adjust around other commitments.",
    "flexible_hours": "Flexible hours make it easier to plan around other commitments.",
    "on_call": "On-call duty can interrupt evenings, weekends and planned time off.",
    "after_hours_expected": "Expected after-hours work can clash with fixed daily routines.",
    "travel_required": "Travel takes time away and can be hard to plan around.",
    "remote_ok": "Remote work removes the commute and can make routines easier to keep.",
    "onsite_required": "Onsite requirements fix where and when the work happens.",
    "open_office": "Open offices can be noisy and hard to focus in for long stretches.",
    "phone_heavy": "Lots of phone work can mean constant interruptions and less written detail.",
    "async_friendly": "Written, asynchronous updates let people read and reply at their own pace.",
    "vague_pace_language": "Vague pace language makes the real workload hard to judge.",
    "clear_expectations": "Clear, written expectations make it easier to know what good work looks like.",
    "unstructured_interview": "An unstructured interview makes the process harder to prepare for.",
    "generous_leave": "Generous leave gives room for time off without losing pay or standing.",
    "unclear_leave": "Unclear leave rules make it hard to know what time off is possible.",
}

SIGNAL_WHY: dict[str, str] = {
    "positive": "The posting states a concrete benefit or flexibility.",
    "negative": "The posting states a concrete restriction or requirement.",
    "unclear": "The wording is vague, so the real situation is hard to judge.",
}

FLAGGED_WHY = (
    "Ignored. This sentence reads like an instruction to the AI. "
    "It had no effect on the score."
)

# One short clause per profile and category. Phrased around practical needs,
# never around a condition or a personal circumstance.
CATEGORY_WHY: dict[str, dict[str, str]] = {
    "parent": {
        "schedule_flexibility": "Predictable end times make school runs and childcare easier to plan.",
        "remote_policy": "Working from home can cut commute time around school and childcare.",
        "communication_style": "Written updates reduce interruptions during school hours.",
        "pace_and_pressure": "Sustained pressure leaves little slack for unplanned family needs.",
        "work_environment": "Travel and events can clash with childcare arrangements.",
        "interview_process": "A clear process makes it easier to schedule around childcare.",
        "caregiving_and_leave": "Clear leave for sick children and emergencies protects routines.",
        "role_clarity": "A clear role makes it easier to plan a workday with interruptions.",
    },
    "neurodivergent": {
        "schedule_flexibility": "Flexible or predictable hours help with focus and energy.",
        "remote_policy": "A quieter or self-directed setup can suit focused work.",
        "communication_style": "Written, asynchronous communication lowers the load of live interaction.",
        "pace_and_pressure": "A steady pace with clear priorities is easier to sustain.",
        "work_environment": "Less noise and fewer interruptions support sustained focus.",
        "interview_process": "A structured interview gives a clear way to prepare.",
        "caregiving_and_leave": "Clear rules for breaks and time off help plan recovery.",
        "role_clarity": "Clear responsibilities and success measures reduce guesswork.",
    },
    "chronic_illness": {
        "schedule_flexibility": "Flexible hours help plan around energy levels and appointments.",
        "remote_policy": "Remote options reduce the energy cost of commuting.",
        "communication_style": "Written updates keep the work manageable on low-energy days.",
        "pace_and_pressure": "Lower sustained pressure makes the work easier to maintain.",
        "work_environment": "Less travel and fewer long on-site days help manage energy.",
        "interview_process": "A clear process makes it easier to plan around appointments.",
        "caregiving_and_leave": "Generous and clear sick and medical leave protects pacing.",
        "role_clarity": "A clear scope makes it easier to plan and pace the work.",
    },
    "eldercare": {
        "schedule_flexibility": "Flexible hours help when a relative needs appointments or support.",
        "remote_policy": "Working from home makes it easier to be close by when needed.",
        "communication_style": "Written updates allow replies between caring tasks.",
        "pace_and_pressure": "Lower sustained pressure leaves room for unplanned family needs.",
        "work_environment": "Less travel keeps you reachable for family needs.",
        "interview_process": "A clear process makes it easier to plan around family commitments.",
        "caregiving_and_leave": "Clear, reasonable leave for family emergencies protects the role.",
        "role_clarity": "A clear role makes it easier to plan around unpredictable days.",
    },
}


def tag_why(tags: list[str], signal: str) -> str:
    """Return the first matching tag explanation, or the signal fallback."""
    for t in tags:
        if t in TAG_WHY:
            return TAG_WHY[t]
    return SIGNAL_WHY[signal]


def profile_why(profile_id: str, category: str) -> str:
    return CATEGORY_WHY[profile_id][category]
