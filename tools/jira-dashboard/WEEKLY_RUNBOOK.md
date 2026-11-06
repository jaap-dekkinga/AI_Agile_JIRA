# Automation & Margin Dashboard — Weekly Runbook

The dashboard is a single self-contained HTML file generated from a SQLite database. This
runbook is how you update and publish it.

## Mental model

```
Jira boards ──pull──► tracker.db (source of truth) ──build──► automation_margin_tracker_dashboard.html
                        ▲                                       (frozen, shareable snapshot)
               template2.html + *.py scripts
```

- `tracker.db` holds all data. The **HTML is a frozen export**: send it to anyone and they
  see that snapshot. It shows a "Snapshot generated …" date.
- The dashboard shows **only locked weeks.** Each locked week is a frozen reporting snapshot.
- Run everything below **from this folder**.

## Critical safety rules

Once you have locked weeks with historical data:

1. ✅ **Do** use `weekly.py` (or `advance_week.py <date>`) for weekly updates. It creates a
   NEW week with fresh Jira data and never touches prior locked weeks.
2. ❌ **Don't** use `apply_pull.py` on locked weeks. Use it only on DRAFT weeks or during
   initial setup, and always pass `--week YYYY-MM-DD`.
3. ✅ **Do** keep backups. `weekly.py` copies `tracker.db` to `tracker.db.bak-*` before it
   changes anything.
4. ❌ **Don't** hand-edit locked weeks with SQL. Changing past data breaks week-over-week
   tracking. To fix an error: restore from a backup, correct it in a draft, then lock.

**Why this matters:** locked weeks are the history used for trend analysis and executive
reporting. Overwriting them destroys the audit trail.

---

## One-time setup

### Path A — pure Python pull (recommended)
1. Create a Jira API token: https://id.atlassian.com/manage-profile/security/api-tokens
2. Copy `jira_config.example.json` → `jira_config.json` and fill in email, token and site
   (or set `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_SITE`). Keep it private.
3. Test: `python pull_jira.py <KEY>` should write `_jira_<KEY>.json`.

### Path B — AI-assistant pull (Atlassian MCP; optional)
1. Connect the Atlassian MCP server in your assistant and authenticate.
2. Ask it to "refresh `<KEY>`". It pulls via MCP and produces the same `_jira_<KEY>.json`.

Both paths produce identical JSON, so they are interchangeable.

### Path C — offline demo
`python seed_demo_db.py`, then prefix any command with `JIRA_DEMO=1`. No account needed.

---

## Weekly update (use this every week)

```bash
python weekly.py 2026-11-06     # the week-ending Friday; omit it for the most recent Friday
```

This pulls every live board into a new week, carries the other projects forward, locks the
week, rebuilds the dashboard, regenerates `exec-talk-script.md` and prints a summary table.

Lines marked **(REVIEW)** in the talk script are judgment calls to confirm before presenting.

Optionally curate that week's "Steps to target", then rebuild:

```bash
python candidates.py --week 2026-11-06 --project 5   # numbered epic menu
python set_steps.py 5 2026-11-06 4 1 3                # pick, in priority order
python build_dashboard.py
```

> `set_steps.py` refuses to write to a locked week. To curate before publishing, stage the
> week as a draft first (`python weekly.py --no-lock`), curate, then lock.

View locally: `python -m http.server 8743` → http://localhost:8743/automation_margin_tracker_dashboard.html

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

- Draft weeks are hidden from the normal build; `--preview` (which `--no-lock` uses) shows
  them and writes `_preview_dashboard.html`, never the shared file.
- Re-pulling a draft **preserves** steps set with `set_steps.py` and epic tags (for
  example `Onboarding`). It only refreshes "auto" steps.

---

## Adding a new Jira project

1. Add a row to `projects` with the board's key in `jira_key`, or set it on an existing
   mock project: `UPDATE projects SET jira_key='<KEY>' WHERE id=<id>;`
2. Add the key to `ACTIVE_KEYS` in `config.py`.
3. From the next `weekly.py` run it is pulled automatically. A board with no epics yet is
   skipped quietly until its first epic lands.

To retire a project, set `projects.active=0`. Don't remove its key from `ACTIVE_KEYS`.

---

## Dates & weeks — quick reference

A **reporting week** is a labelled weekly bucket used for all slicing; **calendar dates** are
real timestamps shown for audit and freshness and mapped *into* a reporting week.

| Term | What it is | Example |
|---|---|---|
| **Reporting week** (`weeks.week`) | The week-ending Friday that names a reporting period; what the dropdown selects. | "Week ending 2026-10-30" |
| **Locked week** (`state='locked'`) | A finalized reporting week — frozen and shown on the dashboard. | 2026-10-23 |
| **Draft week** (`state='draft'`) | A week being prepared — hidden until locked. | a week staged with `--no-lock` |
| **Selected week** | The week chosen in the dropdown; every figure renders "as of" it. | switch to 16 Oct → all figures reflect 16 Oct |
| **Locked date** (`locked_at`) | Calendar day the week was finalized. Audit only. | week 10-30 locked_at 2026-11-02 |
| **Barrier raised / resolved week** | Reporting week a blocker appeared / was cleared. | raised wk 10-09 → shows from 10-09 on |
| **Target GA** (`target_ga`) | Project go-live date; drives "Days to GA". | 2026-12-18 |
| **Snapshot generated** | When the HTML was built (footer). | "06 Nov 2026, 15:36" |

## Key concepts

- **% complete** = story-point-weighted credit ÷ total across epic-linked children.
  **Unpointed stories and orphan (no-epic) issues are invisible to it**: point and link them
  in Jira to close that blind spot.
- **Steps to target:** `steps_source` is 'auto' (regenerated each pull: the epics closest to
  done, or the sprint goal) or 'manual' (your picks via `set_steps.py`).
- **Barrier log:** tied to the selected week. A blocker shows once its raised week is
  reached and flips to Resolved when its resolved week passes.

## Housekeeping

- To revert, copy a `tracker.db.bak-*` backup over `tracker.db` and rebuild.
- Temporary `_jira_*.json` pull files are safe to delete after applying.
- **Sharing:** the HTML embeds all data and has no access control. Share it through an
  access-controlled location, and re-upload after each build.
