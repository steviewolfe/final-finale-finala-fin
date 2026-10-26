from between_the_lines.config import MAX_PROFILES_PER_RUN
from between_the_lines.explain import CATEGORY_WHY, TAG_WHY
from between_the_lines.profiles import DEFAULT_COMPARE, PROFILES, TOPIC_HINTS
from between_the_lines.schemas import CATEGORIES, TAGS, Evidence


def test_nine_categories_including_inclusion():
    assert len(CATEGORIES) == 9
    assert CATEGORIES[-1] == "inclusion_and_accommodation"


def test_new_tags_are_defined_and_explained():
    for tag in ("accommodation_stated", "equal_opportunity_stated", "mandatory_social_events"):
        assert tag in TAGS
        assert TAG_WHY[tag].strip()


def test_eight_profiles_each_cover_all_categories():
    assert len(PROFILES) == 8
    for pid, p in PROFILES.items():
        assert set(p["weights"]) == set(CATEGORIES), pid
        assert set(CATEGORY_WHY[pid]) == set(CATEGORIES), pid


def test_default_compare_is_the_original_four_and_within_the_cap():
    assert DEFAULT_COMPARE == ["parent", "neurodivergent", "chronic_illness", "eldercare"]
    assert len(DEFAULT_COMPARE) <= MAX_PROFILES_PER_RUN == 4


def test_evidence_accepts_the_new_category_and_rejects_unknown():
    Evidence(category="inclusion_and_accommodation", exact_quote="x", signal="positive", tags=[], note="n")
    try:
        Evidence(category="made_up", exact_quote="x", signal="positive", tags=[], note="n")
    except Exception:
        return
    raise AssertionError("unknown category was accepted")


def test_every_category_has_a_topic_hint():
    assert set(TOPIC_HINTS) == set(CATEGORIES)
