#!/usr/bin/env python3
"""Create a fresh tracker.db filled with FICTIONAL demo data.

  python seed_demo_db.py            # refuses to overwrite an existing tracker.db
  python seed_demo_db.py --force    # replace it

Every project, epic, person, blocker and number written here is invented. It exists
so the dashboard, the weekly job and the exec briefing can be run end to end without
a Jira account (pair it with JIRA_DEMO=1, see demo_jira.py).

The schema is the one the rest of the scripts expect:

  weeks(week PK, label, seq, state 'draft'|'locked', locked_at)
  projects(id PK, name, lead, sponsor, workstream, target_ga, summary, planned_pct,
           seq, jira_key, active)
  project_week(project_id, week, pct, planned_to_date, rag, headline, steps,
               confidence, steps_source 'auto'|'manual')
  epics(id PK, project_id, jira_key, name, owner, story_points, start_date,
        deadline, status, tag)
  epic_week(epic_id, week, pct)
  barriers(id PK, project_id, barrier, impact, owner, raised_date, raised_week,
           severity, status, target_res, resolved_week)
  milestone_week(project_id, week, label, pct, basis, issues, done_issues, pts, done_pts)
"""
import os, sqlite3, sys, random
from datetime import date, timedelta

import milestones

DB = 'tracker.db'
RAMP_N = 6

if os.path.exists(DB):
    if '--force' not in sys.argv:
        sys.exit(f"{DB} already exists — pass --force to replace it with demo data")
    os.remove(DB)

rng = random.Random(42)   # deterministic: the same demo every time

SCHEMA = """
CREATE TABLE weeks(week TEXT PRIMARY KEY, label TEXT, seq INTEGER, state TEXT DEFAULT 'draft', locked_at TEXT);
CREATE TABLE projects(id INTEGER PRIMARY KEY, name TEXT UNIQUE, lead TEXT, sponsor TEXT,
  workstream TEXT, target_ga TEXT, summary TEXT, planned_pct REAL, seq INTEGER, jira_key TEXT,
  active INTEGER NOT NULL DEFAULT 1);
CREATE TABLE project_week(project_id INTEGER, week TEXT, pct REAL, planned_to_date REAL,
  rag TEXT, headline TEXT, steps TEXT, confidence TEXT, steps_source TEXT DEFAULT 'auto',
  PRIMARY KEY(project_id, week));
CREATE TABLE epics(id INTEGER PRIMARY KEY, project_id INTEGER, jira_key TEXT, name TEXT,
  owner TEXT, story_points REAL, start_date TEXT, deadline TEXT, status TEXT, tag TEXT);
CREATE TABLE epic_week(epic_id INTEGER, week TEXT, pct REAL, PRIMARY KEY(epic_id, week));
CREATE TABLE barriers(id INTEGER PRIMARY KEY, project_id INTEGER, barrier TEXT, impact TEXT,
  owner TEXT, raised_date TEXT, raised_week TEXT, severity TEXT, status TEXT,
  target_res TEXT, resolved_week TEXT);
"""

# Eight Fridays of locked history, oldest first.
LAST = date(2026, 10, 30)
WEEKS = [(LAST - timedelta(weeks=i)).isoformat() for i in range(7, -1, -1)]

# name, jira_key (None = mock/manual), lead, sponsor, workstream, target GA, planned %, summary
PROJECTS = [
    ("Claims Follow-Up Automation", "CFU", "Jordan Reyes", "Morgan Lee", "Automation", "2026-12-18", 80,
     "Automate claim-status checks and next-step recommendations for the follow-up queue."),
    ("Intake Document Classification", "IDC", "Priya Nair", "Morgan Lee", "Automation", "2027-01-29", 60,
     "Classify inbound payer correspondence and route it to the right work queue."),
    ("Prior-Auth Assistant", None, "Sam Okafor", "Dana Brooks", "Automation", "2027-03-31", 35,
     "Draft prior-authorization requests from chart data for human review (tracked manually)."),
    ("Payer Policy Search", "PPS", "Elena Petrova", "Dana Brooks", "Margin", "2026-12-04", 85,
     "Searchable, cited payer policy answers for billing specialists."),
    ("Operator Workbench", "OWB", "Chris Tan", "Morgan Lee", "Platform", "2027-02-26", 55,
     "The operator UI where recommendations are reviewed and actioned."),
    ("Long-Term Care Onboarding", None, "Avery Johnson", "Dana Brooks", "Margin", "2027-01-15", 50,
     "Onboard the long-term-care line of business onto the shared workflow (tracked manually)."),
    ("Data Platform Foundation", "DPF", "Riley Chen", "Taylor Kim", "Platform", "2027-03-12", 45,
     "A governed data platform for billing, operator actions and payer-policy data."),
    ("Practice System Integrations", None, "Noah Williams", "Taylor Kim", "Platform", "2027-04-30", 30,
     "Connectors to the practice-management systems clients run (tracked manually)."),
    ("Agent Platform", "AGP", "Jamie Fox", "Taylor Kim", "Platform", "2026-11-27", 70,
     "Retired: folded into Operator Workbench."),
]
RETIRED = {"AGP"}

EPIC_NAMES = {
    "CFU": ["Claim status inquiry pipeline", "Status interpretation rules", "Follow-up queue scoring",
            "Re-status scheduler", "Client onboarding: reference pack", "Operator feedback loop"],
    "IDC": ["Document ingestion", "Classifier baseline", "Confidence thresholds and review queue",
            "Routing rules per client", "Accuracy reporting"],
    "PPS": ["Policy corpus ingestion", "Citation-first answer format", "Search relevance tuning",
            "Specialist pilot", "Change alerts for updated policies"],
    "OWB": ["Recommendation review screen", "Bulk actions with approval gate", "Audit trail view",
            "Role-based access", "Keyboard-first navigation", "Accessibility pass"],
    "DPF": ["Source inventory and schema freeze", "Billing system ingestion", "Operator action ingestion",
            "Payer-policy ingestion", "Data-quality monitors", "Analytics workspace outputs",
            "Legacy reporting migration"],
    "AGP": ["Tool registry", "Agent sandbox"],
}
OWNERS = ["Jordan Reyes", "Priya Nair", "Elena Petrova", "Chris Tan", "Riley Chen",
          "Sam Okafor", "Lena Fischer", "Marco Silva", "Unassigned"]

con = sqlite3.connect(DB); cx = con.cursor()
cx.executescript(SCHEMA)
milestones.ensure(cx)

for i, w in enumerate(WEEKS):
    y, m, d = w.split('-')
    cx.execute("INSERT INTO weeks VALUES(?,?,?,'locked',?)", (w, f"{d}/{m}", i, w))

def status(p): return 'Done' if p >= 100 else ('Not Started' if p <= 0 else 'In Progress')
def rag(v): return 'On Track' if v >= -3 else ('At Risk' if v >= -13 else 'Off Track')
CONF = {'On Track': 'High', 'At Risk': 'Medium', 'Off Track': 'Low'}

eid = 0
prev_pct = {}   # epic id -> last week's pct, so progress never goes backwards
for pid, (name, key, lead, sponsor, ws, ga, plan, summary) in enumerate(PROJECTS, 1):
    active = 0 if key in RETIRED else 1
    cx.execute("INSERT INTO projects VALUES(?,?,?,?,?,?,?,?,?,?,?)",
               (pid, name, lead, sponsor, ws, ga, summary, plan, pid, key, active))
    # pace: some projects ahead, some behind, so every RAG colour appears
    pace = {"CFU": 1.05, "IDC": 0.8, "PPS": 0.98, "OWB": 0.65, "DPF": 0.9, "AGP": 0.5}.get(key, 0.85)

    if key:
        epics = []
        for j, en in enumerate(EPIC_NAMES[key], 1):
            eid += 1
            pts = rng.choice([8, 13, 21, 21, 34])
            start = rng.uniform(-12, 12)            # epics finish at different times
            dl = (date.fromisoformat(ga) - timedelta(days=rng.randint(0, 60))).isoformat()
            tag = 'Onboarding' if 'onboarding' in en.lower() else None
            epics.append((eid, pts, start))
            cx.execute("INSERT INTO epics VALUES(?,?,?,?,?,?,?,?,?,?)",
                       (eid, pid, f"{key}-{10 + j * 3}", en, rng.choice(OWNERS), pts,
                        WEEKS[0], dl, 'In Progress', tag))
        for wi, w in enumerate(WEEKS):
            rows = []
            for (e_id, pts, start) in epics:
                planned_td = min(plan, plan * (wi + 1) / RAMP_N)
                pct = max(0.0, min(100.0, round(start + pace * planned_td * rng.uniform(0.7, 1.3), 1)))
                if wi and pct < prev_pct.get(e_id, 0):
                    pct = prev_pct[e_id]           # progress never goes backwards here
                prev_pct[e_id] = pct
                cx.execute("INSERT INTO epic_week VALUES(?,?,?)", (e_id, w, pct))
                rows.append((pct, pts))
            pct = round(sum(p * s for p, s in rows) / sum(s for _, s in rows), 1)
            planned = min(plan, round(plan * (wi + 1) / RAMP_N, 1))
            r = rag(round(pct - planned, 1))
            ndone = sum(1 for p, _ in rows if p >= 100)
            head = f"{name} at {pct}% (SP-weighted); {ndone} of {len(rows)} epics complete."
            cx.execute("INSERT INTO project_week VALUES(?,?,?,?,?,?,?,?,'auto')",
                       (pid, w, pct, planned, r, head,
                        "Focus next on the work closest to done.", CONF[r]))
        cx.execute("UPDATE epics SET status=CASE WHEN (SELECT pct FROM epic_week ew WHERE ew.epic_id=epics.id "
                   "AND ew.week=?)>=100 THEN 'Done' ELSE 'In Progress' END WHERE project_id=?",
                   (WEEKS[-1], pid))
    else:
        # mock project: a manually reported percentage, no epics
        for wi, w in enumerate(WEEKS):
            pct = round(min(100, pace * min(plan, plan * (wi + 1) / RAMP_N)), 1)
            planned = min(plan, round(plan * (wi + 1) / RAMP_N, 1))
            r = rag(round(pct - planned, 1))
            cx.execute("INSERT INTO project_week VALUES(?,?,?,?,?,?,?,?,'manual')",
                       (pid, w, pct, planned, r, f"{ws} at {pct}% (reported manually).",
                        "Update from the project lead at Monday's sync.", CONF[r]))

# Milestones for the board that has them configured (config.MILESTONES['DPF']).
dpf = cx.execute("SELECT id FROM projects WHERE jira_key='DPF'").fetchone()[0]
for wi, w in enumerate(WEEKS):
    for k, (label, _) in enumerate(milestones.defs_for('DPF')):
        if k == 3 and wi < 6:
            cx.execute("INSERT INTO milestone_week VALUES(?,?,?,NULL,NULL,0,0,0,0)", (dpf, w, label))
            continue
        pts = [40, 89, 76, 55][k]
        pct = round(max(0, min(100, [95, 55, 20, 2][k] * (wi + 1) / len(WEEKS))), 1)
        cx.execute("INSERT INTO milestone_week VALUES(?,?,?,?, 'points', ?, ?, ?, ?)",
                   (dpf, w, label, pct, 12, round(12 * pct / 100), pts, round(pts * pct / 100, 1)))

BARRIERS = [
    ("CFU", "Second clearinghouse contract not yet signed", "Fallback routing cannot be tested", "Morgan Lee", 1, "High", "Open", "2026-11-20", None),
    ("CFU", "Payer test environment returns stale statuses", "Two scenarios cannot be demoed", "Jordan Reyes", 3, "Med", "Resolved", "2026-10-16", 5),
    ("IDC", "Labelled training set below 2,000 documents", "Classifier accuracy stuck at baseline", "Priya Nair", 2, "High", "Open", "2026-11-13", None),
    ("PPS", "Policy source licence renewal pending", "Corpus refresh paused", "Dana Brooks", 4, "Med", "Open", "2026-11-06", None),
    ("OWB", "Design system components not yet accessible", "Accessibility epic blocked", "Chris Tan", 1, "Med", "Open", "2026-11-27", None),
    ("OWB", "Two engineers reassigned to incident work", "Velocity down ~30% for two sprints", "Morgan Lee", 5, "High", "Open", "2026-11-13", None),
    ("DPF", "Source system read replica not provisioned", "Billing ingestion cannot start", "Taylor Kim", 0, "High", "Resolved", "2026-09-25", 3),
    ("DPF", "Data retention policy awaiting compliance review", "Operator action ingestion scope unclear", "Riley Chen", 4, "Med", "Open", "2026-11-20", None),
]
for b_id, (key, barrier, impact, owner, wi, sev, st, target, res_wi) in enumerate(BARRIERS, 1):
    pid = cx.execute("SELECT id FROM projects WHERE jira_key=?", (key,)).fetchone()[0]
    cx.execute("INSERT INTO barriers VALUES(?,?,?,?,?,?,?,?,?,?,?)",
               (b_id, pid, barrier, impact, owner, WEEKS[wi], WEEKS[wi], sev, st, target,
                WEEKS[res_wi] if res_wi is not None else None))

con.commit()
counts = {t: cx.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
          for t in ['weeks', 'projects', 'project_week', 'epics', 'epic_week', 'barriers', 'milestone_week']}
con.close()
print(f"wrote {DB} with fictional demo data: {counts}")
print("next: python build_dashboard.py   (or JIRA_DEMO=1 python weekly.py 2026-11-06)")
