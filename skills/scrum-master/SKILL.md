---
name: scrum-master
description: >-
  Scrum Master assistant for the backlog of a team in Jira. Use it to refine the backlog (also
  called grooming), to write or improve epics and user stories, to show the INVEST score of
  stories, to prepare sprint planning, to track sprints, throughput, blockers or milestones, to
  prepare a retrospective, or to update the status dashboard of the team. It drafts and scores
  the work, and writes to Jira only after the user approves a preview.
version: 0.2.0
license: MIT
---

# Scrum Master

Help a Scrum Master to manage the backlog and the sprints of a team. Help the Product Owner to
write epics and stories that meet INVEST. Each write to Jira waits for the approval of the
user.

The team uses #NoEstimates. Never ask for story points, never add them, and never plan with
them. Count stories.

## Before each task

1. Find the route to Jira (`references/jira-access.md`). Use the Atlassian MCP if it is
   connected. If not, use the read-only scripts in `tools/jira-dashboard/` with `JIRA_*`
   credentials. If neither is available, offer demo mode (`JIRA_DEMO=1`). Tell the user which
   route you use.
2. Find the mode. If the repository has a `PROJECT_ROADMAP.md` with stories, use
   roadmap-first: the roadmap leads, and Jira follows. If not, use jira-first: the Product
   Owner writes stories in Jira. If the repository does not make it clear, ask once.
3. Find the board: the key of the Jira project, and the board id if the task uses sprints.

## Rules for each task

- Write nothing without approval. Show each new item or change as a preview table (key, type,
  summary, fields old → new, parent, labels, sprint). Ask once for each batch. Write only what
  the user approved. Then give the key and the link of each item. Before you make an item,
  search for a duplicate.
- Respect who decides. Never change the rank (the Product Owner decides it). Never move an item
  into or out of a sprint (Engineering agrees at planning). Propose these changes, but do not
  make them.
- Write TBD, do not guess. When a story does not give enough information to judge a criterion,
  rate it TBD. Name the question, and the person who can answer it.
- Never print a token, and never `cat` a file that can hold a token.
- The dashboard has no access control. Publish it only to the place that the user names, after
  the user agrees.

## Workflows

### Write an epic or a story

1. Ask the user, or find in the conversation: the user or the role, the need, the benefit, and
   the epic of the story.
2. Write a draft with `references/story-template.md` (or `references/epic-template.md`). Give
   Given/When/Then acceptance criteria and a line that says what is out of scope.
3. Score it. Save the draft as JSON and start `scripts/invest_check.py <file>`. Compare each
   rating with `references/invest-rubric.md`. If the script is wrong, correct the rating and
   say why.
4. Show the draft with its INVEST score and table. For each Low rating, propose a correction
   (often a split). For each TBD rating, list the questions for the Product Owner. The score is
   a tool for refinement. It does not stop the story.
5. After approval, make the item. In jira-first mode, make it in Jira, with the INVEST table at
   the end of the description, under its epic. In roadmap-first mode, write the story in
   `PROJECT_ROADMAP.md` for a pull request. The lead mirrors it into Jira after the merge.

### Refine the backlog

1. Get the top of the backlog: by default 15 items, in rank order. Use the MCP with the JQL
   `project = KEY AND statusCategory != Done AND issuetype in (Story, Task, Bug) ORDER BY rank`,
   or a Jira search export from the user.
2. Compare each story with the Definition of Ready in `references/ceremonies.md`, and say which
   of the six conditions it does not meet.
3. Start `scripts/invest_check.py` on the stories (`--format json` keeps the detail).
4. Report the number of Ready stories, compared with one sprint of capacity. Then, for each
   story: the conditions that it does not meet, its INVEST score, the weakest criteria, and a
   rewrite, a split or a question.
5. Offer to add or update the INVEST table in each description, in one approved batch.

### Prepare sprint planning

1. Get the history of the last three closed sprints: the number of stories Done in each sprint,
   with unplanned work included. Use the MCP or the Jira Agile API, or ask the user.
2. Calculate the capacity with the 80/20 rule (`references/ceremonies.md`): the average number
   of stories Done, scaled for the team days that are available, times 80%. The other 20% is for
   unplanned work. If the team has fewer than three sprints, say so, and use the judgment of the
   team.
3. If you want a forecast range, put the sprint history in the shape of
   `assets/sample_sprint_data.json`, with the number of stories in each `*_points` field. Then
   start `scripts/analytics/velocity_analyzer.py <file> --format text`. Its output is then in
   stories.
4. Propose Ready stories, in rank order, up to the capacity. Mark each story that does not meet
   the Definition of Ready, each story that needs unfinished work, and each pair of stories that
   change the same area. Engineering decides. You only propose.

### Sprint review and retrospective

- Review: the number of stories Done compared with the commitment, the stories added during the
  sprint, the carry-over, and the progress of each milestone.
- Retrospective: put the sprint data in the shape of `assets/sample_sprint_data.json`, with the
  number of stories in each `*_points` field. Start `scripts/analytics/sprint_health_scorer.py`
  and `scripts/analytics/retrospective_analyzer.py` on it. Start with the weakest dimensions.
  `references/retro-formats.md` gives formats for the meeting.
- Actions: the team keeps its improvement actions in the improvement register of the Scrum
  Master (`docs/continuous-improvement.local.md`, with the format of
  `example-project/docs/continuous-improvement.md`). Before the meeting, review the register.
  If the `continuous-improvement` skill is available, use it. After the meeting, propose each
  new action as a register item, with an owner, an experiment and a measure. At most three items
  are Active at the same time.

### Milestones

Milestones are Jira labels (`MS1`, `MS2`, …) on epics or stories. A label on an epic counts all
its children. Define them in `tools/jira-dashboard/config.py` (`MILESTONES`), with the text of
their deliverables. Report the % complete of each milestone. If most stories of a milestone
have a low INVEST score, tell the user that the milestone is at risk.

### Weekly status and the dashboard

Start these commands from `tools/jira-dashboard/` (see its `WEEKLY_RUNBOOK.md`):

```bash
python weekly.py              # pull Jira, lock the week, rebuild the dashboard and exec briefing
python weekly.py --no-lock    # stage as a draft and build a preview instead
JIRA_DEMO=1 python weekly.py  # the same on fictional demo data
```

Give a summary of the changes, the projects that are At Risk or Off Track, and the open
blockers. Offer the executive briefing (`exec-talk-script.md`). Publish the HTML only to the
place that the user names.

For the weekly report of the Scrum Master (board hygiene, burndown, metrics, improvements and
blockers), use routine 1 in `tools/ai-scrum-master/README.md`.

## Files

| Path | Use |
|---|---|
| `references/invest-rubric.md` | The INVEST rubric: the ratings, the score, splitting patterns and examples |
| `references/story-template.md`, `references/epic-template.md` | Shapes for drafts, and the Jira fields |
| `references/jira-access.md` | The route to Jira, the modes, the approval gate and field lookup |
| `references/ceremonies.md` | Roles, the Definition of Ready, the 80/20 rule and the sprint calendar |
| `references/velocity-forecasting-guide.md`, `references/retro-formats.md` | Forecasting and retrospective formats (third party, in story points: read "points" as "stories") |
| `scripts/invest_check.py` | First INVEST score from story JSON or a Jira search export |
| `scripts/analytics/*.py` | Forecast, sprint health score and retrospective analysis (third party, MIT, see `NOTICE.md`) |
| `assets/sample_stories.json`, `assets/sample_sprint_data.json` | Examples of input |
| `../../tools/jira-dashboard/` | Weekly Jira pull, locked snapshots, HTML dashboard and executive briefing |
| `../../tools/ai-scrum-master/` | The scheduled routines, with the weekly report of the Scrum Master |
