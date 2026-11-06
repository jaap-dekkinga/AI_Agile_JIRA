---
description: Prepare sprint planning — velocity forecast, capacity, and a proposed set of Ready stories
argument-hint: "[PROJECT_KEY] [days off this sprint]"
---
Use the scrum-master skill's "Prepare sprint planning" workflow for $ARGUMENTS. Gather sprint history, run `scripts/analytics/velocity_analyzer.py`, compute capacity (70% forecast, scaled for days off, less a 20% buffer), and propose Ready stories in rank order up to capacity, flagging INVEST and dependency risks. This is a proposal for Engineering to agree; do not change the sprint in Jira.
