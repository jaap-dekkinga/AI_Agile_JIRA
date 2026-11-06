#!/usr/bin/env python3
"""Read tracker.db and generate the standalone dashboard HTML.

Workflow: edit tracker.db -> python build_dashboard.py -> refreshed HTML.

Produces a compact week-indexed JSON (every reporting week fully resolved) and
injects it into template2.html at the __DATA__ token. The page renders 'as of'
whichever week the dropdown selects (defaults to the latest).
"""
import json, sqlite3, sys
from datetime import datetime

import milestones

con = sqlite3.connect('tracker.db'); con.row_factory = sqlite3.Row; cx = con.cursor()

# Normally the dashboard shows only locked (finalized) weeks. Pass --preview to also
# include draft weeks so you can eyeball a staged pull before locking it in.
PREVIEW = '--preview' in sys.argv
STATE = "state IN ('locked','draft')" if PREVIEW else "state='locked'"

# The default filename is the team-shared snapshot, so a --preview run would otherwise
# publish unlocked draft numbers to everyone. --out keeps a local review copy separate;
# --preview defaults to one unless you name a path yourself.
OUTFILE = 'automation_margin_tracker_dashboard.html'
if '--out' in sys.argv:
    OUTFILE = sys.argv[sys.argv.index('--out') + 1]
elif PREVIEW:
    OUTFILE = '_preview_dashboard.html'

weeks = [dict(week=r['week'], label=r['label'])
         for r in cx.execute(f"SELECT * FROM weeks WHERE {STATE} ORDER BY seq")]
WK = [w['week'] for w in weeks]
assert WK, "no weeks to render — lock a week with lock_week.py (or use --preview for drafts)"
CUR = WK[-1]
if PREVIEW: print("PREVIEW MODE: including draft weeks")

projects = [dict(id=r['id'], name=r['name'], lead=r['lead'], sponsor=r['sponsor'],
                 workstream=r['workstream'], ga=r['target_ga'], summary=r['summary'])
            for r in cx.execute("SELECT * FROM projects WHERE active=1 ORDER BY seq")]
assert projects, "no active projects to render — all rows have projects.active=0"
# jira_key is the lookup key for config.MILESTONES but is not shown on the page, so
# it is kept out of the projects payload the template renders.
jkey = {r['id']: r['jira_key'] for r in cx.execute("SELECT id,jira_key FROM projects")}

def derive_status(pct):
    if pct >= 100: return 'Done'
    if pct <= 0: return 'Not Started'
    return 'In Progress'

# Full pct series per project (for the trend chart, independent of selected week).
# Index-aligned to WK, with None for any week the project has no row in. A project added
# mid-history simply has no earlier rows; back-filling them would invent progress that
# never happened, so the series carries a genuine gap and the chart skips it.
series = {}
for p in projects:
    have = {r['week']: r['pct'] for r in cx.execute(
        f"""SELECT pw.week, pw.pct FROM project_week pw JOIN weeks w ON w.week=pw.week
            WHERE pw.project_id=? AND w.{STATE}""", (p['id'],)).fetchall()}
    series[p['name']] = [round(have[w], 1) if w in have else None for w in WK]

byWeek = {}
for wi, w in enumerate(WK):
    pw = {}
    for p in projects:
        r = cx.execute("SELECT * FROM project_week WHERE project_id=? AND week=?", (p['id'], w)).fetchone()
        if r is None:
            continue   # project had not joined the portfolio yet in this week
        pct = round(r['pct'], 1); planned = round(r['planned_to_date'], 1)
        # WoW compares against the most recent EARLIER week that has data, not the
        # preceding slot, so a gap in history cannot silently shift the comparison.
        earlier = [v for v in series[p['name']][:wi] if v is not None]
        prev = earlier[-1] if earlier else None
        wow = None if prev is None else round(pct - prev, 1)
        var = round(pct - planned, 1)
        # open blockers as of this week
        brows = cx.execute("SELECT * FROM barriers WHERE project_id=? AND raised_week<=?", (p['id'], w)).fetchall()
        openblk = 0
        for b in brows:
            resolved = b['resolved_week'] is not None and b['resolved_week'] <= w
            if not resolved: openblk += 1
        pw[p['name']] = dict(pct=pct, planned=planned, wow=wow, var=var, rag=r['rag'],
                             headline=r['headline'], steps=r['steps'], conf=r['confidence'],
                             openblk=openblk)
    # only the projects actually reporting in this week
    present = [p for p in projects if p['name'] in pw]
    # epics as-of week
    eps = {}
    for p in present:
        # Soonest delivery date first — reads as a runway, so the epics needing
        # attention this month sit at the top. NULL deadlines sort last; e.id breaks ties.
        erows = cx.execute("""SELECT e.jira_key,e.name,e.owner,e.story_points,e.deadline,e.status,e.tag,ew.pct
                              FROM epics e JOIN epic_week ew ON ew.epic_id=e.id
                              WHERE e.project_id=? AND ew.week=?
                              ORDER BY e.deadline IS NULL, e.deadline, e.id""", (p['id'], w)).fetchall()
        lst = []
        for e in erows:
            pct = round(e['pct'], 1)
            status = e['status'] if w == CUR else derive_status(pct)
            lst.append(dict(key=e['jira_key'], name=e['name'], owner=e['owner'],
                            pts=e['story_points'], deadline=e['deadline'], status=status, pct=pct,
                            tag=e['tag']))
        eps[p['name']] = lst
    # barriers as-of week (visible if raised by then; status reflects resolution as of week)
    bar = {}
    for p in present:
        brows = cx.execute("SELECT * FROM barriers WHERE project_id=? AND raised_week<=? ORDER BY id", (p['id'], w)).fetchall()
        lst = []
        for b in brows:
            resolved = b['resolved_week'] is not None and b['resolved_week'] <= w
            lst.append(dict(barrier=b['barrier'], impact=b['impact'], owner=b['owner'],
                            sev=b['severity'], status=('Resolved' if resolved else b['status']),
                            target=b['target_res'], raised=b['raised_date'],
                            raisedWeek=b['raised_week'],
                            resolvedWeek=(b['resolved_week'] if resolved else None)))
        bar[p['name']] = lst
    # milestones as-of week — only for boards configured in config.MILESTONES, so
    # every other project renders no MS Progress panel at all
    mst = {}
    for p in present:
        rows = milestones.read(cx, p['id'], w, jkey.get(p['id']))
        if rows:
            mst[p['name']] = rows
    byWeek[w] = dict(projects=pw, epics=eps, barriers=bar, milestones=mst)

data = dict(weeks=weeks, currentWeek=CUR, projects=projects, series=series, byWeek=byWeek,
            generatedAt=datetime.now().strftime('%d %b %Y, %H:%M'))
con.close()

tpl = open('template2.html', encoding='utf-8').read()
out = tpl.replace('__DATA__', json.dumps(data, separators=(',', ':')))
assert '__DATA__' not in out
open(OUTFILE, 'w', encoding='utf-8').write(out)
print("generated", OUTFILE, len(out), "chars from tracker.db")
print("weeks:", WK, "| default:", CUR)
