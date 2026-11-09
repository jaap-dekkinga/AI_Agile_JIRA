# Continuous improvement

The register of changes the team is trying in how it works. Each item has a stable id, an
owner, the experiment, how we will know it worked, and the sprint whose retrospective decides.
Ids are never renumbered. A closed item keeps its row and its result, so we can see what we
tried and what we learned.

> **Example content.** These items belong to the fictional Harbor Claims Assistant team.

This page closes the loop that the [sprint retrospective](agile-practices.md#sprint-retrospective)
opens. The retrospective agrees what to try. This register remembers it, and the next
retrospective decides whether it worked. An improvement that only lives in meeting notes or in
someone's head is usually forgotten by the next sprint.

## How it works

1. **An improvement is written here first**, during or straight after the retrospective, in the
   pull request that records it. Anyone may also add one between retrospectives.
2. **At most three items are Trying at once.** A fourth waits as Proposed. A team that changes
   everything at once can't tell which change helped.
3. **Each item has a measure**: a number or a sign anyone can check. "Standups feel better" is
   not a measure. "Standups end within 15 minutes on 8 of 10 days" is.
4. **Every retrospective starts here.** Each item whose **Review by** is this sprint is
   adopted, extended once (one more sprint), or dropped, with its result written in.
5. **An adopted item changes the method in the same pull request**: a line in
   [agile-practices.md](agile-practices.md), the [working agreements](#working-agreements)
   below, or [CLAUDE.md](../CLAUDE.md). Then the change is simply how we work.
6. **An item that needs build work becomes a roadmap story.** The item names the story id
   (`S10-03`), and the story does the work. An item that needs a Jira setting changed becomes a
   Jira Task in the CDD Framework epic, and the item names its key.

**Status:** 💡 Proposed · 🧪 Trying · ✅ Adopted · ✖ Dropped.

## Trying now

| Id | Improvement | Owner | Review by |
|---|---|---|---|
| [CI-004](#ci-004) | Groom to two sprints of Ready stories, not one | PM lead | Sprint 2026-11-23 |
| [CI-005](#ci-005) | Post blockers in the team channel the moment they start | Engineering | Sprint 2026-11-09 |

## All items

| Id | Improvement | Source | Owner | Status |
|---|---|---|---|---|
| [CI-001](#ci-001) | Demo from `main` only, never from a branch | Retro 2026-09-25 | Lead Architect | ✅ Adopted (2026-10-09) |
| [CI-002](#ci-002) | Split stories over 5 points before grooming, not during | Retro 2026-09-25 | PM lead | ✖ Dropped (2026-10-23) |
| [CI-003](#ci-003) | Raise every proposed sprint change at standup, not in side chats | Retro 2026-10-09 | PM lead | ✅ Adopted (2026-10-23) |
| [CI-004](#ci-004) | Groom to two sprints of Ready stories, not one | Retro 2026-10-23 | PM lead | 🧪 Trying |
| [CI-005](#ci-005) | Post blockers in the team channel the moment they start | Retro 2026-10-23 | Engineering | 🧪 Trying |
| [CI-006](#ci-006) | Retro actions reviewed before the demo, while people are fresh | Retro 2026-11-06 | PM lead | 💡 Proposed |

Each item has a section with the same fields. Copy the last one to add a new item, and take the
next free id.

### CI-001

**Demo from `main` only, never from a branch.** ✅ Adopted

- **Source:** retro of sprint 2026-09-14. Two demos showed work that later changed in review.
- **Owner:** Lead Architect
- **Experiment:** for two sprints, a story is only demoed once it has merged.
- **Measure:** no demoed story changes behavior after the demo.
- **Review by:** sprint 2026-09-28
- **Result:** held for two sprints with no exceptions. Adopted as item 4 of the
  [Definition of Done](agile-practices.md#definition-of-done).

### CI-002

**Split stories over 5 points before grooming, not during.** ✖ Dropped

- **Source:** retro of sprint 2026-09-14. Grooming ran over the hour twice.
- **Owner:** PM lead
- **Experiment:** the PM splits any story estimated over 5 points before the session.
- **Measure:** grooming ends within its hour.
- **Review by:** sprint 2026-10-12, extended once
- **Result:** dropped. Splits made without the engineers were often wrong and were redone in
  the meeting. The 8-point limit in the Definition of Ready stays as it is.

### CI-003

**Raise every proposed sprint change at standup, not in side chats.** ✅ Adopted

- **Source:** retro of sprint 2026-09-28. A story was swapped into the sprint after a private
  chat, and two engineers learned about it at the demo.
- **Owner:** PM lead
- **Experiment:** every proposed change to the sprint is raised at standup, or in the team
  channel when it can't wait.
- **Measure:** no change to the sprint in Jira that wasn't raised first, for two sprints.
- **Review by:** sprint 2026-10-12
- **Result:** no exceptions. Adopted in [Daily standup](agile-practices.md#daily-standup) and
  [Engineering decides the sprint](agile-practices.md#engineering-decides-the-sprint).

### CI-004

**Groom to two sprints of Ready stories, not one.** 🧪 Trying

- **Source:** retro of sprint 2026-10-12. The team ran out of Ready work on day 8.
- **Owner:** PM lead
- **Experiment:** keep Ready story points at two sprints of capacity, checked at each grooming.
- **Measure:** nobody runs out of Ready work before day 10, for three sprints in a row.
- **Review by:** sprint 2026-11-23

### CI-005

**Post blockers in the team channel the moment they start.** 🧪 Trying

- **Source:** retro of sprint 2026-10-12. A blocker waited a full day for the next standup.
- **Owner:** Engineering
- **Experiment:** anyone blocked for more than an hour posts it, with what they need and from
  whom.
- **Measure:** the median time from a blocker raised to a huddle is under four working hours.
- **Review by:** sprint 2026-11-09

### CI-006

**Retro actions reviewed before the demo, while people are fresh.** 💡 Proposed

- **Source:** retro of sprint 2026-10-26.
- **Owner:** PM lead
- **Experiment:** not set yet. A Proposed item gets its experiment when it starts.
- **Measure:** not set yet.
- **Review by:** not set yet.

## Working agreements

Habits the team has adopted, each with the item that produced it. A rejected AI proposal with a
reason can also become one here: the reason is often a rule nobody had written down.

| Agreement | From |
|---|---|
| A story is demoed only from `main`. | [CI-001](#ci-001) |
| A proposed sprint change is raised at standup or in the team channel first. | [CI-003](#ci-003) |

## With an AI assistant

The [`continuous-improvement` skill](../.claude/skills/continuous-improvement/SKILL.md) lets an
AI assistant keep this page. Ask it to add an item from retrospective notes, to review the
register before a retrospective, or to close an item with its result. It edits this file and
leaves the change for review, like every other change to the context.
