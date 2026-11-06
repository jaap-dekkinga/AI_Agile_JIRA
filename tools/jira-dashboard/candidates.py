#!/usr/bin/env python3
"""Show the numbered candidate epics (not yet 100%) for a week, per project.

  python candidates.py                     # latest week, all projects
  python candidates.py --project 5         # one project by id
  python candidates.py --week 2026-07-10

Use the numbers with set_steps.py to populate the 'Steps to target' text.
The % shown here is only a reference for choosing; it is NOT written into the text.
"""
import sqlite3, argparse

ap = argparse.ArgumentParser()
ap.add_argument('--week')
ap.add_argument('--project', type=int)
a = ap.parse_args()

con = sqlite3.connect('tracker.db'); con.row_factory = sqlite3.Row; cx = con.cursor()
week = a.week or cx.execute("SELECT week FROM weeks ORDER BY seq DESC LIMIT 1").fetchone()[0]
st = cx.execute("SELECT state FROM weeks WHERE week=?", (week,)).fetchone()
print(f"Candidate epics for week {week} (state={st[0] if st else '??'})\n")

pq = "SELECT id,name FROM projects" + (" WHERE id=?" if a.project else "") + " ORDER BY seq"
projects = cx.execute(pq, (a.project,) if a.project else ()).fetchall()
for p in projects:
    rows = cx.execute("""SELECT e.name, ew.pct FROM epics e JOIN epic_week ew ON ew.epic_id=e.id
                         WHERE e.project_id=? AND ew.week=? AND ew.pct<100 ORDER BY ew.pct, e.id""",
                      (p['id'], week)).fetchall()
    if not rows:
        continue
    print(f"=== [{p['id']}] {p['name']} ===")
    for i, r in enumerate(rows, 1):
        print(f"  {i:2}. {r['name']}  ({int(round(r['pct']))}%)")
    print(f"  -> set with: python set_steps.py {p['id']} {week} <numbers...>\n")
con.close()
