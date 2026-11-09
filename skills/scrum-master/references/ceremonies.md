# Ceremonies and the checklist of the Scrum Master

[`example-project/docs/agile-practices.md`](../../../example-project/docs/agile-practices.md)
gives the full practice, with the reason for each rule. This page is the short version that the
skill uses.

## Roles

| Role | Owns |
|---|---|
| Product Owner | Epics and stories, the backlog order, value and acceptance |
| Scrum Master | The meetings, impediments, backlog readiness, the dashboard, the weekly status and the improvement register |
| Team (Engineering) | The size of each story (one sprint or less), the sprint commitment (by consensus) and how the work is built |

The skill supports the Scrum Master and the Product Owner. It never decides what a sprint
includes. It gets the information ready and writes drafts of the changes.

## #NoEstimates

The team does not use story points. It makes each story small enough to complete in one
sprint, and counts stories. Throughput is the number of stories Done in a sprint.

## Definition of Ready

A story is Ready when all of these conditions are true:

- [ ] The title is clear.
- [ ] The value for the user is explicit.
- [ ] The acceptance criteria are written and detailed.
- [ ] The team can complete the story in one sprint.
- [ ] The dependencies are listed.
- [ ] No blocker stops the story, and each dependency is unblocked.

The INVEST score is not a condition. Refinement shows it as a tool. A low score is a topic for
the conversation, not a reason to stop a story.

## Definition of Done

The story is reviewed and merged. Its tests cite the rules that they prove. The demo operates.
Each new thing that the team found is written down. The Jira item is Done.

## The sprint (two weeks)

| When | Meeting | What the skill does |
|---|---|---|
| Before day 1 | Sprint planning (1 hour) | Calculates the capacity with the 80/20 rule. Lists Ready stories in rank order, up to the capacity. Marks each story that does not meet the Definition of Ready. |
| Each day | Standup (15 minutes) | Lists blockers by age. Escalates each blocker that is older than one working day and has no owner. |
| At about day 5 | Backlog refinement (1 hour) | Compares the top of the backlog with the Definition of Ready, and shows the INVEST score of each story. Writes rewrites, splits and questions. Keeps Ready stories for one more sprint than the current sprint. |
| Day 10 | Sprint review (1 hour) | Gives the stories Done compared with the commitment, the stories added during the sprint, and the progress of the milestones. Updates the dashboard. |
| Day 10 | Retrospective (1 hour) | Starts with the improvement register. Starts `sprint_health_scorer.py` and `retrospective_analyzer.py`. Proposes new register items, each with an owner, an experiment and a measure. At most three items are Active. |
| Weekly (Monday) | Scrum Master report | Board hygiene, burndown, throughput, improvements and blockers (routine 1 in `tools/ai-scrum-master/README.md`). |
| Weekly (Friday) | Status | Starts the weekly job of the dashboard and the executive briefing. Publishes them after the user agrees. |

## Capacity: the 80/20 rule

capacity = the average number of stories Done in the last three sprints × the part of the team
days that are available × 80%.

The other 20% is for unplanned work: urgent bugs, outages and client requests outside the plan.
