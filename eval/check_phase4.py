"""Phase 4 check: guard deliberately leaky questions against private notes."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from between_the_lines.llm import SessionBudget
from between_the_lines.privacy_guard import guard_questions
from between_the_lines.schemas import Question
from between_the_lines.usage import RunMeter

NOTES = "I have ADHD and two kids"
questions = [
    Question(category="communication_style", ask_who="recruiter",
             question="Does the company offer accommodations for employees with ADHD?", ),
    Question(category="caregiving_and_leave", ask_who="hiring_manager",
             question="How are short-notice absences handled when a parent needs to pick up their kids?"),
    Question(category="schedule_flexibility", ask_who="hiring_manager",
             question="How are working hours set, and how are schedule changes communicated?"),
    Question(category="pace_and_pressure", ask_who="hiring_manager",
             question="What does a typical week look like for someone in this role?"),
    Question(category="caregiving_and_leave", ask_who="recruiter",
             question="Does the team have a process for covering work when someone is out sick?"),
]
run = RunMeter("p4-check")
out = guard_questions(questions, NOTES, run=run, budget=SessionBudget(limit=60_000))
for q in out.questions:
    print(f"{q.index} {q.action:9} layer={q.layer or '-':7} fact={q.fact_type:8} -> {q.final!r}")
print("run tokens:", run.total_tokens, "calls:", run.calls)
print("no-notes run:")
out2 = guard_questions(questions[2:], "", run=RunMeter("p4-nonotes"), budget=SessionBudget(limit=60_000))
print("  calls for no-notes run should be 0; actions:", [q.action for q in out2.questions])
