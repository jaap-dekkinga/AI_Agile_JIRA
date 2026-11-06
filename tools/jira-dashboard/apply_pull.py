#!/usr/bin/env python3
"""Apply a Jira epic pull (JSON from pull_jira.py, or from an assistant via MCP) into tracker.db.

  python apply_pull.py <project_id> <json_file> [--week YYYY-MM-DD]

The JSON is {"epics": [...], "milestones": [...], "sprint": {...}} or a bare array of
epics: {key,name,owner,pts,cur_pct,epic_due,latest_child_due,children,done_children}.

IMPORTANT SAFETY RULES:
- This script is for INITIAL SETUP or updating DRAFT weeks only.
- Once you have LOCKED WEEKS, use advance_week.py (or weekly.py) for weekly updates.
- This script will ONLY update the latest locked week (or --week if specified).
- Prior locked weeks are NEVER touched, preserving historical snapshots.

Behavior:
- Replaces the project's epics with the pulled set. PRESERVES epic tags
  (e.g. 'Onboarding') across re-pulls by matching on jira_key.
- Updates epic_week and project_week ONLY for the target week.
- Recomputes project_week pct/planned/var/rag/confidence and the HEADLINE.
- steps: only regenerated for weeks whose steps_source='auto'. Weeks marked
  'manual' (set via set_steps.py) are NEVER overwritten.
"""
import sqlite3, json, sys

import milestones

if len(sys.argv) < 3:
    sys.exit("usage: python apply_pull.py <project_id> <json_file> [--week YYYY-MM-DD]")
PID = int(sys.argv[1]); JF = sys.argv[2]

# Parse optional --week parameter
TARGET_WEEK = None
if len(sys.argv) > 3 and sys.argv[3] == '--week':
    if len(sys.argv) < 5:
        sys.exit("--week requires a date: python apply_pull.py <project_id> <json_file> --week YYYY-MM-DD")
    TARGET_WEEK = sys.argv[4]

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
    See advance_week.steps_from_sprint -- same rule, kept in both entry points.
    """
    if not sprint or not (sprint.get('goal') or '').strip():
        return None
    return f"{sprint['name']} goal: {sprint['goal'].strip()}"

con = sqlite3.connect('tracker.db'); con.row_factory = sqlite3.Row; cx = con.cursor()
prow = cx.execute("SELECT name,target_ga,planned_pct FROM projects WHERE id=?", (PID,)).fetchone()
if not prow: sys.exit(f"project {PID} not found")
name, GA, plan = prow['name'], prow['target_ga'], prow['planned_pct']

# Determine target week and validate
all_weeks = [r['week'] for r in cx.execute("SELECT week FROM weeks WHERE state='locked' ORDER BY seq")]
draft_weeks = [r['week'] for r in cx.execute("SELECT week FROM weeks WHERE state='draft' ORDER BY seq")]

if not all_weeks and not draft_weeks:
    sys.exit("no weeks (locked or draft) to write into")

if TARGET_WEEK:
    if TARGET_WEEK not in all_weeks and TARGET_WEEK not in draft_weeks:
        sys.exit(f"week {TARGET_WEEK} not found in tracker.db")
    WEEK = TARGET_WEEK
    print(f"Targeting specified week: {WEEK}")
else:
    # Default: use latest locked or draft week
    if all_weeks:
        WEEK = all_weeks[-1]
        if len(all_weeks) > 1:
            print(f"WARNING: {len(all_weeks)} locked weeks found. This script will ONLY update {WEEK}.")
            print(f"  Prior weeks ({all_weeks[0]} through {all_weeks[-2]}) will NOT be touched.")
            print(f"  For weekly updates with NEW weeks, use: python advance_week.py <date>")
    else:
        WEEK = draft_weeks[-1]
    print(f"Targeting latest week: {WEEK}")

# Get the week's sequence number for calculating planned_to_date
seq = cx.execute("SELECT seq FROM weeks WHERE week=?", (WEEK,)).fetchone()['seq']

raw = json.load(open(JF, encoding='utf-8'))
# pull_jira.py emits {"epics": [...], "milestones": [...]}. A bare array is the older
# shape (and what a hand-written or MCP-produced pull may look like), so both are
# accepted; a pull without milestones simply leaves them untouched.
E = raw['epics'] if isinstance(raw, dict) else raw
MS = raw.get('milestones') if isinstance(raw, dict) else None
SPRINT = raw.get('sprint') if isinstance(raw, dict) else None

# preserve tags (Onboarding etc.) across re-pulls, keyed by jira_key
existing_epics = {r['jira_key']: dict(r) for r in cx.execute("SELECT * FROM epics WHERE project_id=?", (PID,))}

# Upsert epics: update existing by jira_key, insert new ones
epic_map = {}  # maps epic jira_key to (epic_id, pct, pts)
for e in E:
    cur = eff_pct(e); pts = e.get('pts') or 0
    dl = e.get('epic_due') or e.get('latest_child_due') or GA

    if e['key'] in existing_epics:
        eid = existing_epics[e['key']]['id']
        cx.execute("""UPDATE epics SET name=?,owner=?,story_points=?,deadline=?,status=?
                      WHERE id=?""",
                   (e['name'], e.get('owner') or 'Unassigned', pts, dl, status(cur), eid))
    else:
        eid = cx.execute("SELECT COALESCE(MAX(id),0) FROM epics").fetchone()[0] + 1
        cx.execute("""INSERT INTO epics(id,project_id,jira_key,name,owner,story_points,start_date,deadline,status,tag)
                      VALUES(?,?,?,?,?,?,?,?,?,?)""",
                   (eid, PID, e['key'], e['name'], e.get('owner') or 'Unassigned', pts, None, dl,
                    status(cur), None))

    epic_map[e['key']] = (eid, cur, pts)

    # Update epic_week for target week only
    cx.execute("INSERT OR REPLACE INTO epic_week(epic_id,week,pct) VALUES(?,?,?)", (eid, WEEK, cur))

# Calculate project-level metrics for target week only
num = sum(pct * pts for _, pct, pts in epic_map.values())
den = sum(pts for _, pct, pts in epic_map.values())
pct = round(num / den, 1) if den else 0.0

# Calculate planned_to_date based on week sequence
RAMP_N = 6  # planned-to-date ramp horizon
planned = min(plan, round(plan * (seq + 1) / RAMP_N, 1))
var = round(pct - planned, 1)

# Count completed epics
ndone = sum(1 for _, epic_pct, _ in epic_map.values() if epic_pct >= 100)

# Generate headline (always refreshed, fully data-driven)
head = f"{name} at {pct}% (SP-weighted); {ndone} of {len(E)} epics complete."

# Add an onboarding callout if any epics carry that tag
eps_with_tags = cx.execute("SELECT id,story_points,tag FROM epics WHERE project_id=?", (PID,)).fetchall()
onb = [e for e in eps_with_tags if e['tag'] == 'Onboarding']
if onb:
    ot = sum((e['story_points'] or 0) for e in onb)
    onb_pct_vals = [cx.execute("SELECT pct FROM epic_week WHERE epic_id=? AND week=?", (e['id'], WEEK)).fetchone() for e in onb]
    onb_pcts = [(r['pct'], e['story_points'] or 0) for r, e in zip(onb_pct_vals, onb) if r]
    op = round(sum(p * s for p, s in onb_pcts) / ot, 1) if ot else 0.0
    od = sum(1 for p, s in onb_pcts if p >= 100)
    head += f" Client onboarding at {op}% ({od}/{len(onb)} epics)."

# Update project_week
cx.execute("""INSERT OR REPLACE INTO project_week
              (project_id,week,pct,planned_to_date,rag,confidence,headline,steps,steps_source)
              SELECT ?,?,?,?,?,?,?,COALESCE(pw.steps,''),COALESCE(pw.steps_source,'auto')
              FROM (SELECT 1) dummy
              LEFT JOIN project_week pw ON pw.project_id=? AND pw.week=?""",
           (PID, WEEK, pct, planned, rag(var), CONF[rag(var)], head, PID, WEEK))

# Update steps ONLY if steps_source='auto'
src = cx.execute("SELECT steps_source FROM project_week WHERE project_id=? AND week=?", (PID, WEEK)).fetchone()
if src and src['steps_source'] == 'manual':
    print(f"  Preserved manually-curated steps for week {WEEK}")
else:
    # Auto-generate steps from the epics NEAREST done (see advance_week.py for why).
    notdone = [(key, epic_pct, epic_name) for key, (eid, epic_pct, pts) in epic_map.items()
               if epic_pct < 100
               for epic_name in [cx.execute("SELECT name FROM epics WHERE id=?", (eid,)).fetchone()['name']]]
    lag = sorted(notdone, key=lambda x: x[1], reverse=True)[:3]
    auto = 'All epics complete.' if not notdone else \
        f"Focus next on the work closest to done: {join_and([n for k, p, n in lag])}."
    auto = steps_from_sprint(SPRINT) or auto
    cx.execute("UPDATE project_week SET steps=?,steps_source='auto' WHERE project_id=? AND week=?",
               (auto, PID, WEEK))

if MS:
    milestones.write(cx, PID, WEEK, MS)
    named = [f"{m['label']} {m['pct']}%" if m['pct'] is not None
             else f"{m['label']} unlabelled" for m in MS]
    print(f"  Milestones for {WEEK}: {', '.join(named)}")

con.commit(); con.close()
print(f"Applied {len(E)} epics to project {PID} ({name}) for week {WEEK}")
print(f"  Project completion: {pct}% ({rag(var)})")
print(f"  Next: python build_dashboard.py")
