#!/usr/bin/env python3
"""Lock (finalize) a reporting week — the 'final list is committed' action.

  python lock_week.py [YYYY-MM-DD]

With no argument, locks the latest DRAFT week. Locking stamps locked_at with
today's date and freezes the week: it becomes visible on the dashboard and
refreshes will refuse to overwrite it. Lock is global — it finalizes every
project's numbers for that week at once.
"""
import sqlite3, sys
from datetime import date

con = sqlite3.connect('tracker.db'); cx = con.cursor()

week = sys.argv[1] if len(sys.argv) > 1 else None
if week is None:
    row = cx.execute("SELECT week FROM weeks WHERE state='draft' ORDER BY seq DESC LIMIT 1").fetchone()
    if not row:
        sys.exit("no draft week to lock (open one with open_week.py)")
    week = row[0]

cur = cx.execute("SELECT state FROM weeks WHERE week=?", (week,)).fetchone()
if not cur:
    sys.exit(f"week {week} not found")
if cur[0] == 'locked':
    sys.exit(f"week {week} is already locked")

today = date.today().isoformat()
cx.execute("UPDATE weeks SET state='locked', locked_at=? WHERE week=?", (today, week))
con.commit(); con.close()
print(f"locked {week} (as of {today}). Rebuild: python build_dashboard.py")
