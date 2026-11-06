---
name: scrum-master
description: >-
  Scrum Master assistant for a team's backlog in Jira. Use when the user asks to refine
  the backlog (also called grooming), write or improve epics and user stories, check stories against INVEST (rated Low,
  Good or TBD), prepare sprint planning or capacity, track sprints, velocity, blockers or
  milestones, run a retrospective, or update the team's status dashboard. Drafts and rates work,
  then writes to Jira only after the user approves a preview.
version: 0.1.0
license: MIT
---

# Scrum Master

Help a Scrum Master run the team's backlog and sprints, and help the Product Owner write epics and
stories that meet INVEST. Every write to Jira waits for the user's approval.

## Before anything else

1. **Find the Jira route** (details in `references/jira-access.md`): the Atlassian MCP if it is
   connected; else the read-only scripts in `tools/jira-dashboard/` with `JIRA_*` credentials;
   else offer demo mode (`JIRA_DEMO=1`). Say which route you are using.
2. **Find the mode:** **jira-first** (default: the PO works in Jira) or **repo-first** (stories live
   in `PROJECT_ROADMAP.md` and are mirrored to Jira). Ask once if the repository doesn't make it
   clear.
3. **Find the board:** the Jira project key, and the board id if sprints are involved.

## Hard rules

- **No write without approval.** Preview every create or change as a table (key, type, summary,
  fields old → new, parent, labels, sprint), ask once per batch, write only what was approved, and
  report each key with its link. Search for duplicates before creating.
- **Respect who decides.** Never set story points (the team estimates), change rank (the PO), or
  move issues into or out of a sprint (Engineering agrees at planning). Propose them; don't apply
  them.
- **TBD, not a guess.** When a story lacks the information to judge a criterion, rate it TBD and
  name the question and who should answer it.
- **Secrets stay secret.** Never print a token or `cat` a file that may hold one.
- **The dashboard has no access control.** Publish it only where the user says, after they confirm.

## Workflows

### Write an epic or a story (PO support)

1. Ask for, or infer from the conversation: the user or role, the need, the benefit, and the
   epic it belongs to.
2. Draft it with `references/story-template.md` (or `references/epic-template.md`), with
   Given/When/Then acceptance criteria and an explicit out-of-scope line.
3. Rate it: save the draft as JSON and run `scripts/invest_check.py <file>`. Review each rating
   against `references/invest-rubric.md` and correct any the heuristic got wrong, saying why.
4. Show the draft with its INVEST table. For Low criteria, propose the fix (often a split). For TBD,
   list the questions for the PO.
5. On approval, create the issue in Jira with the INVEST table at the end of the description,
   linked to its epic. Leave story points empty for the team.

### Refine the backlog

1. Pull the top of the backlog (default 15 items, in rank order): through the MCP with JQL
   `project = KEY AND statusCategory != Done AND issuetype in (Story, Task, Bug) ORDER BY rank`,
   or a Jira search export the user provides.
2. Run `scripts/invest_check.py` on them (`--format json` keeps the detail).
3. Report the mix (Good / TBD / Low) and the Ready points against one sprint of capacity. Then, per
   story: its rating, the weakest criteria, and a concrete rewrite, split or question.
4. Offer to add or update the INVEST table in each description, in one approved batch.

### Prepare sprint planning

1. Collect sprint history in the shape of `assets/sample_sprint_data.json`: from Jira (closed
   sprints and their completed points, through the MCP or the Agile API), or from the user.
2. Run `scripts/analytics/velocity_analyzer.py <file> --format text`. With fewer than 3 sprints,
   say so and use the team's judgement instead.
3. Capacity = the 70% forecast, scaled for days off, less a 20% buffer for unplanned work
   (`references/ceremonies.md`).
4. Propose Ready stories in rank order up to capacity, flagging any not Good on INVEST, any that
   depend on unfinished work, and any two that change the same area. Engineering decides; you
   propose.

### Sprint review and retrospective

- Review: done vs committed points, scope added mid-sprint, carry-over, and milestone progress.
- Retro: run `scripts/analytics/sprint_health_scorer.py` and
  `scripts/analytics/retrospective_analyzer.py` on the sprint data. Lead with the weakest health
  dimensions. If under 60% of last retro's actions were completed, suggest at most 3 new actions.
  Each action gets an owner and a measurable check. Formats are in `references/retro-formats.md`.

### Milestones

Milestones are Jira labels (`MS1`, `MS2` …) on epics or stories; a label on an epic counts all its
children. Define them in `tools/jira-dashboard/config.py` (`MILESTONES`) with their deliverable
text. Report each milestone's % complete and flag one whose stories are mostly rated Low or
TBD (read from the INVEST table in each description) as at risk.

### Weekly status and the dashboard

Run from `tools/jira-dashboard/` (see its `WEEKLY_RUNBOOK.md`):

```bash
python weekly.py              # pull Jira, lock the week, rebuild the dashboard and exec briefing
python weekly.py --no-lock    # stage as a draft and build a preview instead
JIRA_DEMO=1 python weekly.py  # the same on fictional demo data
```

Summarise what moved, what is At Risk or Off Track, and open blockers. Offer the exec briefing
(`exec-talk-script.md`). Publish the HTML only to the location the user names.

## Files

| Path | Use |
|---|---|
| `references/invest-rubric.md` | The Low / Good / TBD rubric, splitting patterns, examples |
| `references/story-template.md`, `references/epic-template.md` | Drafting shapes and Jira field mapping |
| `references/jira-access.md` | Route choice, modes, approval gate, field lookup |
| `references/ceremonies.md` | Roles, Definition of Ready (with INVEST), the sprint calendar |
| `references/velocity-forecasting-guide.md`, `references/retro-formats.md` | Forecasting and retro formats |
| `scripts/invest_check.py` | First-pass INVEST rating from story JSON or a Jira search export |
| `scripts/analytics/*.py` | Velocity forecast, sprint health score, retro analysis (third-party, MIT; see `NOTICE.md`) |
| `assets/sample_stories.json`, `assets/sample_sprint_data.json` | Input examples |
| `../../tools/jira-dashboard/` | Weekly Jira pull, locked snapshots, HTML dashboard, exec briefing |
