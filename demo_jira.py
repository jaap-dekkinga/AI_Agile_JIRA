#!/usr/bin/env python3
"""Offline stand-in for Jira, for demos and testing. Never talks to a network.

When JIRA_DEMO=1 is set, pull_jira.py calls write_pull() instead of the Jira API.
It reads the board's epics from tracker.db as of the latest locked week, moves each
one forward by a small random amount, and writes a pull file in exactly the shape
pull_jira.py produces, so apply_pull.py, advance_week.py and weekly.py all run
unchanged:

  JIRA_DEMO=1 python weekly.py 2026-11-06

The numbers are invented. Use it with the fictional data from seed_demo_db.py.
"""
import json, random, sqlite3, sys

import milestones


def write_pull(key, outfile, exit_no_epics):
    con = sqlite3.connect('tracker.db'); con.row_factory = sqlite3.Row
    week = con.execute("SELECT week FROM weeks WHERE state='locked' ORDER BY seq DESC LIMIT 1").fetchone()
    proj = con.execute("SELECT id FROM projects WHERE upper(jira_key)=?", (key,)).fetchone()
    if not proj:
        sys.exit(f"[demo] no project with jira_key {key} in tracker.db")
    rows = con.execute("""SELECT e.jira_key, e.name, e.owner, e.story_points, e.deadline, ew.pct
                          FROM epics e LEFT JOIN epic_week ew ON ew.epic_id=e.id AND ew.week=?
                          WHERE e.project_id=? ORDER BY e.id""",
                       (week['week'] if week else None, proj['id'])).fetchall()
    if not rows:
        print(f"[demo] {key}: board has no epics yet")
        sys.exit(exit_no_epics)

    rng = random.Random(f"{key}-{week['week'] if week else ''}")
    epics = []
    for r in rows:
        pct = r['pct'] or 0.0
        if pct < 100:
            pct = min(100.0, round(pct + rng.choice([0, 0, 2.5, 5, 8, 12]), 1))
        n = max(3, int((r['story_points'] or 8) // 3))
        epics.append({"key": r['jira_key'], "name": r['name'], "owner": r['owner'],
                      "pts": r['story_points'] or 0, "cur_pct": pct,
                      "epic_due": r['deadline'], "latest_child_due": r['deadline'],
                      "children": n, "done_children": round(n * pct / 100),
                      "credit_children": round(n * pct / 100, 3)})

    ms = []
    for label, _ in milestones.defs_for(key):
        prev = con.execute("""SELECT * FROM milestone_week WHERE project_id=? AND week=? AND label=?""",
                           (proj['id'], week['week'], label)).fetchone() if week else None
        if prev is None or prev['pct'] is None:
            ms.append({"label": label, "pct": None, "basis": None, "issues": 0,
                       "done_issues": 0, "pts": 0, "done_pts": 0, "tagged": 0, "tagged_epics": 0})
            continue
        pct = min(100.0, round(prev['pct'] + rng.choice([0, 3, 6]), 1))
        ms.append({"label": label, "pct": pct, "basis": "points", "issues": prev['issues'],
                   "done_issues": round(prev['issues'] * pct / 100), "pts": prev['pts'],
                   "done_pts": round(prev['pts'] * pct / 100, 1), "tagged": 1, "tagged_epics": 1})
    con.close()

    sprint = {"name": f"{key} Sprint (demo)", "goal": ""}
    json.dump({"epics": epics, "milestones": ms, "sprint": sprint},
              open(outfile, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[demo] {key}: {len(epics)} epics -> {outfile} (fictional data, no network)")
