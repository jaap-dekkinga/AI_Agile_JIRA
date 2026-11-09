# Automation & Margin Dashboard: Executive Brief (example)

*Status on 2 Nov 2026, from the Jira pull for the week ending 30 Oct.*

> Example content. The projects, figures and decisions on this page are fictional. They agree
> with the demo data in `seed_demo_db.py`. Use this page as a template to brief leadership on
> the dashboard itself: what it measures, how it measures, and what you need from them.

## In one paragraph

The Automation & Margin dashboard now reads its numbers directly from Jira, without manual data
entry. Three changes make it a more reliable picture of the state of delivery. First, Jira
labels track the milestones, so each milestone has its own progress figure. Second, "% complete"
now gives partial credit for work in progress, not only for finished work. Third, the "Steps to
target" line now names the work that is closest to done, or the sprint goal of the team. The
pull is automatic and can run each weekday. The shared dashboard still moves forward once a
week, when somebody signs off the numbers of that week.

---

## 1. Where the portfolio stands

| Project | % complete | vs plan | Week-on-week | Status |
|---|---:|---:|---:|---|
| Claims Follow-Up Automation | 93.0% | +13.0 | +13.3 | On Track |
| Payer Policy Search | 91.5% | +6.5 | +0.7 | On Track |
| Data Platform Foundation | 47.2% | +2.2 | +3.7 | On Track |
| Intake Document Classification | 53.4% | −6.6 | +3.0 | At Risk |
| Operator Workbench | 35.5% | −19.5 | +2.1 | Off Track |

- Claims Follow-Up Automation made the most progress this week.
- Operator Workbench needs a decision. Two engineers moved to incident work, and velocity is
  lower for two sprints. Either the target date moves, or new people join the team.
- The three projects that people track by hand (Prior-Auth Assistant, Long-Term Care
  Onboarding, Practice System Integrations) have no Jira board yet. Their teams report their
  own figures.
- The portfolio has 6 open blockers.

---

## 2. Daily updates from Jira

How it works today: a scheduled job reads each active Jira board and records the result in the
database of the dashboard. Nobody must type anything. The job only reads from Jira. It never
changes anything there.

| Stage | What happens | Who sees it |
|---|---|---|
| Draft | The job pulls the numbers of the week from Jira. It can pull them again as many times as necessary. Each new pull replaces the pull before it. | Review copy only |
| Locked | Somebody signs off the week, and it is frozen as a permanent snapshot. Nothing calculates it again after that. | Everyone, on the shared dashboard |

Why the shared dashboard stays weekly: leaders act on the change from week to week. For this
comparison, the figure of last week must be a fixed point. If the published numbers move each
day, it is not fixed. Daily pulls give the team new numbers to work from, and the weekly lock keeps the
history true.

One condition before more people see it: the dashboard is a single file that holds all project
data and has no login of its own. To host it as a website, you need a host with access control.

---

## 3. Tracking milestones with Jira labels

Each milestone is a Jira label (for Data Platform Foundation, `MS1`–`MS4`). Each work item with
the label counts toward that milestone. The dashboard shows a separate progress figure for each
milestone, next to the plain-English deliverable that it stands for. When you put a label on an
epic, all items under the epic count.

Two design choices keep the figures correct:

- "Not labelled yet" is not the same as "0%". If no Jira item has the label of a milestone, the
  dashboard says so. It does not show 0%.
- The dashboard measures milestones in the same way as the project, from the same items and
  rules. Thus you can compare the two directly.

Recommendation: ask each team to put labels on its next two or three milestones. Then the
portfolio has the same early warning for each team.

---

## 4. How "% complete" is calculated

% complete is weighted by effort. Each work item counts in proportion to its story points. Work
in progress gets part of its effort:

| Jira status | Credit |
|---|---:|
| Done (and other completed states) | 100% |
| In Review | 75% |
| In Progress | 50% |
| Not started, Blocked, In QA | 0% |

Boards that do not estimate effort count the finished items. Thus they do not show 0%.

Remember these three points:

1. A change to the rule causes a single step in the trend. The dashboard does not calculate the
   earlier weeks again, because Jira does not keep the status history that is necessary for
   this.
2. The statuses that Jira classes as completed count as 100%. This can include "Won't Do", or
   work that waits for acceptance testing. Decide on purpose if this is what you want.
3. The credit levels are a reporting convention, not a measurement. They are coarse on purpose.
   Nobody changes them to make the status of a project look better.

---

## 5. Decisions requested

1. Operator Workbench: move the target date, or add people to the team.
2. Milestone labels: ask each team to put labels on its next milestones in Jira.
3. Sprint goals: ask each team to fill in the sprint goal field. The dashboard uses it directly.
4. Hosting: choose a host with access control before the dashboard is published as a website.
