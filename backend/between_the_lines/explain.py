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
    "accommodation_stated": "The posting says adjustments can be requested, so the conversation can start from a known route.",
    "equal_opportunity_stated": "A stated equal-opportunity commitment suggests the employer has thought about fair treatment.",
    "mandatory_social_events": "Expected attendance at team events can clash with caring duties, faith practice, or energy limits.",
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
        "inclusion_and_accommodation": "A stated route for flexible arrangements makes it easier to ask for them.",
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
        "inclusion_and_accommodation": "A stated way to request adjustments makes it easier to ask for them.",
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
        "inclusion_and_accommodation": "A stated route for adjustments makes it easier to ask for them.",
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
        "inclusion_and_accommodation": "A stated route for adjustments makes it easier to ask for them.",
    },
    "deaf_hard_of_hearing": {
        "schedule_flexibility": "Schedules posted in advance make planning around captioned or interpreted sessions easier.",
        "remote_policy": "Written-first setups let you work without relying on overheard conversation.",
        "communication_style": "Written, captioned, and asynchronous communication lowers the load of live calls.",
        "pace_and_pressure": "Clear priorities in writing reduce the need to catch fast verbal changes.",
        "work_environment": "Quieter spaces and fewer overlapping conversations make listening easier.",
        "interview_process": "A structured interview with questions shared in advance lets you prepare access needs.",
        "caregiving_and_leave": "Clear rules for time off and appointments help plan access support.",
        "role_clarity": "Written responsibilities and success measures reduce reliance on verbal instructions.",
        "inclusion_and_accommodation": "A stated route for access adjustments makes it easier to ask for them.",
    },
    "religious_observance": {
        "schedule_flexibility": "Predictable schedules make it easier to plan around prayer times and holy days.",
        "remote_policy": "Working from home can make it easier to keep prayer times and rest days.",
        "communication_style": "Written updates reduce pressure to answer on days or times you observe.",
        "pace_and_pressure": "Steady pacing leaves room for observance without falling behind.",
        "work_environment": "Clear dress code and event expectations make it easier to plan in advance.",
        "interview_process": "Knowing interview dates early helps plan around observance.",
        "caregiving_and_leave": "Clear leave for holy days and observance protects your practice.",
        "role_clarity": "Clear responsibilities make it easier to plan a week around observance.",
        "inclusion_and_accommodation": "A stated route for religious accommodation makes it easier to ask for it.",
    },
    "students_part_time": {
        "schedule_flexibility": "Fixed or posted shifts make it easier to fit around classes and other work.",
        "remote_policy": "Remote options can save travel time between study, work, and home.",
        "communication_style": "Written updates fit around study time and irregular availability.",
        "pace_and_pressure": "A steady pace is easier to keep up with alongside coursework.",
        "work_environment": "Clear expectations for events and travel help plan a busy week.",
        "interview_process": "A clear process makes it easier to fit interviews around classes.",
        "caregiving_and_leave": "Clear rules for time off around exams protect your studies.",
        "role_clarity": "Clear hours and duties make it easier to plan a term.",
        "inclusion_and_accommodation": "A stated route for flexible arrangements makes it easier to ask for them.",
    },
    "career_returners": {
        "schedule_flexibility": "Clear schedules help rebuild a routine after a break.",
        "remote_policy": "Remote options can ease a return while confidence builds.",
        "communication_style": "Clear written expectations make it easier to find your footing.",
        "pace_and_pressure": "A realistic pace gives room to relearn skills without rushing.",
        "work_environment": "A supportive team setting makes a return easier.",
        "interview_process": "A structured interview lets you show current skills clearly.",
        "caregiving_and_leave": "Clear leave rules help plan around the first months back.",
        "role_clarity": "Clear success measures and a ramp-up plan help you see what good work looks like.",
        "inclusion_and_accommodation": "A stated route for returnship or support adjustments makes it easier to ask.",
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
