# AI scrum master routines

Five routines an AI assistant can run for a team on a schedule, written so a person stays in
charge. Each one reads Jira and the repository, then **proposes**. It never changes Jira or
merges anything on its own unless the team has allowed that kind of action.

They cover the parts of a Scrum Master's job that are record-keeping, as listed in
[Atlassian's Scrum Master guide](https://www.atlassian.com/agile/scrum/scrum-master): keeping
the board current, protecting planning from unready work, chasing impediments, following up on
retrospectives, and reporting. Facilitation, coaching and reading the room stay with people.

> **Example content.** The routines use the fictional Harbor Claims Assistant project from
> [`example-project/`](../../example-project/). Jira project `HCA`, story ids and paths refer to it.

## Two ways to run them

| | Claude Code scheduled task (`/schedule`) | Conductor goal |
|---|---|---|
| Where it runs | Anthropic's cloud, laptop open or not | Your Claude Code session, while it is open |
| How you approve | You read its report and act yourself | Approve or reject each proposal in the Goals pane, or from your phone |
| What enforces "propose only" | The prompt | The prompt, plus the guard plugin, which blocks tool calls the goal doesn't allow |
| Memory between runs | None, beyond what it reads | Per-goal memory. Your rejection reasons become rules it follows |
| Best for | Read-only reports | Routines that propose changes you want to approve one by one |

Start with scheduled tasks. Each routine below is a complete prompt, so it works as a
`/schedule` prompt as it stands. Add [Conductor](https://github.com/shannonbay/Conductor) later
if you want approve-in-the-pane and the guard. Conductor is an early, one-person project, so try
it on one routine first.

## Autonomy: what the AI may do alone

Conductor gives every kind of action a level: **off** (never), **propose** (ask first) or
**auto** (go ahead). The levels below fit the rule in
[agile-practices.md](../../example-project/docs/agile-practices.md#engineering-decides-the-sprint):
Jira follows the team's agreement and never gets ahead of it.

| Action category | Level | Why |
|---|---|---|
| `jira.read` | auto | Reading changes nothing |
| `jira.comment` | propose | A comment reaches people. Move to auto after the team trusts it |
| `jira.label` | propose | Labels drive the roadmap sync (`hca-roadmap`, `not-hca`) |
| `jira.edit` | off | The roadmap owns a Task's text. The next sync would overwrite it anyway |
| `jira.transition` | off | Status follows the roadmap. Sprint changes need Engineering's consensus |
| `jira.sprint` | off | Only the PM changes a sprint, after Engineering agrees |
| `repo.edit` | propose | Edits are left in the working tree for the owner to commit |
| `repo.commit` | off | The repository owner commits |

**Tool rules** map tool names to these categories, so the guard plugin can block a call.
Atlassian tool names differ by connector, so check yours with `/mcp`. With the Atlassian remote
MCP server they look like this:

```json
{
  "mcp__*tlassian*__addCommentToJiraIssue": "jira.comment",
  "mcp__*tlassian*__editJiraIssue": "jira.edit",
  "mcp__*tlassian*__transitionJiraIssue": "jira.transition",
  "Edit": "repo.edit",
  "Write": "repo.edit"
}
```

Conductor matches tool names, not shell commands, so `repo.commit` and locking a dashboard
week are held by the instructions and by `CLAUDE.md`, not by the guard.

## The routines

### 1. Board hygiene

- **Schedule:** weekdays at 8:30, before standup.
- **Objective:** keep the HCA board true to the roadmap.
- **Instructions:**
  Read `example-project/PROJECT_ROADMAP.md` and the open Tasks under the station epics of Jira
  project HCA. Report each of these, one line per Task, with its key and story id:
  - a Task in a sprint with no story points
  - a Task whose Jira status is behind its roadmap status
  - a roadmap story with no Task (its **Jira** column is `—`)
  - a Task under a station epic with neither the `hca-roadmap` nor the `not-hca` label
  - a Task In Progress with no update for 3 working days

  For an unlabeled Task, propose either writing the story in the roadmap or labeling it
  `not-hca`. Never edit a Task's text, status or sprint.
- **Health number:** the number of problems found. Zero is healthy.

### 2. Definition of Ready check

- **Schedule:** the day before backlog grooming, and the day before sprint planning.
- **Objective:** only Ready stories reach planning.
- **Instructions:**
  For the 15 highest-ranked To Do Tasks in HCA, check each story against the
  [Definition of Ready](../../example-project/docs/agile-practices.md#definition-of-ready).
  For each one that fails, say which of the five points it fails and what would fix it, for
  example "names no spec rule", "needs S7-01, not merged", "13 points, split it", "blocked on
  Q-030 with no recorded assumption".
  End with the Ready story points against two sprints of capacity.
- **Health number:** Ready story points divided by one sprint's capacity. Below 1.0 needs grooming.

### 3. Blocker ageing

- **Schedule:** weekdays at 13:00.
- **Objective:** no impediment waits unnoticed.
- **Instructions:**
  List Tasks flagged as blocked in HCA and the rows of **Blocking now** in
  `example-project/docs/platform/open-questions.md`. For each, give how long it has been
  blocked, its owner, and whether the standup left it with an owner and next step, a huddle,
  or an open question. Flag anything blocked for more than one working day with no owner.
  Propose a comment on the Task asking the owner for the next step. Never transition it.
- **Health number:** the number of blockers older than one working day with no owner.

### 4. Retrospective follow-up

- **Schedule:** the morning of the sprint's last day, before the demo and retrospective.
- **Objective:** every improvement the team tries gets a decision.
- **Instructions:**
  Use the `continuous-improvement` skill to review
  `example-project/docs/continuous-improvement.md`. Report the items due at this retrospective
  with their measures, the overdue items, items missing a measure or an owner, and free
  Trying slots. Where a measure can be read from Jira (for example "nobody runs out of Ready
  work before day 10"), read it and give the number. Change nothing in the file.
- **Health number:** the number of items past their review sprint.

### 5. Weekly dashboard

- **Schedule:** Fridays at 15:00.
- **Objective:** a frozen weekly snapshot and an executive talk script, ready for review.
- **Instructions:**
  In `tools/jira-dashboard`, run `python weekly.py --no-lock` to stage this week as a draft and
  build the preview. Report the summary table, any project marked stale, and the lines marked
  (REVIEW) in the talk script. Propose locking the week. Lock it only after approval, with
  `python lock_week.py <date>` and then `python weekly.py <date>`.
  See [the runbook](../jira-dashboard/WEEKLY_RUNBOOK.md).
- **Health number:** `0` when this week is locked, `1` when it is not.

## Creating them in Conductor

After installing Conductor (its [Quickstart](https://github.com/shannonbay/Conductor#quickstart)),
in the repository's folder:

```text
/goal-new Board hygiene: keep the HCA board true to the roadmap
```

Pick the schedule it suggests or type one (`weekdays at 9`, `cron 30 8 * * 1-5`). Then, in the
goal's settings in Conductor's web app, paste the routine's instructions and set the autonomy
levels and tool rules above. A Conductor health check is a shell command that exits 0 while the
goal is met and prints the number to chart. Each routine names its health number. The command
that produces it depends on your setup, for example a short script over a Jira export. Your Claude Code session needs the
Atlassian connector, because each run is a subagent of that session and uses its tools.

When you reject a proposal, give the reason. Conductor keeps it as memory, and later runs
follow it. A reason that turns out to be a team habit belongs in the
[working agreements](../../example-project/docs/continuous-improvement.md#working-agreements),
where the whole team can see it.
