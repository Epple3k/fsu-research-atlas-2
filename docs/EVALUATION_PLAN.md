# FSU Research Explorer — usability and trust evaluation

## Purpose

Test whether visible, interactive provenance helps people verify and explain AI-supported claims about a complex research dataset.

This is a small formative product evaluation for a portfolio case study. It is not designed to support generalizable academic claims. If the work becomes formal research, coursework requiring human-subjects approval or a publication, confirm the appropriate institutional review process before recruiting.

## Research questions

1. Does inline access to source papers change whether participants verify a claim?
2. Does it improve the accuracy of their explanation?
3. Does it change confidence or trust?
4. Where does the question → claim → network → evidence workflow break down?

## Participants

Recruit 6–8 adults.

Aim for:

- 2–3 people who have searched scholarly literature before: faculty, graduate students, research assistants, librarians or research staff.
- 3–5 people comfortable reading a data interface but without specialist research-administration experience.

Record relevant background, not unnecessary personal information.

## Conditions

### A — Claim-only control

URL: https://epple3k.github.io/fsu-research-atlas-2/?study=control

Participants can read claims and see the highlighted network relationship. Paper-level evidence is unavailable.

### B — Evidence-first interface

URL: https://epple3k.github.io/fsu-research-atlas-2/?study=full

Participants can select claims, see the highlighted relationship and inspect paper-level evidence.

## Study design

Use a within-subject, counterbalanced comparison so every participant sees both conditions while reducing order bias.

| Participant | First | Second |
|---|---|---|
| 1 | A with Task 1 | B with Task 2 |
| 2 | B with Task 2 | A with Task 1 |
| 3 | A with Task 2 | B with Task 1 |
| 4 | B with Task 1 | A with Task 2 |
| 5 | Repeat row 1 | Repeat row 1 |
| 6 | Repeat row 2 | Repeat row 2 |
| 7–8 | Continue alternating | Continue alternating |

Do not let a participant repeat the same task in both conditions. The specific answer learned in the first condition would contaminate the second.

## Matched tasks

### Task 1 — growth

“Using this tool, identify one pair of research areas whose collaboration appears to have grown since 2022. Explain what the claim means and tell me what, if anything, makes you trust it.”

### Task 2 — strongest connection

“Using this tool, identify one of the strongest cross-field research connections at FSU. Explain what the claim means and tell me what, if anything, makes you trust it.”

Optional third qualitative task after both conditions:

“Find one thing in this interface you would want to verify before using it in a real decision.”

## Moderator script

### Opening

“Thanks for helping me test a prototype. I am testing the interface, not you. Some parts may be confusing or incomplete. Please think aloud: say what you expect, what you notice and what you are trying to do. I will mostly stay quiet until the task ends.”

“I would like to take notes about your actions and comments. I will not include your name in the case study. Is that okay?”

Do not record audio or video unless the participant gives explicit permission.

### Before each task

- Open the assigned URL in a fresh private/incognito window.
- Confirm the intended condition loaded.
- Read the task exactly as written.
- Start the timer.
- Do not explain the graph, claims or evidence interaction.
- If the participant asks for help, respond once with: “What would you expect to do?”
- If they remain blocked for 60 seconds, record the blockage and end the task.

### After each task

Ask:

1. “What answer did you reach?”
2. “How confident are you that your answer is correct, from 1 to 5?”
3. “How much do you trust the conclusion shown by the interface, from 1 to 5?”
4. “What specifically increased or decreased that trust?”
5. “What did you think would happen when you selected a claim?”
6. “What was the most confusing moment?”

### Closing

“Which version would you use for a real investigation, and why?”

“What information was still missing?”

“If you could change one thing, what would it be?”

## Metrics

| Measure | How to record |
|---|---|
| Task completion | Yes / No / With moderator help |
| Correct relationship | Exact field pair participant reports |
| Explanation accuracy | 0 = incorrect, 1 = partly correct, 2 = correct in their own words |
| Time on task | Seconds from task start to final answer |
| Confidence | Participant rating, 1–5 |
| Trust | Participant rating, 1–5 |
| Evidence-seeking attempt | Yes / No; include attempted action |
| Source opened | Yes / No |
| Hesitations | Timestamp and visible behavior |
| Quote | Short exact phrase, with permission |

### Accuracy rubric

- **0 — Incorrect:** identifies the wrong relationship or misstates what the number represents.
- **1 — Partial:** identifies a valid relationship but cannot explain the metric or time comparison.
- **2 — Correct:** identifies a valid relationship and accurately explains what the count or change means.

## Analysis

For this sample size, report counts, medians and ranges. Do not imply statistical significance.

Useful comparisons:

- number who attempted evidence inspection in A versus B;
- number who opened at least one paper in B;
- median explanation score by condition;
- median task time by condition;
- median trust and confidence by condition;
- recurring hesitation points;
- the most consequential usability failure.

Treat higher trust carefully. The goal is calibrated trust supported by verification and accurate explanation, not maximum trust.

## Decision rules for iteration

Revise the interface if any of the following occurs:

- 2 or more participants do not realize claims are selectable.
- 2 or more cannot connect a selected claim to the highlighted network relationship.
- 2 or more interpret “since 2022” as a continuous annual growth rate.
- participants open papers but cannot tell why those papers support the claim.
- the control condition is judged more trustworthy solely because it looks simpler.
- evidence visibility raises trust while explanation accuracy stays flat or declines.

## What to publish in the case study

After testing, report:

1. participant count and relevant background;
2. study setup and counterbalancing;
3. exact tasks;
4. observed behaviors and metric summaries;
5. one or two representative quotes;
6. what changed in the interface as a direct result;
7. limitations.

Do not publish participant names, contact details, raw recordings or exaggerated claims.
