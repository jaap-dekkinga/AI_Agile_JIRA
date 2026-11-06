#!/usr/bin/env python3
"""Advance the reporting calendar by ONE new frozen (locked) reporting week.

  python advance_week.py <YYYY-MM-DD> [label] [--no-lock] [--only KEY,KEY | --all]
  python build_dashboard.py

With --no-lock the week is fully populated and verified but left in state='draft',
so you can review it with `build_dashboard.py --preview` before committing it with
`lock_week.py <YYYY-MM-DD>`. (Staging a multi-project draft by hand does not work:
apply_pull.py defaults to the latest LOCKED week, and open_week.py does not carry
mock projects forward.)

Unlike apply_pull.py, this ADDS a single new week and writes ONLY that week — prior
locked weeks are never touched, so each locked week becomes a genuine frozen
snapshot and real week-over-week history accumulates.

Per project:
  - Live (jira_key set AND in ACTIVE_KEYS): pulls the board fresh via pull_jira.py and
    writes its CURRENT state into the new week. Epics are upserted BY jira_key so
    prior weeks' epic_week rows keep their stable ids and history. Tags are kept.
  - Stale/mock (no jira_key, or a jira_key outside ACTIVE_KEYS): carries its most
    recent locked week forward unchanged.

ACTIVE_KEYS (config.py) is the set of boards reported live. Other boards are
deliberately allowed to go stale. Use --only KEY,KEY to override for one run, or
--all to pull every project that has a jira_key.

Safety: the new week is created 'draft', fully populated, verified (every project
must have a row), then locked in one transaction. Any failure rolls everything
back so build_dashboard never sees a partial week.
"""
import sqlite3, sys, subprocess, json, os
from datetime import date

RAMP_N = 6  # planned-to-date ramp horizon; caps at planned_pct from week 6 onward

import milestones
from config import ACTIVE_KEYS   # boards pulled live; everything else carries forward
from pull_jira import EXIT_NO_EPICS

def status(p): return 'Done' if p >= 100 else ('Not Started' if p <= 0 else 'In Progress')
def rag(v): return 'On Track' if v >= -3 else ('At Risk' if v >= -13 else 'Off Track')
CONF = {'On Track': 'High', 'At Risk': 'Medium', 'Off Track': 'Low'}
def eff_pct(e):
    if (e.get('pts') or 0) == 0 and (e.get('children') or 0) > 0:
        # credit_children carries partial credit (config.STATUS_CREDIT); it is absent
        # from older pulls, where the strict count is correct.
        num = e.get('credit_children', e.get('done_children', 0))
        return round(100 * num / e['children'], 1)
    return e['cur_pct']
def join_and(x):
    if len(x) == 1: return x[0]
    if len(x) == 2: return f"{x[0]} and {x[1]}"
    return ", ".join(x[:-1]) + f", and {x[-1]}"
def steps_from_sprint(sprint):
    """The sprint goal as a steps line, or None to fall back to the generated one.

    The goal is the team's own statement of intent, so it outranks anything derived
    from epic percentages. Many boards leave it blank, which is why this returns
    None rather than an empty string -- a blank goal must not blank out the steps.
    """
    if not sprint or not (sprint.get('goal') or '').strip():
        return None
    return f"{sprint['name']} goal: {sprint['goal'].strip()}"

NO_LOCK = '--no-lock' in sys.argv
ACTIVE = ACTIVE_KEYS
argv = []
it = iter(sys.argv)
for a in it:
    if a == '--no-lock':
        continue
    if a == '--all':
        ACTIVE = None   # None = pull every project that has a jira_key
        continue
    if a == '--only':
        ACTIVE = {k.strip().upper() for k in next(it, '').split(',') if k.strip()}
        continue
    argv.append(a)
if len(argv) < 2:
    sys.exit("usage: python advance_week.py YYYY-MM-DD [label] [--no-lock] [--only KEY,KEY | --all]")
NEW = argv[1]
y, m, d = NEW.split('-')
LABEL = argv[2] if len(argv) > 2 else f"{d}/{m}"

con = sqlite3.connect('tracker.db'); con.row_factory = sqlite3.Row; cx = con.cursor()

if cx.execute("SELECT 1 FROM weeks WHERE week=?", (NEW,)).fetchone():
    sys.exit(f"week {NEW} already exists")
prev = cx.execute("SELECT week FROM weeks WHERE state='locked' ORDER BY seq DESC LIMIT 1").fetchone()
if not prev:
    sys.exit("no existing locked week to advance from")
PREV = prev['week']
seq = cx.execute("SELECT COALESCE(MAX(seq),-1) FROM weeks").fetchone()[0] + 1
cx.execute("INSERT INTO weeks(week,label,seq,state,locked_at) VALUES(?,?,?,'draft',NULL)", (NEW, LABEL, seq))
print(f"advancing from {PREV} -> new week {NEW} (seq {seq})")

# active=0 projects are retired from reporting: not pulled, not carried forward, and
# not required by the completeness check below. Their history stays in the db.
projects = cx.execute("SELECT id,name,jira_key,target_ga,planned_pct FROM projects "
                      "WHERE active=1 ORDER BY seq").fetchall()
jira_done, carried, failed = [], [], []
not_yet = []   # ids of registered boards with no epics and no history yet

print(f"live boards: {'ALL with a jira_key' if ACTIVE is None else (', '.join(sorted(ACTIVE)) or 'none')}"
      " — all other projects carry their last locked week forward")

for p in projects:
    pid, key = p['id'], p['jira_key']
    if key and (ACTIVE is None or key.upper() in ACTIVE):
        jf = f"_jira_{key}.json"
        r = subprocess.run([sys.executable, 'pull_jira.py', key, jf], capture_output=True, text=True)
        never_reported = not cx.execute("SELECT 1 FROM project_week WHERE project_id=? LIMIT 1",
                                        (pid,)).fetchone()
        if r.returncode == EXIT_NO_EPICS and never_reported:
            # A registered board nobody has planned yet. Not a failure: it has no
            # history to go stale, so it just stays off the dashboard until its
            # first epic lands. A board that HAS reported and now comes back empty
            # is not this case — that falls through to 'failed' and aborts the week.
            print(f"  - {p['name']} ({key}): no epics yet - not on the dashboard until it has one")
            not_yet.append(pid)
            continue
        if r.returncode != 0 or not os.path.exists(jf):
            print(f"  ! pull failed for {p['name']} ({key}): {(r.stderr or r.stdout).strip()[:140]}")
            failed.append(p['name']); continue
        raw = json.load(open(jf, encoding='utf-8')); os.remove(jf)
        # {"epics": [...], "milestones": [...]} since milestone tracking landed; a
        # bare array is the older shape and still works.
        E = raw['epics'] if isinstance(raw, dict) else raw
        if isinstance(raw, dict) and raw.get('milestones'):
            milestones.write(cx, pid, NEW, raw['milestones'])
        wkrows = []   # (cur_pct, pts, epic_id)
        for e in E:
            cur = eff_pct(e); pts = e.get('pts') or 0
            dl = e.get('epic_due') or e.get('latest_child_due') or p['target_ga']
            ex = cx.execute("SELECT id FROM epics WHERE project_id=? AND jira_key=?", (pid, e['key'])).fetchone()
            if ex:
                eid = ex['id']
                cx.execute("UPDATE epics SET name=?,owner=?,story_points=?,deadline=?,status=? WHERE id=?",
                           (e['name'], e.get('owner') or 'Unassigned', pts, dl, status(cur), eid))
            else:
                eid = cx.execute("SELECT COALESCE(MAX(id),0) FROM epics").fetchone()[0] + 1
                cx.execute("""INSERT INTO epics(id,project_id,jira_key,name,owner,story_points,start_date,deadline,status,tag)
                              VALUES(?,?,?,?,?,?,?,?,?,NULL)""",
                           (eid, pid, e['key'], e['name'], e.get('owner') or 'Unassigned', pts, None, dl, status(cur)))
            cx.execute("INSERT OR REPLACE INTO epic_week(epic_id,week,pct) VALUES(?,?,?)", (eid, NEW, cur))
            wkrows.append((cur, pts, eid))
        num = sum(c * s for c, s, _ in wkrows); den = sum(s for c, s, _ in wkrows)
        pct = round(num / den, 1) if den else 0.0
        planned = min(p['planned_pct'], round(p['planned_pct'] * (seq + 1) / RAMP_N, 1))
        var = round(pct - planned, 1)
        ndone = sum(1 for c, s, _ in wkrows if c >= 100)
        head = f"{p['name']} at {pct}% (SP-weighted); {ndone} of {len(E)} epics complete."
        onb_ids = {r2['id'] for r2 in cx.execute("SELECT id FROM epics WHERE project_id=? AND tag='Onboarding'", (pid,))}
        if onb_ids:
            onb = [(c, s) for c, s, eid in wkrows if eid in onb_ids]
            ot = sum(s for c, s in onb)
            opct = round(sum(c * s for c, s in onb) / ot, 1) if ot else 0.0
            od = sum(1 for c, s in onb if c >= 100)
            head += f" Client onboarding at {opct}% ({od}/{len(onb_ids)} epics)."
        idname = {r2['id']: r2['name'] for r2 in cx.execute("SELECT id,name FROM epics WHERE project_id=?", (pid,))}
        # Most-complete first: the epics nearest done are the cheapest to finish, and
        # finishing them is what converts work-in-progress into delivered percentage.
        notdone = sorted([(c, idname[eid]) for c, s, eid in wkrows if c < 100 and eid in idname],
                         key=lambda x: x[0], reverse=True)
        steps = 'All epics complete.' if not notdone else \
            f"Focus next on the work closest to done: {join_and([n for _, n in notdone[:3]])}."
        steps = steps_from_sprint(raw.get('sprint') if isinstance(raw, dict) else None) or steps
        cx.execute("""INSERT INTO project_week(project_id,week,pct,planned_to_date,rag,headline,steps,confidence,steps_source)
                      VALUES(?,?,?,?,?,?,?,?, 'auto')""",
                   (pid, NEW, pct, planned, rag(var), head, steps, CONF[rag(var)]))
        jira_done.append(f"{p['name']} {pct}%")
    else:
        prow = cx.execute("""SELECT pct,planned_to_date,rag,headline,steps,confidence,steps_source
                             FROM project_week WHERE project_id=? AND week=?""", (pid, PREV)).fetchone()
        if not prow:
            print(f"  ! no prior row to carry forward for {p['name']}"); failed.append(p['name']); continue
        cx.execute("""INSERT INTO project_week(project_id,week,pct,planned_to_date,rag,headline,steps,confidence,steps_source)
                      VALUES(?,?,?,?,?,?,?,?,?)""",
                   (pid, NEW, prow['pct'], prow['planned_to_date'], prow['rag'], prow['headline'],
                    prow['steps'], prow['confidence'], prow['steps_source'] or 'auto'))
        for er in cx.execute("""SELECT ew.epic_id AS eid, ew.pct AS pct FROM epic_week ew
                                JOIN epics e ON e.id=ew.epic_id WHERE e.project_id=? AND ew.week=?""",
                             (pid, PREV)).fetchall():
            cx.execute("INSERT OR REPLACE INTO epic_week(epic_id,week,pct) VALUES(?,?,?)", (er['eid'], NEW, er['pct']))
        # Milestones carry forward with everything else. Without this a board that
        # went stale would show an empty MS panel for the new week, reading as
        # "the labels disappeared" rather than "these numbers are unchanged".
        milestones.ensure(cx)
        cx.execute("""INSERT OR REPLACE INTO milestone_week
                      (project_id,week,label,pct,basis,issues,done_issues,pts,done_pts)
                      SELECT project_id,?,label,pct,basis,issues,done_issues,pts,done_pts
                      FROM milestone_week WHERE project_id=? AND week=?""", (NEW, pid, PREV))
        carried.append(p['name'])

missing = [p['name'] for p in projects if p['id'] not in not_yet
           and not cx.execute("SELECT 1 FROM project_week WHERE project_id=? AND week=?", (p['id'], NEW)).fetchone()]
if missing:
    con.rollback()
    sys.exit(f"ABORT (rolled back): no data for {NEW} for: {missing}. Week not created.")

if not NO_LOCK:
    cx.execute("UPDATE weeks SET state='locked', locked_at=? WHERE week=?", (date.today().isoformat(), NEW))
con.commit(); con.close()
print(f"staged {NEW} as DRAFT (not locked)." if NO_LOCK else f"locked {NEW}.")
print(f"  Jira ({len(jira_done)}): {', '.join(jira_done)}")
print(f"  carried forward ({len(carried)}): {', '.join(carried)}")
if not_yet:
    print(f"  no epics yet, not shown ({len(not_yet)}): "
          f"{', '.join(p['name'] for p in projects if p['id'] in not_yet)}")
if failed:
    print(f"  NOTE failed/skipped: {failed}")
if NO_LOCK:
    print(f"next: python build_dashboard.py --preview   # review, then: python lock_week.py {NEW}")
else:
    print("next: python build_dashboard.py")
