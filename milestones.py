#!/usr/bin/env python3
"""Per-week milestone progress: storage, and the definitions it is keyed against.

Milestone percentages are STORED per reporting week, not computed at render time.
That is the same rule the rest of the dashboard follows: a locked week is a frozen
snapshot, so its milestone figures must be the ones measured that week, not
whatever Jira happens to say the next time someone runs a build. It also keeps
build_dashboard.py credential-free — it only ever reads tracker.db.

The deliverable text lives in config.MILESTONES, never in the database: only the
measurements are stored, keyed by (project, week, label). Reword a deliverable
and every historical week picks up the new wording, which is what you want for a
typo; see the note in config.py for why renaming a *label* is different.

  from milestones import ensure, labels_for, write, read
"""
from config import MILESTONES

DDL = """
CREATE TABLE IF NOT EXISTS milestone_week(
    project_id  INTEGER NOT NULL,
    week        TEXT    NOT NULL,
    label       TEXT    NOT NULL,   -- the Jira label; the join key, never displayed
    pct         REAL,               -- NULL = nothing in Jira carries this label
    basis       TEXT,               -- 'points' | 'count' (0-point scope) | NULL
    issues      INTEGER NOT NULL DEFAULT 0,
    done_issues INTEGER NOT NULL DEFAULT 0,
    pts         REAL    NOT NULL DEFAULT 0,
    done_pts    REAL    NOT NULL DEFAULT 0,
    PRIMARY KEY (project_id, week, label)
)"""


def ensure(cx):
    """Create the table if this is the first run against an older tracker.db."""
    cx.execute(DDL)


def defs_for(jira_key):
    """[(label, deliverable)] for a board, in display order. [] if not configured."""
    return MILESTONES.get((jira_key or '').upper(), [])


def labels_for(jira_key):
    return [label for label, _ in defs_for(jira_key)]


def write(cx, project_id, week, rows):
    """Replace this project/week's milestone rows with `rows` from a Jira pull.

    Only the target week is touched, so prior locked weeks keep the numbers they
    were locked with. Rows for labels no longer configured are deleted rather than
    left behind, otherwise a removed milestone would linger in the stored week
    while being absent from the rendered panel.
    """
    ensure(cx)
    cx.execute("DELETE FROM milestone_week WHERE project_id=? AND week=?", (project_id, week))
    for m in rows:
        cx.execute("""INSERT INTO milestone_week
                      (project_id,week,label,pct,basis,issues,done_issues,pts,done_pts)
                      VALUES(?,?,?,?,?,?,?,?,?)""",
                   (project_id, week, m['label'], m.get('pct'), m.get('basis'),
                    m.get('issues') or 0, m.get('done_issues') or 0,
                    m.get('pts') or 0, m.get('done_pts') or 0))


def read(cx, project_id, week, jira_key):
    """Milestones for one project-week, in configured order, joined to their text.

    Returns [] — render no panel at all — in two cases: the board has no milestones
    configured, or this week has no stored rows whatsoever. The second case is a week
    locked before milestones were tracked; showing 'not yet labelled' rows there
    would claim Jira had no labels that week, when the truth is that nobody measured.
    Once a week has any rows, a configured label missing from them comes back pct=None
    and IS reported as not-yet-labelled, which by then is a real finding.
    """
    defs = defs_for(jira_key)
    if not defs:
        return []
    ensure(cx)
    have = {r['label']: r for r in cx.execute(
        "SELECT * FROM milestone_week WHERE project_id=? AND week=?", (project_id, week))}
    if not have:
        return []
    out = []
    for label, text in defs:
        r = have.get(label)
        out.append(dict(
            label=label, text=text,
            pct=(round(r['pct'], 1) if r and r['pct'] is not None else None),
            basis=(r['basis'] if r else None),
            issues=(r['issues'] if r else 0),
            doneIssues=(r['done_issues'] if r else 0),
            pts=(r['pts'] if r else 0),
            donePts=(r['done_pts'] if r else 0),
        ))
    return out
