# Automation & Margin Dashboard — Executive Brief (example)

*Status as of 2 Nov 2026, from the Jira pull for the week ending 30 Oct.*

> **Example content.** The projects, figures and decisions below are fictional and match the
> demo data in `seed_demo_db.py`. Use this as a template for briefing leadership on the
> dashboard itself: what it measures, how, and what you need from them.

## In one paragraph

The Automation & Margin dashboard now reads its numbers straight from Jira, with no manual
data entry. Three changes make it a more reliable picture of where delivery stands.
**Milestones are tracked by Jira label**, so each milestone has its own progress figure.
**"% complete" now gives partial credit** for work that is under way, not only for finished
work. **The "Steps to target" line** now names the work closest to done, or the team's own
sprint goal. The pull is automated and can run every weekday. The shared dashboard still
moves forward once a week, when that week's numbers are signed off.

---

## 1. Where the portfolio stands

| Project | % complete | vs plan | Week-on-week | Status |
|---|---:|---:|---:|---|
| Claims Follow-Up Automation | 93.0% | +13.0 | +13.3 | On Track |
| Payer Policy Search | 91.5% | +6.5 | +0.7 | On Track |
| Data Platform Foundation | 47.2% | +2.2 | +3.7 | On Track |
| Intake Document Classification | 53.4% | −6.6 | +3.0 | At Risk |
| Operator Workbench | 35.5% | −19.5 | +2.1 | **Off Track** |

- **Claims Follow-Up Automation** made the most progress this week.
- **Operator Workbench** needs a decision. Two engineers were reassigned to incident work
  and velocity is down for two sprints. Either the target date moves or the team is
  backfilled.
- The three **manually tracked projects** (Prior-Auth Assistant, Long-Term Care Onboarding,
  Practice System Integrations) have no Jira board yet, so their figures are self-reported.
- There are 6 open blockers across the portfolio.

---

## 2. Daily updates from Jira

**How it works today.** A scheduled job reads every active Jira board and records the result
in the dashboard's database. Nobody has to type anything in. The job only reads from Jira and
never changes anything there.

| Stage | What happens | Who sees it |
|---|---|---|
| **Draft** | The week's numbers are pulled from Jira and can be re-pulled any number of times. Each re-pull replaces the previous one. | Review copy only |
| **Locked** | The week is signed off and frozen as a permanent snapshot. It is never recalculated afterwards. | Everyone, on the shared dashboard |

**Why the shared dashboard stays weekly.** Week-on-week change is the trend leaders act on. If
published numbers moved every day, last week's figure would no longer be a fixed point to
compare against. Daily pulls give the team fresh numbers to work from, and the weekly lock
keeps the history honest.

**One prerequisite before wider sharing.** The dashboard is a single file that contains all
project data and has no login of its own. Hosting it as a website needs an access-controlled
host.

---

## 3. Tracking milestones with Jira labels

Each milestone is a Jira label (for Data Platform Foundation, `MS1`–`MS4`). Any work item
carrying the label counts toward that milestone, and the dashboard shows a separate progress
figure for each one, next to the plain-English deliverable it stands for. Labelling an **epic**
brings in **every item underneath it**.

Two design choices protect the reading:

- **"Not labelled yet" is not the same as "0%".** If no Jira item carries a milestone's label,
  the dashboard says so instead of showing 0%.
- **Milestones are measured the same way as the project**, from the same items and rules, so
  the two can be compared directly.

**Recommendation.** Ask each team to label its next two or three milestones, for the same
early-warning view across the portfolio.

---

## 4. How "% complete" is calculated

% complete is weighted by effort: each work item counts in proportion to its story points.
Work under way earns part of its effort:

| Jira status | Credit |
|---|---:|
| Done (and other completed states) | 100% |
| In Review | 75% |
| In Progress | 50% |
| Not started, Blocked, In QA | 0% |

Boards that don't estimate effort fall back to counting finished items, so they don't read 0%.

Three things to keep in mind:

1. **Changing the rule creates a one-time step** in the trend. Earlier weeks are not restated,
   because Jira does not keep the status history needed to recalculate them.
2. **Statuses Jira classes as completed count as 100%**, which can include "Won't Do" or work
   awaiting acceptance testing. Decide deliberately whether that is what you want.
3. **The credit levels are a reporting convention, not a measurement.** They are kept coarse on
   purpose and are not adjusted to improve any project's status.

---

## 5. Decisions requested

1. **Operator Workbench.** Move the target date or backfill the team.
2. **Milestone labels.** Ask every team to label its upcoming milestones in Jira.
3. **Sprint goals.** Ask every team to fill in the sprint goal field. It feeds the dashboard
   directly.
4. **Hosting.** Choose an access-controlled host before the dashboard is published as a website.
