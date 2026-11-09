---
description: Prepare the sprint retrospective from the improvement register and the sprint health
argument-hint: "[sprint data file or PROJECT_KEY]"
---
Use the "Sprint review and retrospective" workflow of the scrum-master skill for $ARGUMENTS. First, review the improvement register (`docs/continuous-improvement.local.md`): the items that are due, the overdue items, and the items without a measure or an owner. Use the `continuous-improvement` skill if it is available. Then run `scripts/analytics/sprint_health_scorer.py` and `scripts/analytics/retrospective_analyzer.py`, with the number of stories in each `*_points` field. Start with the weakest dimensions, and propose a format from `references/retro-formats.md`. After the meeting, propose each new action as a register item, with an owner, an experiment and a measure. At most three items are Active.
