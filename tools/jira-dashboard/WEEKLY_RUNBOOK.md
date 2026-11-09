# Automation & Margin Dashboard: Weekly Runbook

The dashboard is a single self-contained HTML file that the scripts make from a SQLite
database. This runbook tells you how to update and publish it.

## Mental model

```
Jira boards ──pull──► tracker.db (source of truth) ──build──► automation_margin_tracker_dashboard.html
                        ▲                                       (frozen, shareable snapshot)
               template2.html + *.py scripts
```

- `tracker.db` holds all data. The HTML is a frozen export. When you send it to a person, they
  see that snapshot. It shows a "Snapshot generated …" date.
- The dashboard shows only locked weeks. Each locked week is a frozen reporting snapshot.
- Run all the commands on this page from this folder.

## Critical safety rules

When you have locked weeks with historical data, obey these rules:

1. Use `weekly.py` (or `advance_week.py <date>`) for weekly updates. It makes a new week with
   new Jira data, and never touches the locked weeks before it.
2. Do not use `apply_pull.py` on locked weeks. Use it only on draft weeks or during the first
   setup. Always give `--week YYYY-MM-DD`.
3. Keep backups. `weekly.py` copies `tracker.db` to `tracker.db.bak-*` before it changes
   anything.
4. Do not edit locked weeks by hand with SQL. If you change past data, the trend from week to
   week is wrong. To correct an error, restore a backup, correct the error in a draft, and then
   lock the draft.

The locked weeks are the history for trend analysis and executive reporting. If you overwrite
them, you destroy the audit trail.

---

## One-time setup

### Path A: pure Python pull (recommended)

1. Make a Jira API token: https://id.atlassian.com/manage-profile/security/api-tokens
2. Copy `jira_config.example.json` to `jira_config.json`. Fill in the email, the token and the
   site, or set `JIRA_EMAIL`, `JIRA_API_TOKEN` and `JIRA_SITE`. Keep the file private.
3. Do a test: `python pull_jira.py <KEY>` must write `_jira_<KEY>.json`.

### Path B: AI-assistant pull (Atlassian MCP, optional)

1. Connect the Atlassian MCP server in your assistant and sign in.
2. Ask the assistant to "refresh `<KEY>`". It pulls through MCP and makes the same
   `_jira_<KEY>.json`.

The two paths make the same JSON, so you can use either one.

### Path C: offline demo

Run `python seed_demo_db.py`. Then put `JIRA_DEMO=1` before each command. You do not need an
account.

---

## Weekly update (use this each week)

```bash
python weekly.py 2026-11-06     # the week-ending Friday; omit it for the most recent Friday
```

This command pulls each live board into a new week and carries the other projects forward.
Then it locks the week, makes the dashboard again, makes `exec-talk-script.md` again, and
prints a summary table.

The talk script marks some lines with (REVIEW). These lines are judgment calls. Make sure that
they are correct before you present.

If you want, select the "Steps to target" for that week, and then build again:

```bash
python candidates.py --week 2026-11-06 --project 5   # numbered epic menu
python set_steps.py 5 2026-11-06 4 1 3                # pick, in priority order
python build_dashboard.py
```

> `set_steps.py` refuses to write to a locked week. To select the steps before you publish,
> stage the week as a draft first (`python weekly.py --no-lock`). Then select the steps, and
> lock the week.

To look at the dashboard on your computer, run `python -m http.server 8743`. Then open
http://localhost:8743/automation_margin_tracker_dashboard.html

---

## Draft flow (review before publishing)

```bash
python weekly.py 2026-11-06 --no-lock   # 1. stage as a draft; builds _preview_dashboard.html
python weekly.py 2026-11-06             # 2. re-pull the draft in place, as often as needed
python candidates.py --week 2026-11-06  # 3. curate steps (optional)
python set_steps.py 5 2026-11-06 4 1 3
python lock_week.py 2026-11-06          # 4. finalize (freezes the week)
python weekly.py 2026-11-06             # 5. rebuild the shareable outputs
```

- The normal build does not show draft weeks. `--preview` (which `--no-lock` uses) shows them,
  and writes `_preview_dashboard.html`. It never writes the shared file.
- When you pull a draft again, the pull keeps the steps that you set with `set_steps.py` and
  the epic tags (for example `Onboarding`). It changes only the "auto" steps.

---

## Adding a new Jira project

1. Add a row to `projects`, with the key of the board in `jira_key`. Or set the key on a mock
   project: `UPDATE projects SET jira_key='<KEY>' WHERE id=<id>;`
2. Add the key to `ACTIVE_KEYS` in `config.py`.
3. The next `weekly.py` run pulls the board automatically. If a board has no epics yet, the job
   skips it without a message until its first epic exists.

To retire a project, set `projects.active=0`. Do not remove its key from `ACTIVE_KEYS`.

---

## Dates & weeks: quick reference

A reporting week is a labeled weekly bucket that the dashboard uses for all slicing. Calendar
dates are real timestamps. The dashboard shows them for audit and freshness, and maps them
*into* a reporting week.

| Term | What it is | Example |
|---|---|---|
| Reporting week (`weeks.week`) | The week-ending Friday that names a reporting period. The dropdown selects it. | "Week ending 2026-10-30" |
| Locked week (`state='locked'`) | A finalized reporting week. It is frozen, and the dashboard shows it. | 2026-10-23 |
| Draft week (`state='draft'`) | A week in preparation. It stays hidden until you lock it. | A week staged with `--no-lock` |
| Selected week | The week that you choose in the dropdown. Each figure shows the values "as of" that week. | Select 16 Oct, and all figures show 16 Oct |
| Locked date (`locked_at`) | The calendar day on which the week was finalized. For audit only. | Week 10-30, locked_at 2026-11-02 |
| Barrier raised / resolved week | The reporting week in which a blocker started, or was removed. | Raised in week 10-09, shown from 10-09 |
| Target GA (`target_ga`) | The go-live date of the project. "Days to GA" comes from it. | 2026-12-18 |
| Snapshot generated | The time when the HTML was built (in the footer). | "06 Nov 2026, 15:36" |

## Key concepts

- % complete = the credit, weighted by story points, divided by the total, across the children
  that are linked to an epic. It does not see stories without points or issues without an
  epic. Give them points and link them in Jira, so that the dashboard sees them.
- Steps to target: `steps_source` is 'auto' or 'manual'. 'auto' is made again at each pull,
  from the epics that are closest to done or from the sprint goal. 'manual' is your choice,
  made with `set_steps.py`.
- Barrier log: it follows the selected week. A blocker shows from its raised week. It changes
  to Resolved after its resolved week.

## Housekeeping

- To go back to an earlier state, copy a `tracker.db.bak-*` backup over `tracker.db` and build
  again.
- After you apply them, you can delete the temporary `_jira_*.json` pull files.
- Sharing: the HTML holds all data and has no access control. Share it through a location with
  access control, and upload it again after each build.
