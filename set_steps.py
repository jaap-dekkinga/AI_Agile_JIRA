#!/usr/bin/env python3
"""Populate the 'Steps to target' text for a project+week from candidate numbers.

  python set_steps.py <project_id> <week> <n1> <n2> ...

The numbers refer to the list printed by candidates.py (same ordering: least
complete first). Epics appear in the ORDER YOU LIST THEM. Names only, no %.
Refuses to write to a locked week (open a draft to change history).
"""
import sqlite3, sys

if len(sys.argv) < 4:
    sys.exit("usage: python set_steps.py <project_id> <week> <n1> <n2> ...")
pid = int(sys.argv[1]); week = sys.argv[2]; nums = [int(x) for x in sys.argv[3:]]

con = sqlite3.connect('tracker.db'); con.row_factory = sqlite3.Row; cx = con.cursor()
wk = cx.execute("SELECT state FROM weeks WHERE week=?", (week,)).fetchone()
if not wk:
    sys.exit(f"week {week} not found")
if wk['state'] == 'locked':
    sys.exit(f"week {week} is locked — cannot edit. Open a new draft week to change priorities.")

# same ordering as candidates.py
cand = cx.execute("""SELECT e.name FROM epics e JOIN epic_week ew ON ew.epic_id=e.id
                     WHERE e.project_id=? AND ew.week=? AND ew.pct<100 ORDER BY ew.pct, e.id""",
                  (pid, week)).fetchall()
try:
    names = [cand[n-1]['name'] for n in nums]
except IndexError:
    sys.exit(f"a number is out of range (project {pid} has {len(cand)} candidates for {week})")

def join_and(x):
    if len(x) == 1: return x[0]
    if len(x) == 2: return f"{x[0]} and {x[1]}"
    return ", ".join(x[:-1]) + f", and {x[-1]}"

steps = f"Priorities for next week: {join_and(names)}."
# mark as 'manual' so a future re-pull (apply_pull.py) never overwrites your picks
cx.execute("UPDATE project_week SET steps=?, steps_source='manual' WHERE project_id=? AND week=?",
           (steps, pid, week))
con.commit(); con.close()
print(f"project {pid} / {week} steps set (manual):\n  {steps}\nRebuild: python build_dashboard.py")
