---
description: Groom the top of the Jira backlog and rate each story on INVEST (Low / Good / TBD)
argument-hint: "[PROJECT_KEY] [number of items, default 15]"
---
Use the scrum-master skill's "Groom the backlog" workflow for $ARGUMENTS. Pull the top items in rank order, run `scripts/invest_check.py`, review the ratings, and report the Good / TBD / Low mix, the Ready points, and a rewrite, split or question for each story that is not Good. Offer the label and description updates as one batch, and write nothing to Jira until I approve the preview.
