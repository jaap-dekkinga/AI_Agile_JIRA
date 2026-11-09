# Continuous improvement

This page is the register of the changes that the team tries in how it works. Each item has a
stable id, an owner, the experiment, the measure that shows if it worked, and the sprint whose
retrospective decides. We never renumber ids. A closed item keeps its row and its result. Thus
we can see what we tried and what we learned.

> Example content. These items belong to the fictional Harbor Claims Assistant team.

This page closes the loop that the [sprint retrospective](agile-practices.md#sprint-retrospective)
opens. The retrospective agrees on what to try. This register remembers it, and the next
retrospective decides if it worked. If an improvement is only in meeting notes or in the head of
one person, the team usually forgets it before the next sprint.

## How it works

1. Write an improvement here first, during or directly after the retrospective, in the pull
   request that records it. Anyone can also add an item between retrospectives.
2. At most three items are Trying at the same time. A fourth item waits as Proposed. If a team
   changes everything at the same time, it cannot tell which change helped.
3. Each item has a measure: a number or a sign that anyone can examine. "Standups feel better"
   is not a measure. "Standups end in 15 minutes on 8 of 10 days" is a measure.
4. Each retrospective starts here. For each item whose Review by is this sprint, the team
   adopts it, extends it once (by one sprint), or drops it. Then the team writes in the result.
5. An adopted item changes the method in the same pull request. This can be a line in
   [agile-practices.md](agile-practices.md), a row in the [working agreements](#working-agreements)
   on this page, or a line in [CLAUDE.md](../CLAUDE.md). After that, the change is how we work.
6. If an item needs build work, it becomes a roadmap story. The item names the story id
   (`S10-03`), and the story does the work. If an item needs a change to a Jira setting, it
   becomes a Jira Task in the CDD Framework epic, and the item names its key.

An item has one of four statuses: Proposed, Trying, Adopted or Dropped.

## Trying now

| Id | Improvement | Owner | Review by |
|---|---|---|---|
| [CI-004](#ci-004) | Groom to two sprints of Ready stories, not one | PM lead | Sprint 2026-11-23 |
| [CI-005](#ci-005) | Post blockers in the team channel when they start | Engineering | Sprint 2026-11-09 |

## All items

| Id | Improvement | Source | Owner | Status |
|---|---|---|---|---|
| [CI-001](#ci-001) | Demo from `main` only, never from a branch | Retro 2026-09-25 | Lead Architect | Adopted (2026-10-09) |
| [CI-002](#ci-002) | Split stories of more than 5 points before grooming, not during grooming | Retro 2026-09-25 | PM lead | Dropped (2026-10-23) |
| [CI-003](#ci-003) | Raise each proposed sprint change at the standup, not in a private chat | Retro 2026-10-09 | PM lead | Adopted (2026-10-23) |
| [CI-004](#ci-004) | Groom to two sprints of Ready stories, not one | Retro 2026-10-23 | PM lead | Trying |
| [CI-005](#ci-005) | Post blockers in the team channel when they start | Retro 2026-10-23 | Engineering | Trying |
| [CI-006](#ci-006) | Review the improvement items before the demo, when people are not tired | Retro 2026-11-06 | PM lead | Proposed |

Each item has a section with the same fields. To add an item, copy the last section and take the
next free id.

### CI-001

Demo from `main` only, never from a branch. Status: Adopted.

- Source: the retro of sprint 2026-09-14. Two demos showed work that changed later in review.
- Owner: Lead Architect
- Experiment: for two sprints, the team shows a story at the demo only after it is merged.
- Measure: no story changes behavior after its demo.
- Review by: sprint 2026-09-28
- Result: no exceptions in two sprints. Adopted as item 4 of the
  [Definition of Done](agile-practices.md#definition-of-done).

### CI-002

Split stories of more than 5 points before grooming, not during grooming. Status: Dropped.

- Source: the retro of sprint 2026-09-14. Grooming went over its hour two times.
- Owner: PM lead
- Experiment: before the session, the PM splits each story with an estimate of more than 5
  points.
- Measure: grooming ends in its hour.
- Review by: sprint 2026-10-12, extended once
- Result: dropped. Splits that the PM made without the engineers were often wrong, and the team
  did them again in the meeting. The limit of 8 points in the Definition of Ready does not
  change.

### CI-003

Raise each proposed sprint change at the standup, not in a private chat. Status: Adopted.

- Source: the retro of sprint 2026-09-28. After a private chat, a story went into the sprint
  in place of another story. Two engineers learned about it at the demo.
- Owner: PM lead
- Experiment: each proposed change to the sprint is raised at the standup. If it cannot wait,
  it is raised in the team channel.
- Measure: for two sprints, no change to the sprint in Jira without a proposal first.
- Review by: sprint 2026-10-12
- Result: no exceptions. Adopted in [Daily standup](agile-practices.md#daily-standup) and
  [Engineering decides the sprint](agile-practices.md#engineering-decides-the-sprint).

### CI-004

Groom to two sprints of Ready stories, not one. Status: Trying.

- Source: the retro of sprint 2026-10-12. The team had no more Ready work on day 8.
- Owner: PM lead
- Experiment: keep Ready story points equal to two sprints of capacity. Examine the number at
  each grooming session.
- Measure: for three sprints in a row, each engineer has Ready work until day 10.
- Review by: sprint 2026-11-23

### CI-005

Post blockers in the team channel when they start. Status: Trying.

- Source: the retro of sprint 2026-10-12. A blocker waited a full day for the next standup.
- Owner: Engineering
- Experiment: when a person is blocked for more than one hour, they post it in the team
  channel. The post says what they need and from whom.
- Measure: the median time from a new blocker to a huddle is less than four working hours.
- Review by: sprint 2026-11-09

### CI-006

Review the improvement items before the demo, when people are not tired. Status: Proposed.

- Source: the retro of sprint 2026-10-26.
- Owner: PM lead
- Experiment: not set yet. A Proposed item gets its experiment when it starts.
- Measure: not set yet.
- Review by: not set yet.

## Working agreements

This table lists the habits that the team adopted, each with the item that it came from. A
rejected AI proposal with a reason can also become an agreement here. The reason is often a
rule that nobody wrote down before.

| Agreement | From |
|---|---|
| The team shows a story at the demo only from `main`. | [CI-001](#ci-001) |
| Each proposed sprint change goes to the standup or the team channel first. | [CI-003](#ci-003) |

## With an AI assistant

With the [`continuous-improvement` skill](../.claude/skills/continuous-improvement/SKILL.md),
an AI assistant can keep this page current. You can ask it to add an item from your retrospective
notes, to review the register before a retrospective, or to close an item with its result. It
changes this file and leaves the change for review, like each other change to the context.
