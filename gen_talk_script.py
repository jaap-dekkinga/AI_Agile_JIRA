#!/usr/bin/env python3
"""Generate a fresh exec talk script from tracker.db for the latest locked week.

  python gen_talk_script.py [output.md]     # default: exec-talk-script.md

Reads the current locked reporting week (and the prior locked week for week-over-week)
and writes a speaker script with LIVE numbers, movers, a risks/mitigations table built
from the barrier log, and suggested asks. Facts are auto-filled from the data; lines
marked (REVIEW) are judgment calls to confirm before presenting.

Re-run each week after: advance_week.py <date> -> build_dashboard.py -> gen_talk_script.py
(weekly.py runs all three.)
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
emoji = {'On Track': '🟢', 'At Risk': '🟡', 'Off Track': '🔴'}

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
        asks.append(f"**{name}:** assign an owner to unblock “{b['barrier']}” ({b['severity']}).")
for x in live:
    if x['rag'] == 'Off Track' and x['pct'] == 0:
        asks.append(f"**{x['name']}:** confirm scope, target % and go-live date — it's newly launched and measured against a placeholder target.")
    elif x['rag'] in ('At Risk', 'Off Track'):
        asks.append(f"**{x['name']}:** {x['rag']} at {x['pct']}% ({x['var']:+} vs plan) — agree resourcing/priority to get it back on track.")
seen = set(); asks = [a for a in asks if not (a in seen or seen.add(a))][:6]

L = []
L.append("# Exec Briefing — Automation & Margin Dashboard")
L.append(f"**Reporting week ending {fdate(CUR)}** · generated {datetime.now().strftime('%d %b %Y %H:%M')} · ~10 min + Q&A\n")
L.append("> Auto-generated from tracker.db. `[SHOW: …]` cues = where to be in the dashboard. "
         "Numbers are live; lines marked **(REVIEW)** are judgment calls to confirm before presenting.\n")

L.append("## 1 · Portfolio at a glance\n`[SHOW: Portfolio Overview]`")
L.append(f"- **{rag_ct['On Track']} On Track · {rag_ct['At Risk']} At Risk · {rag_ct['Off Track']} Off Track** across {len(P)} projects.")
L.append(f"- **{len(live)} live from Jira**, averaging **{avg_live}% complete** (story-point-weighted).")
if not movers:
    L.append("- This is the first trustworthy locked baseline — week-over-week reads flat; real deltas begin next week.\n")
else:
    L.append("")

if movers:
    L.append("## 2 · This week's movers\n`[SHOW: trajectory chart]`")
    for x in gain:
        L.append(f"- 📈 **{x['name']}** {x['wow']:+} pts → {x['pct']}%.")
    for x in drop:
        L.append(f"- 📉 **{x['name']}** {x['wow']:+} pts → {x['pct']}%. *(REVIEW: explain why)*")
    L.append("")

L.append("## 3 · Where each initiative stands\n`[SHOW: project table]`\n")
L.append("| Project | Source | % | WoW | Status | vs Plan | Top open risk |")
L.append("|---|---|---|---|---|---|---|")
for x in P:
    wow = '—' if x['wow'] is None else f"{x['wow']:+}"
    top = x['openb'][0]['barrier'][:42] if x['openb'] else '—'
    src = x['key'] if x['live'] else 'mock'
    L.append(f"| {x['name']} | {src} | {x['pct']}% | {wow} | {emoji.get(x['rag'],'')} {x['rag']} | {x['var']:+} | {top} |")
L.append("")

# spotlight: leaders and watch items
leaders = sorted([x for x in live if x['rag'] == 'On Track'], key=lambda x: -x['pct'])[:2]
watch = [x for x in live if x['rag'] in ('At Risk', 'Off Track')]
L.append("## 4 · Spotlight (talking points)")
for x in leaders:
    line = f"- 🟢 **{x['name']} — {x['pct']}%, On Track** ({x['var']:+} vs plan)."
    if x['onbpct'] is not None:
        line += f" Onboarding tracked separately at **{x['onbpct']}%**."
    L.append(line)
for x in watch:
    tb = f" Top blocker: “{x['openb'][0]['barrier']}” ({x['openb'][0]['severity']})." if x['openb'] else ""
    if x['pct'] == 0:
        L.append(f"- 🔴 **{x['name']} — just launched (0%).** Red is vs a placeholder target, not a slip. *(REVIEW: confirm plan/GA.)*{tb}")
    else:
        L.append(f"- {emoji[x['rag']]} **{x['name']} — {x['pct']}%, {x['rag']}.**{tb} *(REVIEW: mitigation + owner.)*")
L.append("")

L.append("## 5 · Risks & mitigations\n`[SHOW: a project's Barrier log]`\n")
if risks:
    L.append("| Project | Risk | Severity | Owner | Status |")
    L.append("|---|---|---|---|---|")
    for name, b in risks[:8]:
        L.append(f"| {name} | {b['barrier'][:48]} | {b['severity']} | {b['owner'] or '—'} | {b['status']} |")
    L.append("\n*(REVIEW: confirm each mitigation and the specific help needed.)*\n")
else:
    L.append("_No open blockers logged this week._\n")

L.append("## 6 · Asks (REVIEW — tailor to the room)")
if asks:
    for i, a in enumerate(asks, 1):
        L.append(f"{i}. {a}")
else:
    L.append("- _No auto-suggested asks; add your own._")
L.append("- **Standing ask:** every team points its Jira stories — that's what keeps these numbers honest.\n")

L.append("## 7 · How we run this (build trust)")
L.append("> Generated straight from Jira, **locked each week** so history can't drift, stamped with a "
         "generation date, with a built-in glossary for every metric and date.")
L.append("`[SHOW: KPI Glossary → Dates & reporting weeks]`\n")

L.append("### Appendix — Q&A")
L.append("- **Why can a number be lower than a past story?** Unpointed Jira stories are invisible to the %; "
         "as teams point their backlog the % reflects *all* the work (truer, sometimes lower).")
L.append("- **Why is WoW flat?** " + ("First trustworthy baseline; deltas start next week." if not movers else "See movers above."))
L.append("- **Is it live?** A weekly locked **snapshot**, not a live feed — stable and auditable. Footer shows the build time.")

open(OUT, 'w', encoding='utf-8').write("\n".join(L) + "\n")
con.close()
print(f"wrote {OUT} for week ending {CUR} ({len(P)} projects, {len(risks)} open risks, {len(asks)} asks)")
