# AI scrum master routines

This page gives four routines that an AI assistant can operate for a team on a schedule. A
person stays in charge of each one. Each routine reads Jira and the repository, and then reports
or proposes. It never changes Jira or merges anything alone, unless the team permits that kind
of action.

The routines do the record-keeping part of the work of a Scrum Master, as
[Atlassian's Scrum Master guide](https://www.atlassian.com/agile/scrum/scrum-master) lists it:

- Keep the board current.
- Keep stories that are not ready out of planning.
- Do the follow-up of impediments.
- Do the follow-up of retrospectives.
- Report the sprint burndown and other metrics.

People keep the facilitation, the coaching and the reading of the room.

> Example content. The routines use the fictional Harbor Claims Assistant project from
> [`example-project/`](../../example-project/). The Jira project `HCA`, the story ids and the
> paths refer to it.

| Routine | Schedule | Output |
|---|---|---|
| [1. Weekly Scrum Master report](#1-weekly-scrum-master-report) | Mondays at 8:30 | A Markdown report for the Scrum Master |
| [2. Definition of Ready check](#2-definition-of-ready-check) | The day before refinement and the day before planning | A list of the stories that are not Ready |
| [3. Retrospective follow-up](#3-retrospective-follow-up) | The last day of the sprint | The improvement items that are due |
| [4. Weekly dashboard](#4-weekly-dashboard) | Fridays at 15:00 | The executive dashboard and talk script, for approval |

## Two ways to operate them

| | Claude Code scheduled task | Conductor goal |
|---|---|---|
| Where it operates | In the cloud (`/schedule`), or on your computer (a scheduled task in the Claude desktop app) | In your Claude Code session, while it is open |
| How you approve | You read its report and act yourself | You approve or reject each proposal in the Goals pane, or from your phone |
| What enforces "propose only" | The prompt | The prompt, and the guard plugin, which blocks tool calls that the goal does not permit |
| Memory from one run to the next | Only what it reads | Memory for each goal. Your reasons for a rejection become rules that it obeys |
| Best for | Reports | Routines that propose changes, which you approve one at a time |

Routines 1 and 3 read the improvement register. At this time, the register is a local file on
the computer of the Scrum Master (`docs/continuous-improvement.local.md`). Thus operate these
two routines on that computer. A routine in the cloud cannot read the file. Without the file,
routine 1 writes its report without the section on improvements.

Start with scheduled tasks. Each routine on this page is a full prompt, so you can use it
without changes. Add [Conductor](https://github.com/shannonbay/Conductor) later, if you want to
approve in the pane and use the guard. Conductor is an early project of one person, so try it
on one routine first.

## Autonomy: what the AI can do alone

Conductor gives each kind of action a level: off (never), propose (ask first) or auto (go
ahead). The levels in the table agree with the rule in
[agile-practices.md](../../example-project/docs/agile-practices.md#engineering-decides-the-sprint):
Jira follows the agreement of the team, and never gets ahead of it.

| Action category | Level | Why |
|---|---|---|
| `jira.read` | auto | A read changes nothing |
| `jira.comment` | propose | A comment gets to people. Change it to auto after the team trusts the routine |
| `jira.label` | propose | Labels control the roadmap sync (`hca-roadmap`, `not-hca`) |
| `jira.edit` | off | The roadmap owns the text of a Task. The next sync overwrites the edit |
| `jira.transition` | off | The status comes from the roadmap. Sprint changes need the consensus of Engineering |
| `jira.sprint` | off | Only the PM changes a sprint, after Engineering agrees |
| `repo.edit` | propose | Edits stay in the working tree for the owner to commit |
| `repo.commit` | off | The repository owner commits |

Tool rules map tool names to these categories, so that the guard plugin can block a call. The
names of the Atlassian tools are different for each connector. To find your names, use `/mcp`.
With the Atlassian remote MCP server, the rules look like this:

```json
{
  "mcp__*tlassian*__addCommentToJiraIssue": "jira.comment",
  "mcp__*tlassian*__editJiraIssue": "jira.edit",
  "mcp__*tlassian*__transitionJiraIssue": "jira.transition",
  "Edit": "repo.edit",
  "Write": "repo.edit"
}
```

Conductor matches tool names, not shell commands. Thus the guard does not hold `repo.commit`
or the lock of a dashboard week. The instructions and `CLAUDE.md` hold them.

## The routines

### 1. Weekly Scrum Master report

- Schedule: Mondays at 8:30, before the standup.
- Objective: each week, the Scrum Master gets one report on the board, the sprint, the
  improvements and the blockers.
- Instructions:
  Read `example-project/PROJECT_ROADMAP.md`, the active sprint and the last three closed
  sprints of the Jira project HCA, and `example-project/docs/platform/open-questions.md`. If
  the file `example-project/docs/continuous-improvement.local.md` exists, read it too. Write
  the report to `sm-reports/YYYY-MM-DD.md`, with the date of today. Git ignores this folder.
  The report has these sections, in this order:

  1. Board hygiene. Give one line for each Task, with its key and story id:
     - A Task in a sprint without story points.
     - A Task whose Jira status is behind its roadmap status.
     - A roadmap story without a Task (its Jira column is `—`).
     - A Task under a station epic without the label `hca-roadmap` and without the label
       `not-hca`. Propose one of two actions: write the story in the roadmap, or give the Task
       the label `not-hca`.
     - A Task In Progress without an update for 3 working days.
  2. Sprint burndown. Give the sprint goal and the committed story points on day 1. Make a
     table with one row for each working day until today: the day, the ideal remaining points
     (a straight line from the committed points to 0 on day 10), and the actual remaining
     points (committed points minus the points of the Tasks that were Done on or before that
     day). Then say if the sprint is ahead of the ideal line or behind it, and by how many
     points.
  3. Metrics. Give the velocity (the average of Done points in the last three sprints), the
     capacity buffer used (the points of Tasks with the label `unplanned` in the active sprint),
     and the carry-over of the last sprint (the Tasks that were not Done at its end).
  4. Improvements. From the local register, give the number of Active items, the items that are
     after their Review by sprint, and the items that are Active without a measure or an owner.
     If the register is not available, write "Register not available on this computer".
  5. Blockers. List the Tasks in HCA with the blocked flag, and the rows of Blocking now in the
     open questions. For each one, give how long it is blocked and its owner. Mark each item
     that is blocked for more than one working day without an owner.

  Never edit the text, the status or the sprint of a Task. Never post a comment on a Task in
  this routine.
- Health number: the number of board problems, plus the number of blockers older than one
  working day without an owner. Zero is healthy.

### 2. Definition of Ready check

- Schedule: the day before backlog refinement, and the day before sprint planning.
- Objective: only Ready stories get to planning.
- Instructions:
  Compare each of the 15 To Do Tasks with the highest rank in HCA with the
  [Definition of Ready](../../example-project/docs/agile-practices.md#definition-of-ready).
  For each story that fails, say which of the six conditions it fails and what corrects it.
  For example: "the title does not say what the story does", "no value for the user", "no
  acceptance criteria", "too large for one sprint, split it", "needs S7-01, not listed" or
  "blocked on Q-030". End with the Ready story points, compared with two sprints of capacity.
- Health number: Ready story points divided by the capacity of one sprint. If the number is
  less than 1.0, the backlog needs refinement.

### 3. Retrospective follow-up

- Schedule: the morning of the last day of the sprint, before the demo and the retrospective.
  Operate it on the computer of the Scrum Master.
- Objective: each improvement that the team tries gets a decision.
- Instructions:
  Use the `continuous-improvement` skill to review the local register
  `example-project/docs/continuous-improvement.local.md`. Report the items that are due at this
  retrospective, with their measures. Also report the overdue items, the items without a measure
  or an owner, and the free Active places. If you can read a measure from Jira (for example
  "each engineer has Ready work until day 10"), read it and give the number. Do not change the
  file.
- Health number: the number of items after their Review by sprint.

### 4. Weekly dashboard

- Schedule: Fridays at 15:00.
- Objective: a frozen weekly snapshot and an executive talk script, ready for review.
- Instructions:
  In `tools/jira-dashboard`, start `python weekly.py --no-lock`. This command stages the week as
  a draft and makes the preview. Report the summary table, each project with the mark stale,
  and the lines with the mark (REVIEW) in the talk script. Propose to lock the week. Lock it
  only after approval: start `python lock_week.py <date>`, and then `python weekly.py <date>`.
  See [the runbook](../jira-dashboard/WEEKLY_RUNBOOK.md).
- Health number: `0` when this week is locked, and `1` when it is not.

## Creating them in Conductor

First, install Conductor (see its [Quickstart](https://github.com/shannonbay/Conductor#quickstart)).
Then, in the folder of the repository, type:

```text
/goal-new Weekly Scrum Master report: one report each week on the board, the sprint, the improvements and the blockers
```

Choose the schedule that it suggests, or type one (`mondays at 8:30`, `cron 30 8 * * 1`). Then
open the settings of the goal in the web app of Conductor:

1. Paste the instructions of the routine.
2. Set the autonomy levels and the tool rules from this page.
3. Add a health check. In Conductor, a health check is a shell command. It exits with 0 while
   the goal is met, and prints the number to chart. Each routine names its health number. The
   command that gives the number depends on your setup, for example a short script over a Jira
   export.

Your Claude Code session needs the Atlassian connector, because each run is a subagent of that
session and uses its tools.

When you reject a proposal, give the reason. Conductor keeps the reason as memory, and later
runs obey it. If a reason is a habit of the team, add it to the working agreements in the local
improvement register.
