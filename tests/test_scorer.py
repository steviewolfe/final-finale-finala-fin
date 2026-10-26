import math

from between_the_lines.profiles import PROFILES, TOPIC_HINTS
from between_the_lines.schemas import CATEGORIES, Evidence
from between_the_lines.scorer import score_all, score_profile


def ev(cat, signal, tags=(), quote="q"):
    return Evidence(category=cat, exact_quote=quote, signal=signal, tags=list(tags), note="n")


def test_weights_sum_to_one_for_every_profile():
    for pid, p in PROFILES.items():
        assert set(p["weights"]) == set(CATEGORIES), pid
        assert math.isclose(sum(p["weights"].values()), 1.0, abs_tol=1e-9), pid


def test_scoring_is_deterministic():
    evidence = [ev("pace_and_pressure", "negative"), ev("role_clarity", "unclear")]
    a = score_all(evidence, list(PROFILES))
    b = score_all(list(reversed(evidence)), list(PROFILES))
    for pid in PROFILES:
        assert a[pid].overall == b[pid].overall
        assert a[pid].band == b[pid].band


def test_missing_categories_are_not_penalized():
    only_positive = [ev("remote_policy", "positive")]
    s = score_profile(only_positive, "parent")
    assert s.categories["schedule_flexibility"].score is None
    assert s.overall == 100.0          # only the scored category counts
    assert s.coverage == PROFILES["parent"]["weights"]["remote_policy"]


def test_no_evidence_gives_no_overall_score():
    s = score_profile([], "eldercare")
    assert s.overall is None
    assert s.coverage == 0
    assert s.band == "Not enough evidence"


def test_tag_override_replaces_signal_and_lowest_wins():
    # parent: on_call override is 10, travel_required is 15; the lowest wins.
    s = score_profile([ev("schedule_flexibility", "positive", ["on_call", "travel_required"])], "parent")
    assert s.categories["schedule_flexibility"].score == 10


def test_red_flag_needs_weight_and_low_score():
    s = score_profile([ev("caregiving_and_leave", "negative")], "eldercare")
    assert s.categories["caregiving_and_leave"].red_flag is True
    assert "caregiving_and_leave" in s.red_flags
    low_weight = score_profile([ev("interview_process", "negative")], "parent")
    assert low_weight.categories["interview_process"].red_flag is False


def test_bands():
    good = [ev("schedule_flexibility", "positive"), ev("caregiving_and_leave", "positive")]
    assert score_profile(good, "parent").band == "Good fit"
    # One category (about 18% coverage) is too thin for a verdict.
    assert score_profile([ev("remote_policy", "unclear")], "parent").band == "Limited evidence"
    assert score_profile([ev("remote_policy", "negative")], "parent").band == "Limited evidence"
    # With enough coverage the bands apply.
    mixed = [ev("schedule_flexibility", "unclear"), ev("caregiving_and_leave", "positive"),
             ev("pace_and_pressure", "unclear")]
    assert score_profile(mixed, "parent").band == "Mixed"  # about 66
    neg = [ev(c, "negative") for c in ["schedule_flexibility", "caregiving_and_leave", "pace_and_pressure"]]
    assert score_profile(neg, "parent").band == "Concern"


def test_topic_hints_cover_every_category():
    assert set(TOPIC_HINTS) == set(CATEGORIES)
