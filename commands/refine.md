---
description: Refine the top of the Jira backlog against the Definition of Ready, and show the INVEST score of each story
argument-hint: "[PROJECT_KEY] [number of items, default 15]"
---
Use the "Refine the backlog" workflow of the scrum-master skill for $ARGUMENTS. Get the top items in rank order. Compare each one with the Definition of Ready, and run `scripts/invest_check.py`. Review the ratings. Report the number of Ready stories, compared with one sprint of capacity. For each story that is not Ready, give the conditions that it does not meet, its INVEST score, and a rewrite, a split or a question. The INVEST score is a tool, not a condition. Offer the updates of the INVEST tables as one batch. Write nothing to Jira until I approve the preview. Do not use story points.
