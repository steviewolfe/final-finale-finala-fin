import between_the_lines.privacy_guard as pg
from between_the_lines.llm import SessionBudget
from between_the_lines.privacy_lexicon import lexicon_hits, redact
from between_the_lines.profiles import TOPIC_HINTS
from between_the_lines.schemas import Question
from between_the_lines.usage import RunMeter


def q(text, cat="role_clarity"):
    return Question(category=cat, question=text, ask_who="recruiter")


def test_lexicon_catches_sensitive_terms():
    assert lexicon_hits("Does the company support employees with ADHD?")
    assert lexicon_hits("How do you handle pickup for kids after school?")
    assert lexicon_hits("What is the leave policy for a diagnosis?")
    assert not lexicon_hits("How are working hours set for this team?")


def test_note_terms_are_matched_from_user_notes():
    hits = lexicon_hits("What is the process for vendor reviews?", extra_terms={"vendor"})
    assert hits == ["vendor"]


def test_redact_removes_sensitive_words():
    out = redact("Support for ADHD and two kids?", {"adhd"})
    assert "ADHD" not in out and "kids" not in out


def test_topic_hints_contain_no_sensitive_terms():
    for cat, hint in TOPIC_HINTS.items():
        assert lexicon_hits(hint) == [], f"{cat} hint is not condition-free: {hint}"


def test_no_notes_means_no_llm_call(monkeypatch):
    def boom(**kwargs):
        raise AssertionError("LLM must not be called without notes")
    monkeypatch.setattr(pg, "call_llm", boom)
    out = pg.guard_questions([q("How are hours set?")], "", run=RunMeter("t1"),
                             budget=SessionBudget(limit=10_000))
    assert [x.action for x in out.questions] == ["kept"]


def test_rewrite_that_reintroduces_a_note_term_is_dropped(monkeypatch, tmp_path):
    monkeypatch.setattr(pg, "PRIVACY_LOG", tmp_path / "privacy_log.csv")
    fake = {"results": [{"id": 0, "verdict": "leaks", "fact_type": "diagnosis",
                         "rewrite": "Is there support for ADHD here?"}]}
    monkeypatch.setattr(pg, "call_llm", lambda **kw: fake)
    out = pg.guard_questions([q("Do you support ADHD?")], "I have ADHD",
                             run=RunMeter("t2"), budget=SessionBudget(limit=10_000))
    assert out.questions[0].action == "blocked"
    assert out.safe == []
    log = (tmp_path / "privacy_log.csv").read_text()
    assert "blocked" in log and "ADHD" not in log


def test_safe_rewrite_is_used_and_logged(monkeypatch, tmp_path):
    monkeypatch.setattr(pg, "PRIVACY_LOG", tmp_path / "privacy_log.csv")
    fake = {"results": [{"id": 0, "verdict": "infers", "fact_type": "children",
                         "rewrite": "How does the team handle short-notice absences?"}]}
    monkeypatch.setattr(pg, "call_llm", lambda **kw: fake)
    out = pg.guard_questions([q("Who covers when a parent leaves early for pickup?")],
                             "two kids", run=RunMeter("t3"), budget=SessionBudget(limit=10_000))
    assert out.safe[0].final == "How does the team handle short-notice absences?"
    assert out.count("rewritten") == 1
