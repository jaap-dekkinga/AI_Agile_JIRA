# Automation & Margin Dashboard (Jira → weekly snapshot)

A weekly portfolio dashboard that pulls epics and story points from Jira boards and
generates one self-contained HTML snapshot for executive reporting, plus a speaker
script for the weekly briefing.

> Every project, person, Jira key and number in this folder's demo data is **fictional**
> (see `seed_demo_db.py`). Brand slots in the template are marked `[placeholder]`.

## What it shows

- Story-point-weighted completion per project, with partial credit for work in progress
- RAG status (On Track / At Risk / Off Track) against a planned ramp
- Week-over-week trend, from frozen weekly snapshots
- Milestone progress by Jira label
- "Steps to target": the epics closest to done, or the team's sprint goal
- A barrier (blocker) log, raised and resolved by reporting week

Each week is a **frozen historical snapshot**: once locked it is never modified, so the
week-over-week trend is genuine.

## Architecture

```
Jira boards ──pull──► tracker.db (SQLite) ──build──► automation_margin_tracker_dashboard.html
                        ▲                               (self-contained, shareable)
               Python scripts + template2.html
```

- **tracker.db** is the source of truth.
- **The HTML** is a frozen export with the data embedded. No server or database is needed
  to view it.
- **Locked weeks** are the history the dashboard shows. Draft weeks stay hidden until locked.

## Try it in two minutes (no Jira account)

```bash
cd tools/jira-dashboard
python seed_demo_db.py                 # fictional projects, 8 locked weeks of history
JIRA_DEMO=1 python weekly.py 2026-11-06  # "pull" one more week from the offline demo Jira
python -m http.server 8743             # open http://localhost:8743/automation_margin_tracker_dashboard.html
```

`JIRA_DEMO=1` makes `pull_jira.py` read from `demo_jira.py` instead of the Jira API, so
the whole weekly job runs offline. A pre-built sample of the outputs is in
[`samples/`](samples/).

## Use it with your Jira

Requirements: Python 3.9+ and the standard library only. Nothing to `pip install`.

1. Create a Jira API token at https://id.atlassian.com/manage-profile/security/api-tokens.
2. Copy `jira_config.example.json` to `jira_config.json` and fill it in, or set
   `JIRA_EMAIL`, `JIRA_API_TOKEN` and `JIRA_SITE`. **Never commit `jira_config.json`**;
   it is in `.gitignore`.
3. Edit `config.py`: your board keys in `ACTIVE_KEYS`, any non-Epic parent types in
   `PARENT_TYPES`, and milestone labels in `MILESTONES`.
4. Check `SP_FIELD` in `pull_jira.py`. `customfield_10016` is the story-point field on
   most Jira Cloud sites, but not all.
5. Create your projects in `tracker.db` (start from `seed_demo_db.py`, or insert rows into
   `projects` with each `jira_key`), then run the weekly job.

## Weekly workflow

```bash
python weekly.py              # week ending the most recent Friday: pull → lock → build → brief
python weekly.py --no-lock    # stage as a draft and build a preview instead
```

`weekly.py` runs `advance_week.py`, `build_dashboard.py` and `gen_talk_script.py` in order
and prints a summary table. The step-by-step and draft flows are in
[WEEKLY_RUNBOOK.md](WEEKLY_RUNBOOK.md).

## Scripts

| Script | Purpose |
|---|---|
| `weekly.py [date] [--no-lock] [--only K,K] [--all]` | ⭐ The whole weekly job in one command |
| `advance_week.py <date>` | Add one new frozen week: pull live boards, carry the rest forward, lock |
| `build_dashboard.py [--preview] [--out f]` | Generate the HTML (locked weeks only unless `--preview`) |
| `gen_talk_script.py [out.md]` | Generate the exec briefing from the latest locked week |
| `pull_jira.py <KEY> [out.json]` | Pull one board via the Jira REST API (or the demo with `JIRA_DEMO=1`) |
| `apply_pull.py <id> <json> --week <date>` | Apply a pull to one draft week (setup and corrections only) |
| `open_week.py <date>` / `lock_week.py [date]` | Manual draft flow |
| `candidates.py` / `set_steps.py` | Curate "Steps to target" by hand |
| `seed_demo_db.py [--force]` | Create a tracker.db of fictional demo data |
| `demo_jira.py` | Offline stand-in for Jira, used when `JIRA_DEMO=1` |
| `config.py` / `milestones.py` | Board keys, status credit, milestone definitions and storage |

## Key concepts

- **% complete** is story-point-weighted across epic-linked children, with partial credit
  per status (`config.STATUS_CREDIT`: In Progress 50%, In Review 75%). Unpointed and
  orphan issues are invisible to it; a fully unpointed epic falls back to issue counts.
- **Live vs stale:** only boards in `ACTIVE_KEYS` are pulled. Everything else carries its
  last locked week forward and is flagged `stale` in the weekly summary.
- **Steps to target** is `auto` (regenerated each pull) or `manual` (set with
  `set_steps.py`, never overwritten).
- **Milestones** are Jira labels. "Not yet labelled" is reported separately from 0%.

## Sharing the dashboard

The HTML embeds all its data and has **no access control**. Share it only through an
access-controlled location. A sent file is frozen at its "Snapshot generated" date.

## Working with an AI assistant

The pull can also be done by an AI assistant with an Atlassian MCP connection: it fetches
the same epics and children and writes the same `_jira_<KEY>.json`, which `apply_pull.py`
accepts. Both paths produce identical JSON, so they are interchangeable.
