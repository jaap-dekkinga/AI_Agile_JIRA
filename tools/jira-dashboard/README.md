# Automation & Margin Dashboard (Jira → weekly snapshot)

This tool is a weekly portfolio dashboard. It gets epics and story points from Jira boards and
makes one self-contained HTML snapshot for executive reporting. It also makes a speaker script
for the weekly briefing.

> Each project, person, Jira key and number in the demo data of this folder is fictional (see
> `seed_demo_db.py`). The template marks the brand slots with `[placeholder]`.

## What it shows

- Completion for each project, weighted by story points, with partial credit for work in
  progress.
- RAG status (On Track / At Risk / Off Track) against a planned ramp.
- The trend from week to week, from frozen weekly snapshots.
- Milestone progress by Jira label.
- "Steps to target": the epics that are closest to done, or the sprint goal of the team.
- A barrier (blocker) log, raised and resolved by reporting week.

Each week is a frozen historical snapshot. After you lock a week, nothing changes it. Thus the
trend from week to week is true.

## Architecture

```
Jira boards ──pull──► tracker.db (SQLite) ──build──► automation_margin_tracker_dashboard.html
                        ▲                               (self-contained, shareable)
               Python scripts + template2.html
```

- `tracker.db` is the source of truth.
- The HTML is a frozen export, with the data in the file. You do not need a server or a
  database to see it.
- The dashboard shows the locked weeks as its history. Draft weeks stay hidden until you lock
  them.

## Try it in two minutes (no Jira account)

```bash
cd tools/jira-dashboard
python seed_demo_db.py                 # fictional projects, 8 locked weeks of history
JIRA_DEMO=1 python weekly.py 2026-11-06  # "pull" one more week from the offline demo Jira
python -m http.server 8743             # open http://localhost:8743/automation_margin_tracker_dashboard.html
```

With `JIRA_DEMO=1`, `pull_jira.py` reads from `demo_jira.py`, not from the Jira API. Thus the
full weekly job operates offline. A pre-built sample of the outputs is in
[`samples/`](samples/).

## Use it with your Jira

You need Python 3.9 or later and the standard library only. It is not necessary to `pip install`
anything.

1. Make a Jira API token at https://id.atlassian.com/manage-profile/security/api-tokens.
2. Copy `jira_config.example.json` to `jira_config.json` and fill it in. Or set `JIRA_EMAIL`,
   `JIRA_API_TOKEN` and `JIRA_SITE`. Never commit `jira_config.json`. It is in `.gitignore`.
3. Edit `config.py`. Put your board keys in `ACTIVE_KEYS`, the parent types that are not Epic
   in `PARENT_TYPES`, and the milestone labels in `MILESTONES`.
4. Make sure that `SP_FIELD` in `pull_jira.py` is the story-point field of your site.
   `customfield_10016` is the story-point field on most Jira Cloud sites, but not on all of them.
5. Add your projects to `tracker.db`. Start from `seed_demo_db.py`, or add rows to
   `projects` with the `jira_key` of each project. Then start the weekly job.

## Weekly workflow

```bash
python weekly.py              # week ending the most recent Friday: pull → lock → build → brief
python weekly.py --no-lock    # stage as a draft and build a preview instead
```

`weekly.py` starts `advance_week.py`, `build_dashboard.py` and `gen_talk_script.py` in this
order. Then it prints a summary table. [WEEKLY_RUNBOOK.md](WEEKLY_RUNBOOK.md) gives the step-by-step
flow and the draft flow.

## Scripts

| Script | Purpose |
|---|---|
| `weekly.py [date] [--no-lock] [--only K,K] [--all]` | The full weekly job in one command |
| `advance_week.py <date>` | Adds one new frozen week. It pulls the live boards, copies the last week of the other projects into it, and locks the week |
| `build_dashboard.py [--preview] [--out f]` | Makes the HTML. It uses only locked weeks, unless you give `--preview` |
| `gen_talk_script.py [out.md]` | Makes the executive briefing from the latest locked week |
| `pull_jira.py <KEY> [out.json]` | Pulls one board through the Jira REST API, or from the demo with `JIRA_DEMO=1` |
| `apply_pull.py <id> <json> --week <date>` | Applies a pull to one draft week. Use it only for setup and corrections |
| `open_week.py <date>` / `lock_week.py [date]` | The manual draft flow |
| `candidates.py` / `set_steps.py` | Select the "Steps to target" by hand |
| `seed_demo_db.py [--force]` | Makes a `tracker.db` with fictional demo data |
| `demo_jira.py` | An offline replacement for Jira, used when `JIRA_DEMO=1` |
| `config.py` / `milestones.py` | Board keys, status credit, milestone definitions and storage |

## Key concepts

- % complete is weighted by story points across the children that are linked to an epic. It
  gives partial credit for each status (`config.STATUS_CREDIT`: In Progress 50%, In Review
  75%). It does not see issues without points or issues without a parent. If no issue in an
  epic has points, it uses issue counts.
- Live and stale: the job pulls only the boards in `ACTIVE_KEYS`. All other projects copy their
  last locked week into the new week, and the weekly summary marks them `stale`.
- Steps to target is `auto` (made again at each pull) or `manual` (set with `set_steps.py`,
  never overwritten).
- Milestones are Jira labels. The dashboard reports "Not yet labelled" separately from 0%.

## Sharing the dashboard

The HTML holds all its data and has no access control. Share it only through a location with
access control. A file that you send stays frozen at its "Snapshot generated" date.

## Working with an AI assistant

An AI assistant with an Atlassian MCP connection can also do the pull. It gets the same epics
and children, and writes the same `_jira_<KEY>.json`, which `apply_pull.py` accepts. The two
paths make the same JSON, so you can use either one.

To let an AI assistant start this job each week and propose to lock the week, see routine 4 in
[`tools/ai-scrum-master/`](../ai-scrum-master/README.md).
