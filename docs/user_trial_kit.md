# User trial kit: Between the Lines

Purpose: collect real evidence of time saved and quality of decisions, for the report's Impact section.
Do not invent results. Record exactly what happens.

## 1. Who to invite (aim for 3 people, one per profile if possible)
- Someone who is neurodivergent and has job-searched recently.
- A working parent or carer who has job-searched recently.
- Anyone who has read job postings and wondered what they really meant.

Ask each person first. Do not use anyone who has not agreed.

## 2. Consent script (read aloud or send in writing)
"This is a class project. I'd like you to try a job-posting tool for about 15 minutes.
I'll time how long you take to decide whether a posting fits, with and without it.
I'll write down what you say. You can stop at any time. Your name will not be used
unless you say so, and you can choose whether to be quoted. Your private notes stay on
this computer and are not saved."

Record: consent given (yes/no), name use (anonymous / first name / full name), quote use (yes/no).

## 3. Before-and-after timing (per posting)
1. Give the person one posting (use a sample, or a real one they are considering).
2. Without the app: ask them to decide "fits / unsure / does not fit" and say what they would
   need to ask the employer. Start the timer when they start, stop when they answer.
3. With the app: give them the app at http://localhost:8000 (or the hosted link). Same
   question. Start the timer at the first click, stop at their answer.
4. Record both times, both answers, and whether the answers changed.

Use two different postings, one per condition, or the same posting in both conditions
with a gap of at least a day. Say which you used.

## 4. Questionnaire (after both tasks)
Rate 1 (strongly disagree) to 5 (strongly agree):
1. The app helped me see what the posting actually says.
2. I trust the quotes it shows me.
3. The questions it drafted are ones I would ask.
4. I felt safe entering private notes.
5. I would use this before applying.

Open questions (write their words exactly):
- What was the most useful thing you saw?
- What confused you?
- What did you want that was missing?

## 5. What to record (evals/trial_log.csv)
One row per person per posting. Columns are in evals/trial_log.csv.

## 6. Putting it in the report
- Replace the Impact placeholders with: the number of people, median time without and with
  the app, how many changed their answer, and one quote each person agreed to.
- Report only what happened. Include small samples as small samples.
- Keep the consent record (not names) in your own files, not in the repo.

## 7. Ethics and privacy
- Do not collect names, health details, or employer names in the repo.
- If you record audio, delete it after transcribing.
- Do not show anyone else's private notes in a screenshot.
