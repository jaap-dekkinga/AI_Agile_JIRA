#!/usr/bin/env python3
"""Make a new executive talk script from tracker.db for the latest locked week.

  python gen_talk_script.py [output.md]     # default: exec-talk-script.md

The script reads the current locked reporting week, and the locked week before it for the
change from week to week. It writes a speaker script with the current numbers, the largest
changes, a table of risks and mitigations from the barrier log, and proposed requests. The
data gives the facts. Lines with the mark (REVIEW) are judgment calls. Make sure that they are
correct before you give the briefing.

Start it again each week, after: advance_week.py <date> -> build_dashboard.py
(weekly.py starts all three scripts.)
"""
import sqlite3, sys
from datetime import datetime

OUT = sys.argv[1] if len(sys.argv) > 1 else 'exec-talk-script.md'
con = sqlite3.connect('tracker.db'); con.row_factory = sqlite3.Row; cx = con.cursor()

locked = [r['week'] for r in cx.execute("SELECT week FROM weeks WHERE state='locked' ORDER BY seq")]
if not locked:
    sys.exit("no locked weeks in tracker.db")
CUR = locked[-1]; PREV = locked[-2] if len(locked) > 1 else None
SEVRANK = {'High': 0, 'Med': 1, 'Medium': 1, 'Low': 2}

def fdate(d):
    try: return datetime.strptime(d, '%Y-%m-%d').strftime('%d %b %Y')
    except Exception: return d or '—'

P = []
for p in cx.execute("SELECT id,name,jira_key,planned_pct,target_ga FROM projects "
                    "WHERE active=1 ORDER BY seq").fetchall():
    cw = cx.execute("SELECT pct,rag,planned_to_date FROM project_week WHERE project_id=? AND week=?", (p['id'], CUR)).fetchone()
    if not cw: continue
    pw = cx.execute("SELECT pct FROM project_week WHERE project_id=? AND week=?", (p['id'], PREV)).fetchone() if PREV else None
    wow = round(cw['pct'] - pw['pct'], 1) if pw else None
    brs = cx.execute("""SELECT barrier,impact,owner,severity,status,resolved_week FROM barriers
                        WHERE project_id=? AND raised_week<=? ORDER BY id""", (p['id'], CUR)).fetchall()
    openb = [b for b in brs if b['status'] != 'Resolved' and not (b['resolved_week'] and b['resolved_week'] <= CUR)]
    openb.sort(key=lambda b: SEVRANK.get(b['severity'], 3))
    onb = cx.execute("""SELECT e.story_points sp, ew.pct pct FROM epics e JOIN epic_week ew ON ew.epic_id=e.id
                        WHERE e.project_id=? AND e.tag='Onboarding' AND ew.week=?""", (p['id'], CUR)).fetchall()
    onbpct = None
    if onb:
        ot = sum(r['sp'] or 0 for r in onb)
        onbpct = round(sum(r['pct'] * (r['sp'] or 0) for r in onb) / ot, 1) if ot else 0.0
    P.append(dict(id=p['id'], name=p['name'], live=bool(p['jira_key']), key=p['jira_key'],
                  pct=cw['pct'], rag=cw['rag'], var=round(cw['pct'] - cw['planned_to_date'], 1),
                  wow=wow, ga=p['target_ga'], openb=openb, onbpct=onbpct))

live = [x for x in P if x['live']]
rag_ct = {k: sum(1 for x in P if x['rag'] == k) for k in ['On Track', 'At Risk', 'Off Track']}
avg_live = round(sum(x['pct'] for x in live) / len(live), 1) if live else 0

# movers (only if we have a prior week with real movement)
movers = [x for x in P if x['wow'] is not None and abs(x['wow']) >= 0.1]
gain = sorted(movers, key=lambda x: -x['wow'])[:2]
drop = [x for x in sorted(movers, key=lambda x: x['wow']) if x['wow'] < 0][:2]

# open risks across live projects, by severity
risks = []
for x in live:
    for b in x['openb']:
        risks.append((x['name'], b))
risks.sort(key=lambda r: SEVRANK.get(r[1]['severity'], 3))

# suggested asks (REVIEW): high blockers + at-risk/off-track live projects
asks = []
for name, b in risks:
    if SEVRANK.get(b['severity'], 3) == 0:
        asks.append(f"{name}: give an owner to the blocker “{b['barrier']}” ({b['severity']}), so that the owner removes it.")
for x in live:
    if x['rag'] == 'Off Track' and x['pct'] == 0:
        asks.append(f"{x['name']}: agree on the scope, the target % and the go-live date. The project is new, and the dashboard measures it against a placeholder target.")
    elif x['rag'] in ('At Risk', 'Off Track'):
        asks.append(f"{x['name']}: {x['rag']} at {x['pct']}% ({x['var']:+} against the plan). Agree on people and priority, so that it returns to On Track.")
seen = set(); asks = [a for a in asks if not (a in seen or seen.add(a))][:6]

L = []
L.append("# Executive briefing: Automation & Margin Dashboard")
L.append(f"Reporting week ending {fdate(CUR)} · generated {datetime.now().strftime('%d %b %Y %H:%M')} · about 10 minutes, then questions\n")
L.append("> A script makes this file from tracker.db. A `[SHOW: …]` cue tells you which part of the dashboard to show. "
         "The numbers come from the data. Lines with the mark (REVIEW) are judgment calls. "
         "Make sure that they are correct before you give the briefing.\n")

L.append("## 1 · Portfolio summary\n`[SHOW: Portfolio Overview]`")
L.append(f"- {rag_ct['On Track']} On Track · {rag_ct['At Risk']} At Risk · {rag_ct['Off Track']} Off Track, across {len(P)} projects.")
L.append(f"- {len(live)} projects get their data from Jira. Their average is {avg_live}% complete.")
if not movers:
    L.append("- This is the first locked baseline that you can trust. The change from last week shows 0. Real changes start next week.\n")
else:
    L.append("")

if movers:
    L.append("## 2 · Largest changes this week\n`[SHOW: trajectory chart]`")
    for x in gain:
        L.append(f"- {x['name']}: {x['wow']:+} percentage points, to {x['pct']}%.")
    for x in drop:
        L.append(f"- {x['name']}: {x['wow']:+} percentage points, to {x['pct']}%. *(REVIEW: say why.)*")
    L.append("")

L.append("## 3 · Status of each initiative\n`[SHOW: project table]`\n")
L.append("| Project | Source | % | Change from last week | Status | Against plan | Largest open risk |")
L.append("|---|---|---|---|---|---|---|")
for x in P:
    wow = '—' if x['wow'] is None else f"{x['wow']:+}"
    top = x['openb'][0]['barrier'][:42] if x['openb'] else '—'
    src = x['key'] if x['live'] else 'mock'
    L.append(f"| {x['name']} | {src} | {x['pct']}% | {wow} | {x['rag']} | {x['var']:+} | {top} |")
L.append("")

# spotlight: leaders and watch items
leaders = sorted([x for x in live if x['rag'] == 'On Track'], key=lambda x: -x['pct'])[:2]
watch = [x for x in live if x['rag'] in ('At Risk', 'Off Track')]
L.append("## 4 · Points to talk about")
for x in leaders:
    line = f"- {x['name']}: {x['pct']}%, On Track ({x['var']:+} against the plan)."
    if x['onbpct'] is not None:
        line += f" The dashboard tracks onboarding separately, at {x['onbpct']}%."
    L.append(line)
for x in watch:
    tb = f" Largest blocker: “{x['openb'][0]['barrier']}” ({x['openb'][0]['severity']})." if x['openb'] else ""
    if x['pct'] == 0:
        L.append(f"- {x['name']}: new project (0%). The status is Off Track against a placeholder target, not because of a delay. *(REVIEW: make sure that the plan and the GA date are correct.)*{tb}")
    else:
        L.append(f"- {x['name']}: {x['pct']}%, {x['rag']}.{tb} *(REVIEW: give the mitigation and its owner.)*")
L.append("")

L.append("## 5 · Risks and mitigations\n`[SHOW: a project's Barrier log]`\n")
if risks:
    L.append("| Project | Risk | Severity | Owner | Status |")
    L.append("|---|---|---|---|---|")
    for name, b in risks[:8]:
        L.append(f"| {name} | {b['barrier'][:48]} | {b['severity']} | {b['owner'] or '—'} | {b['status']} |")
    L.append("\n*(REVIEW: make sure that each mitigation is correct, and say what the team needs.)*\n")
else:
    L.append("_The log has no open blockers this week._\n")

L.append("## 6 · Requests (REVIEW: change them for the audience)")
if asks:
    for i, a in enumerate(asks, 1):
        L.append(f"{i}. {a}")
else:
    L.append("- _The script has no requests to propose. Add your own._")
L.append("- Standing request: each team links each Jira story to its epic. These numbers do not include a story without an epic.\n")

L.append("## 7 · How we make this report")
L.append("> The data comes directly from Jira. We lock each week, so the history cannot change. "
         "Each file shows the date on which it was made, and has a glossary for each metric and date.")
L.append("`[SHOW: KPI Glossary → Dates & reporting weeks]`\n")

L.append("### Appendix: questions and answers")
L.append("- Why can a number be lower than in an earlier week? The % includes only the Jira stories that are linked to an epic. "
         "When a team adds stories to an epic, the % includes more work. The number is more correct, and sometimes lower.")
L.append("- Why do some projects show no change from last week? " + ("This is the first baseline that you can trust. Changes start next week." if not movers else "Their numbers did not change this week, or their teams report them by hand. Section 2 gives the largest changes."))
L.append("- Is it live? No. It is a weekly locked snapshot, not a live feed. Thus it is stable, and you can audit it. The footer shows when the file was made.")

open(OUT, 'w', encoding='utf-8').write("\n".join(L) + "\n")
con.close()
print(f"wrote {OUT} for week ending {CUR} ({len(P)} projects, {len(risks)} open risks, {len(asks)} asks)")
