from between_the_lines.explain import CATEGORY_WHY, SIGNAL_WHY, TAG_WHY, tag_why
from between_the_lines.profiles import PROFILES
from between_the_lines.schemas import CATEGORIES, TAGS


def test_every_tag_has_an_explanation():
    assert set(TAG_WHY) == set(TAGS)
    assert all(TAG_WHY[t].strip() for t in TAGS)


def test_every_profile_category_pair_has_text():
    for pid in PROFILES:
        assert set(CATEGORY_WHY[pid]) == set(CATEGORIES), pid
        assert all(CATEGORY_WHY[pid][c].strip() for c in CATEGORIES)


def test_category_text_is_short():
    for pid in CATEGORY_WHY:
        for cat, text in CATEGORY_WHY[pid].items():
            assert len(text.split()) <= 16, (pid, cat, text)


def test_tag_why_falls_back_to_signal():
    assert tag_why([], "negative") == SIGNAL_WHY["negative"]
    assert tag_why(["on_call"], "positive") == TAG_WHY["on_call"]
