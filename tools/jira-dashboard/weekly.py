#!/usr/bin/env python3
"""The whole weekly job in ONE command: pull Jira -> new locked week -> dashboard -> summary.

  python weekly.py                 # week ending the most recent Friday
  python weekly.py 2026-09-04      # explicit week-ending Friday
  python weekly.py --no-lock       # stage as draft + preview build instead of locking
  python weekly.py --only DPF,OWB  # override which boards are pulled live
  python weekly.py --all           # pull every project that has a jira_key
  python weekly.py --no-refresh    # rebuild outputs only; do not re-pull a draft week

A week that does not exist yet is created. A week that exists and is still a DRAFT is
re-pulled in place, because that is the point of a draft: it tracks the live board
until you lock it. A LOCKED week is a frozen snapshot and is never re-pulled — only
its outputs are rebuilt.

Replaces the old three-step ritual (advance_week.py -> build_dashboard.py ->
gen_talk_script.py) and prints the resulting week as a table so you can see what
moved without opening the dashboard or querying the db.

Only the boards in config.ACTIVE_KEYS are pulled live; every other project carries
its last locked week forward unchanged and is flagged 'stale' in the table.
"""
import sqlite3, subprocess, sys, shutil, os
from datetime import date, timedelta

from config import ACTIVE_KEYS
from pull_jira import EXIT_NO_EPICS

DB = 'tracker.db'


def latest_friday(today=None):
    d = today or date.today()
    return d - timedelta(days=(d.weekday() - 4) % 7)


def run(args):
    """Run a sibling script, streaming its output; abort the job on failure."""
    print(f"\n$ python {' '.join(args)}", flush=True)
    r = subprocess.run([sys.executable] + args)
    if r.returncode != 0:
        sys.exit(f"FAILED: {args[0]} exited {r.returncode} — nothing further was run.")


def refresh(week, live_keys):
    """Re-pull the live boards into an existing DRAFT week, in place.

    apply_pull.py is always given an explicit --week: bare, it defaults to the
    latest LOCKED week and would overwrite a frozen snapshot. Manual steps and
    epic tags survive the re-pull (apply_pull preserves both).
    """
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    projects = con.execute("SELECT id,name,jira_key FROM projects "
                           "WHERE jira_key IS NOT NULL AND active=1 ORDER BY seq").fetchall()
    con.close()
    live = [p for p in projects
            if live_keys is None or (p['jira_key'] or '').upper() in live_keys]
    if not live:
        print("no live boards to refresh — rebuilding outputs only.")
        return set()
    print(f"refreshing draft {week} from: {', '.join(p['jira_key'] for p in live)}")
    done, failed, empty = [], [], []
    for p in live:
        key, jf = p['jira_key'], f"_jira_{p['jira_key']}.json"
        # A dead board (deleted project, renamed key) must not abort the others, so
        # this pull is NOT run through run() — it is allowed to fail per-project.
        print(f"\n$ python pull_jira.py {key} {jf}", flush=True)
        r = subprocess.run([sys.executable, 'pull_jira.py', key, jf],
                           capture_output=True, text=True)
        if r.returncode == EXIT_NO_EPICS:
            # Registered but not planned yet: nothing to write, nothing gone stale.
            print(f"  - {p['name']} ({key}): no epics yet - not on the dashboard until it has one")
            empty.append(key)
            continue
        if r.returncode != 0 or not os.path.exists(jf):
            print(f"  ! pull failed for {p['name']} ({key}): "
                  f"{(r.stderr or r.stdout).strip()[:200]}")
            failed.append(key)
            continue
        run(['apply_pull.py', str(p['id']), jf, '--week', week])
        os.remove(jf)
        done.append(key)
    print(f"\nrefreshed ({len(done)}): {', '.join(done) or 'none'}")
    if empty:
        print(f"no epics yet, not shown ({len(empty)}): {', '.join(empty)}")
    if failed:
        print(f"NOT refreshed ({len(failed)}): {', '.join(failed)} — these projects keep "
              f"the values already in {week}; they are flagged 'stale' below.")
    return set(done)


def summary(week, prev, live_keys):
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    rows = con.execute("""
        SELECT p.name, p.jira_key, p.target_ga, w.pct, w.planned_to_date, w.rag,
               w.steps_source, (SELECT pct FROM project_week
                                WHERE project_id=p.id AND week=?) AS prev_pct
        FROM project_week w JOIN projects p ON p.id=w.project_id
        WHERE w.week=? AND p.active=1 ORDER BY p.seq""", (prev, week)).fetchall()
    blockers = con.execute("""
        SELECT COUNT(*) FROM barriers b JOIN projects p ON p.id=b.project_id
        WHERE p.active=1 AND b.raised_week <= ?
          AND (b.resolved_week IS NULL OR b.resolved_week > ?)""",
        (week, week)).fetchone()[0]
    con.close()

    print(f"\n=== week ending {week}  (prior locked week {prev}) ===")
    hdr = f"{'project':<34}{'board':<7}{'%':>7}{'plan':>7}{'var':>7}{'WoW':>7}  {'RAG':<11}{'source':<9}target GA"
    print(hdr); print('-' * len(hdr))
    for r in rows:
        key = r['jira_key'] or '-'
        fresh = bool(r['jira_key']) and (live_keys is None or key.upper() in live_keys)
        wow = None if r['prev_pct'] is None else round(r['pct'] - r['prev_pct'], 1)
        print(f"{r['name'][:33]:<34}{key:<7}{r['pct']:>7.1f}{r['planned_to_date']:>7.1f}"
              f"{r['pct'] - r['planned_to_date']:>7.1f}"
              f"{('   n/a' if wow is None else f'{wow:+.1f}'):>7}  "
              f"{r['rag']:<11}{('live' if fresh else 'stale'):<9}{r['target_ga'] or '-'}")
    print(f"\nopen blockers as at {week}: {blockers}")
    off = [r['name'] for r in rows if r['rag'] == 'Off Track']
    if off:
        print(f"Off Track: {', '.join(off)}")


def main():
    argv = sys.argv[1:]
    no_lock = '--no-lock' in argv
    no_refresh = '--no-refresh' in argv
    live = ACTIVE_KEYS
    passthru, dates = [], []
    it = iter(argv)
    for a in it:
        if a == '--no-lock':
            passthru.append(a)
        elif a == '--no-refresh':
            pass
        elif a == '--all':
            live = None; passthru.append(a)
        elif a == '--only':
            v = next(it, '')
            live = {k.strip().upper() for k in v.split(',') if k.strip()}
            passthru += ['--only', v]
        else:
            dates.append(a)
    week = dates[0] if dates else latest_friday().isoformat()

    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    exists = con.execute("SELECT state FROM weeks WHERE week=?", (week,)).fetchone()
    prev = con.execute("""SELECT week FROM weeks WHERE state='locked' AND week<?
                          ORDER BY seq DESC LIMIT 1""", (week,)).fetchone()
    con.close()
    prev = prev['week'] if prev else week

    def backup(tag):
        bak = f"{DB}.bak-{date.today():%Y%m%d-%H%M}-{tag}"
        shutil.copyfile(DB, bak)
        print(f"backed up {DB} -> {bak}")

    draft = bool(exists) and exists['state'] == 'draft'
    if exists and not draft:
        print(f"week {week} is LOCKED — not re-pulling it (locked weeks are frozen "
              f"snapshots). Rebuilding outputs only.")
    elif draft and no_refresh:
        print(f"week {week} is a draft but --no-refresh was given. "
              f"Rebuilding outputs only.")
    elif draft:
        backup(f"refresh-{week}")
        # report live/stale on what actually came back, not on what we asked for
        live = refresh(week, live)
    else:
        backup(week)
        run(['advance_week.py', week] + passthru)

    preview = no_lock or draft
    run(['build_dashboard.py'] + (['--preview'] if preview else []))
    run(['gen_talk_script.py'])
    summary(week, prev, live)
    html = '_preview_dashboard.html' if preview else 'automation_margin_tracker_dashboard.html'
    print(f"\nOutputs: {html}, exec-talk-script.md")
    if preview:
        print(f"  {week} is still a draft, so the shareable "
              f"automation_margin_tracker_dashboard.html was NOT updated.\n"
              f"  exec-talk-script.md is regenerated from the latest LOCKED week, not {week}.\n"
              f"  To publish: python lock_week.py {week} && python weekly.py {week}")


if __name__ == '__main__':
    main()
