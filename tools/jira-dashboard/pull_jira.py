#!/usr/bin/env python3
"""Pull epics + child-issue rollup for a Jira project via the REST API.

This is the PURE-PYTHON path — no AI assistant, no MCP. It produces exactly the
JSON that apply_pull.py consumes, so it is a drop-in for an assistant-driven pull.

  python pull_jira.py <PROJECT_KEY> [output.json]
  python apply_pull.py <project_id> _jira_<PROJECT_KEY>.json

Credentials are read in this order:
  1. env vars: JIRA_EMAIL, JIRA_API_TOKEN, JIRA_SITE (e.g. yourcompany.atlassian.net)
  2. jira_config.json in this folder: {"email": "...", "api_token": "...", "site": "..."}

Create an API token at:
  https://id.atlassian.com/manage-profile/security/api-tokens
Keep it PRIVATE — do not commit jira_config.json or the token anywhere.

Set JIRA_DEMO=1 to skip Jira entirely and generate a fictional pull from tracker.db
(see demo_jira.py), so the whole weekly job can be tried without an account.

Uses only the Python standard library (urllib) — nothing to pip install.
"""
import sys, os, json, base64, urllib.request, urllib.error, urllib.parse

from milestones import labels_for
from config import PARENT_TYPES, STATUS_CREDIT

SP_FIELD = "customfield_10016"   # 'Story point estimate' on most Jira Cloud sites; check yours
CHILD_TYPES = "Story, Task, Bug, Spike"
AGILE = "/rest/agile/1.0"        # boards and sprints; the rest of the pull uses /api/3

# Distinct exit status for "the board exists but has no epics yet", so callers can
# tell a brand-new board (skip it quietly) from a vanished or misspelt one (fail).
EXIT_NO_EPICS = 3


def load_cfg():
    site = os.environ.get("JIRA_SITE")
    email = os.environ.get("JIRA_EMAIL")
    token = os.environ.get("JIRA_API_TOKEN")
    if not (email and token and site):
        try:
            c = json.load(open("jira_config.json", encoding="utf-8"))
            email = email or c.get("email")
            token = token or c.get("api_token")
            site = site or c.get("site")
        except FileNotFoundError:
            pass
    if not (email and token and site):
        sys.exit("Missing credentials: set JIRA_EMAIL + JIRA_API_TOKEN + JIRA_SITE env vars, "
                 "or create jira_config.json (see jira_config.example.json).")
    return site, email, "Basic " + base64.b64encode(f"{email}:{token}".encode()).decode()


def search(site, auth, jql, fields):
    """JQL search via /rest/api/3/search/jql with token pagination.

    The old /rest/api/3/search endpoint (startAt/total offset paging) was
    removed by Atlassian. The replacement returns an opaque nextPageToken and
    an isLast flag instead of a total count.
    """
    out, token = [], None
    while True:
        params = {
            "jql": jql,
            "fields": ",".join(fields) if isinstance(fields, list) else fields,
            "maxResults": 100,
        }
        if token:
            params["nextPageToken"] = token
        url = f"https://{site}/rest/api/3/search/jql?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(
            url, headers={"Authorization": auth, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req) as r:
                data = json.load(r)
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:300]
            sys.exit(f"Jira API error {e.code} for JQL [{jql}]:\n{detail}")
        except urllib.error.URLError as e:
            sys.exit(f"Network error reaching {site}: {e.reason}")
        out.extend(data.get("issues", []))
        token = data.get("nextPageToken")
        if data.get("isLast") or not token:
            break
    return out


def project_exists(site, auth, key):
    """True if the project is visible to this token; False on a 404."""
    req = urllib.request.Request(f"https://{site}/rest/api/3/project/{key}",
                                 headers={"Authorization": auth, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req):
            return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        sys.exit(f"Jira API error {e.code} checking project {key}: {e.read().decode()[:300]}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error reaching {site}: {e.reason}")


def keynum(issue):
    try:
        return int(issue["key"].split("-")[1])
    except Exception:
        return 0


def credit(status):
    """Fraction of an issue's effort to count as delivered. See config.STATUS_CREDIT.

    Status NAME wins, because statuses that share a category can deserve different
    credit ('In Progress' and 'In Review' are both 'indeterminate'). Anything not
    named falls back to the category: 'done' -> 1.0, everything else -> 0.0.
    """
    st = status or {}
    name = st.get("name")
    if name in STATUS_CREDIT:
        return float(STATUS_CREDIT[name])
    return 1.0 if ((st.get("statusCategory") or {}).get("key") == "done") else 0.0


def soft_get(site, auth, path):
    """GET that returns None instead of exiting. For data we can do without."""
    req = urllib.request.Request(f"https://{site}{path}",
                                 headers={"Authorization": auth, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except (urllib.error.HTTPError, urllib.error.URLError):
        return None


def sprint_goal(site, auth, key):
    """The active sprint's goal for a board -> {"name", "goal"}, or None.

    Sprint goals live on the Agile API (/rest/agile/1.0), not the issue search that
    feeds everything else, and many boards leave the goal blank.

    Strictly best-effort by design: no agile board, no active sprint, an empty goal,
    a permissions problem or a flaky endpoint all return None, and the caller falls
    back to the generated steps line. This must never raise -- advance_week.py rolls
    back the entire week when a pull fails, and a missing sprint goal is not a reason
    to cost every other project its week.
    """
    boards = soft_get(site, auth, f"{AGILE}/board?projectKeyOrId={key}") or {}
    for b in boards.get("values", []):
        sprints = soft_get(site, auth, f"{AGILE}/board/{b['id']}/sprint?state=active") or {}
        for s in sprints.get("values", []):
            goal = (s.get("goal") or "").strip()
            if goal:
                return {"name": s.get("name") or "Current sprint", "goal": goal}
    return None


def milestone_rollup(site, auth, key, labels, kids):
    """Completion per milestone label, SP-weighted, from the labels in Jira.

    Scope for one label = every issue carrying it, with one substitution: a label on
    an EPIC contributes that epic's CHILDREN instead of the epic row itself. Epics
    usually carry no story points, so counting the container would add a 0-point row
    and leave all the real work underneath it invisible. Children come from the set
    already used for the project %, so a milestone figure is directly comparable to
    the project figure it sits beside.

    Returns one row per CONFIGURED label, in order, including labels nothing carries
    — those come back pct=None ('not yet labelled'), which is a different statement
    from 0% and is reported as such.
    """
    if not labels:
        return []
    by_parent = {}
    for k in kids:
        parent = (k["fields"].get("parent") or {}).get("key")
        if parent:
            by_parent.setdefault(parent, []).append(k)

    # One query for every milestone label, then split locally: an issue can carry
    # more than one, so it may legitimately count toward several milestones.
    quoted = ",".join('"%s"' % l.replace('"', '') for l in labels)
    tagged = search(site, auth, f"project = {key} AND labels in ({quoted})",
                    ["labels", "issuetype", "status", SP_FIELD])

    out = []
    for label in labels:
        members = {}             # issue key -> fields, deduped (epics can share children)
        direct = epics_used = 0
        for i in tagged:
            f = i["fields"]
            if label not in (f.get("labels") or []):
                continue
            direct += 1
            if (f.get("issuetype") or {}).get("name") == "Epic":
                epics_used += 1
                for c in by_parent.get(i["key"], []):
                    members[c["key"]] = c["fields"]
            else:
                members[i["key"]] = f

        pts = done_pts = cred = 0.0
        n = ndone = 0
        for f in members.values():
            sp = f.get(SP_FIELD) or 0
            cr = credit(f.get("status"))
            pts += sp
            n += 1
            done_pts += sp * cr      # credited effort, so it always equals pct x pts
            cred += cr
            if cr >= 1.0:
                ndone += 1           # strict count of finished issues, for display

        if pts:
            pct, basis = round(100 * done_pts / pts, 1), "points"
        elif n:
            # Scope exists but is entirely unpointed: fall back to issue count so the
            # milestone reads as real progress rather than a spurious 0%.
            pct, basis = round(100 * cred / n, 1), "count"
        else:
            pct, basis = None, None

        out.append({"label": label, "pct": pct, "basis": basis,
                    "issues": n, "done_issues": ndone,
                    "pts": pts, "done_pts": done_pts,
                    "tagged": direct, "tagged_epics": epics_used})
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python pull_jira.py <PROJECT_KEY> [output.json]")
    KEY = sys.argv[1].upper()
    outfile = sys.argv[2] if len(sys.argv) > 2 else f"_jira_{KEY}.json"
    if os.environ.get("JIRA_DEMO"):
        # Offline demo: fictional data from tracker.db, no credentials, no network.
        import demo_jira
        demo_jira.write_pull(KEY, outfile, EXIT_NO_EPICS)
        return
    site, email, auth = load_cfg()

    parent_type = PARENT_TYPES.get(KEY, "Epic")
    epics = search(site, auth,
                   f'project = {KEY} AND issuetype = "{parent_type}" ORDER BY created ASC',
                   ["summary", "assignee", "duedate"])
    # Jira's search API returns an empty set (not an error) for an unknown project,
    # so zero epics is ambiguous: a vanished/renamed key, or a real board nobody has
    # planned yet. Ask the project endpoint which. Either way nothing is written —
    # that is what stops an empty board appearing on the dashboard as a real 0% —
    # but only a missing board is a failure; an empty one exits EXIT_NO_EPICS so the
    # weekly job skips it without holding up everyone else's week.
    if not epics:
        if project_exists(site, auth, KEY):
            print(f"{KEY}: board exists but has no {parent_type} issues yet - "
                  f"nothing to report. It joins the dashboard once it has one.")
            sys.exit(EXIT_NO_EPICS)
        sys.exit(f"No epics found for project {KEY} and the project was not found "
                 f"(https://{site}/rest/api/3/project/{KEY}). Check the key. "
                 f"Refusing to write a 0% pull.")
    kids = search(site, auth,
                  f"project = {KEY} AND issuetype in ({CHILD_TYPES}) "
                  f"AND parent is not EMPTY ORDER BY parent ASC",
                  ["status", "parent", SP_FIELD, "duedate"])

    agg = {}
    for k in kids:
        f = k["fields"]
        parent = (f.get("parent") or {}).get("key")
        if not parent:
            continue
        sp = f.get(SP_FIELD) or 0
        cr = credit(f.get("status"))
        due = f.get("duedate")
        a = agg.setdefault(parent, {"total": 0.0, "done": 0.0, "n": 0, "ndone": 0,
                                    "cred": 0.0, "latest": None})
        a["total"] += sp; a["n"] += 1
        a["done"] += sp * cr       # effort-weighted credit -> drives the percentage
        a["cred"] += cr            # issue-weighted credit -> 0-point fallback only
        if cr >= 1.0:
            # Strict count of fully-finished issues, kept separate from "cred" so the
            # "x of y issues" shown to readers never reads as a fraction of an issue.
            a["ndone"] += 1
        if due and (a["latest"] is None or due > a["latest"]):
            a["latest"] = due

    result = []
    for e in sorted(epics, key=keynum):
        f = e["fields"]
        a = agg.get(e["key"], {"total": 0.0, "done": 0.0, "n": 0, "ndone": 0,
                               "cred": 0.0, "latest": None})
        pct = round(100 * a["done"] / a["total"], 1) if a["total"] else 0.0
        result.append({
            "key": e["key"],
            "name": f.get("summary", ""),
            "owner": (f.get("assignee") or {}).get("displayName") or "Unassigned",
            "pts": a["total"],
            "cur_pct": pct,
            "epic_due": f.get("duedate"),
            "latest_child_due": a["latest"],
            "children": a["n"],
            "done_children": a["ndone"],
            # Credit-weighted child count. eff_pct() uses this instead of
            # done_children for 0-point epics, so partial credit reaches the
            # unpointed boards too and not just the pointed ones.
            "credit_children": round(a["cred"], 3),
        })

    ms = milestone_rollup(site, auth, KEY, labels_for(KEY), kids)
    sg = sprint_goal(site, auth, KEY)

    # Object, not a bare array, so milestones travel with the epics in one file.
    # apply_pull.py and advance_week.py both still accept the old array form.
    json.dump({"epics": result, "milestones": ms, "sprint": sg},
              open(outfile, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    tot = sum(r["pts"] for r in result)
    done = sum(r["pts"] * r["cur_pct"] / 100 for r in result)
    overall = round(100 * done / tot, 1) if tot else 0.0
    print(f"{KEY}: {len(result)} epics, {tot:g} story points, ~{overall}% SP-weighted -> {outfile}")
    print(f"  sprint goal: {sg['name']} - {sg['goal']}" if sg else
          "  sprint goal: none set - steps will come from epic completion instead")
    for m in ms:
        if m["pct"] is None:
            print(f"  {m['label']}: not yet labelled - no {KEY} issue carries this label")
        else:
            scope = (f"{m['done_pts']:g}/{m['pts']:g}sp" if m["basis"] == "points"
                     else f"{m['done_issues']}/{m['issues']} issues, unpointed")
            print(f"  {m['label']}: {m['pct']}% ({scope} over {m['issues']} issues"
                  f" from {m['tagged']} labelled)")
    print(f"next: python apply_pull.py <project_id> {outfile}")


if __name__ == "__main__":
    main()
