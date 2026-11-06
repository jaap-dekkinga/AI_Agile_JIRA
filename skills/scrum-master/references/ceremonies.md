# Ceremonies and the Scrum Master's checklist

The full practice, with the reasons behind each rule, is in
[`example-project/docs/agile-practices.md`](../../../example-project/docs/agile-practices.md).
This page is the short version the skill works from.

## Roles

| Role | Owns |
|---|---|
| **Product Owner** | Epics and stories, backlog order, value and acceptance. |
| **Scrum Master** | The ceremonies, impediments, backlog readiness, the dashboard and the weekly status. |
| **Team (Engineering)** | Estimates, the sprint commitment (by consensus), how the work is built. |

The skill supports the Scrum Master and the Product Owner. It never decides what goes into a
sprint, and never sets story points; it prepares the information and drafts the changes.

## Definition of Ready

A story is Ready when an engineer could start it tomorrow without asking anyone a question:

1. Written with the story template, in Jira (jira-first) or the roadmap (repo-first).
2. Acceptance criteria written, Given/When/Then.
3. Every open question has an owner and a recorded assumption.
4. Its dependencies are done, or stubbed.
5. Estimated at 8 points or fewer.
6. **INVEST rating is Good, or each TBD has an owner and a question.**

## Definition of Done

Reviewed and merged; tests cite the rules they prove; the demo runs; anything new found is
written down; the Jira issue is Done.

## The sprint (two weeks)

| When | Ceremony | What the skill does |
|---|---|---|
| Before day 1 | **Sprint planning** (1 h) | Runs `velocity_analyzer.py`; proposes a commitment at the 70% confidence forecast, less a 20% buffer for unplanned work; lists Ready stories in rank order up to that capacity; flags any story not Good on INVEST. |
| Daily | **Standup** (15 min) | Lists blockers by age; any blocker older than 2 days is escalated with an owner. |
| Around day 5 | **Backlog refinement** (1 h) | Runs `invest_check.py` on the top of the backlog; drafts rewrites for Low stories and questions for TBD ones; keeps at least one sprint of Ready points beyond the current sprint. |
| Day 10 | **Sprint review** (1 h) | Summarises done vs committed, scope added mid-sprint, milestone progress; refreshes the dashboard. |
| Day 10 | **Retrospective** (1 h) | Runs `sprint_health_scorer.py` and `retrospective_analyzer.py`; picks at most 3 new actions if fewer than 60% of last actions were completed; each action gets an owner and a measurable check. |
| Weekly (Friday) | **Status** | Runs the dashboard's weekly job and the exec briefing; publishes after the user confirms. |

## Capacity, in one line

capacity = average points Done over the last 3 sprints × share of team days available − 20% buffer.
With 6+ sprints of history, prefer the Monte Carlo forecast at 70% confidence.
