#!/usr/bin/env python3
"""Open a new DRAFT reporting week.

  python open_week.py 2026-07-10 [label]

Creates a weeks row in state='draft'. Draft weeks are NOT shown on the dashboard
until you lock them (lock_week.py). Pulls/refreshes stage their numbers into the
latest draft week; you can re-pull as many times as you like before locking.
"""
import sqlite3, sys

if len(sys.argv) < 2:
    sys.exit("usage: python open_week.py YYYY-MM-DD [label]")
week = sys.argv[1]
y, m, d = week.split('-')
label = sys.argv[2] if len(sys.argv) > 2 else f"{d}/{m}"

con = sqlite3.connect('tracker.db'); cx = con.cursor()
exists = cx.execute("SELECT state FROM weeks WHERE week=?", (week,)).fetchone()
if exists:
    sys.exit(f"week {week} already exists (state={exists[0]})")
seq = cx.execute("SELECT COALESCE(MAX(seq),-1) FROM weeks").fetchone()[0] + 1
cx.execute("INSERT INTO weeks(week,label,seq,state,locked_at) VALUES(?,?,?,'draft',NULL)",
           (week, label, seq))
con.commit(); con.close()
print(f"opened draft week {week} (label {label}, seq {seq}). Pull/stage into it, then: python lock_week.py {week}")
