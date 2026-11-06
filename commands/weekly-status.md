---
description: Run the weekly Jira pull, rebuild the status dashboard and exec briefing, and summarise what moved
argument-hint: "[week-ending date YYYY-MM-DD] [--no-lock] [--demo]"
---
Use the scrum-master skill's "Weekly status and the dashboard" workflow for $ARGUMENTS. Run `tools/jira-dashboard/weekly.py` (with `JIRA_DEMO=1` if I said --demo), then summarise movers, At Risk and Off Track projects, milestones and open blockers. Ask before publishing the HTML, and publish only to the location I name.
