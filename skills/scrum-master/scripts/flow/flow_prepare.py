#!/usr/bin/env python3
"""Turn an export from Jira, Azure DevOps or a CSV file into flow data, and make it anonymous.

  python flow_prepare.py jira  export.json  -o flow.json [--team-from project|component|field:ID]
  python flow_prepare.py ado   updates.json -o flow.json
  python flow_prepare.py csv   history.csv  -o flow.json
  python flow_prepare.py flow  flow.json    -o flow-anon.json      # anonymize flow data again

Options:
  --anonymize            Replace ids with hashes and team names with "Team 1", "Team 2" and so on.
                         Remove summaries, people and labels.
  --keep-labels A,B      With --anonymize: keep only these labels (for example dor-met,MS1).
  --salt TEXT            The salt for the hashes. Without it, the script uses a random salt and
                         does not write it, so nobody can reverse the hashes.
  --suggest-map map.json Also write a first status map, and print the list of statuses.

Inputs:
  jira  A Jira search response with the changelog: {"issues": [...]} from
        /rest/api/3/search/jql?expand=changelog, the output of pull_jira_flow.py, or a list of
        issues. Each issue has "changelog": {"histories": [...]} or {"values": [...]}.
  ado   Azure DevOps work item updates: a list of {"id": 12, "updates": [...]}, or
        {"value": [...]} with "workItemId" in each update (GET _apis/wit/workitems/{id}/updates).
  csv   Either one row for each transition (id, type, team, created, from, to, at), or one row
        for each revision (id, type, team, state, changed), for example from the Azure DevOps
        Analytics view WorkItemRevisions or a Jira status-history export. The script finds the
        shape from the header. It accepts common column names (key, WorkItemId, status, State,
        ChangedDate, timestamp, issuetype, WorkItemType, project, AreaPath).

Standard library only.
"""
import argparse
import csv
import hashlib
import json
import os
import secrets
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flowlib as fl  # noqa: E402


# --------------------------------------------------------------------------- Jira

def _field_text(v):
    if v is None:
        return ""
    if isinstance(v, dict):
        return v.get("name") or v.get("value") or v.get("title") or v.get("key") or ""
    if isinstance(v, list):
        return _field_text(v[0]) if v else ""
    return str(v)


def from_jira(data, team_from="project"):
    issues = data.get("issues", data) if isinstance(data, dict) else data
    items, warnings = [], []
    for iss in issues:
        f = iss.get("fields", {})
        if team_from == "project":
            team = _field_text(f.get("project")) or iss.get("key", "").split("-")[0]
            if isinstance(f.get("project"), dict):
                team = f["project"].get("key") or team
        elif team_from == "component":
            team = _field_text(f.get("components"))
        elif team_from.startswith("field:"):
            team = _field_text(f.get(team_from.split(":", 1)[1]))
        else:
            team = ""
        cl = iss.get("changelog") or {}
        hist = cl.get("histories") or cl.get("values") or []
        total = cl.get("total")
        if total is not None and total > len(hist):
            warnings.append(f"{iss.get('key')}: the changelog has {total} entries, but the export has "
                            f"{len(hist)}. Use pull_jira_flow.py, which gets the full changelog.")
        trs = []
        for h in hist:
            for ch in h.get("items", []):
                if ch.get("field") == "status" or ch.get("fieldId") == "status":
                    trs.append({"at": h.get("created"), "from": ch.get("fromString"),
                                "to": ch.get("toString")})
        items.append({
            "id": iss.get("key") or iss.get("id"),
            "summary": f.get("summary"),
            "type": _field_text(f.get("issuetype")) or "Item",
            "team": team,
            "created": f.get("created"),
            "status": _field_text(f.get("status")) or None,
            "labels": f.get("labels") or [],
            "transitions": trs,
        })
    return items, warnings


# --------------------------------------------------------------------------- Azure DevOps

def _ado_new(fields, name):
    v = fields.get(name)
    if isinstance(v, dict):
        return v.get("newValue"), v.get("oldValue")
    return None, None


def from_ado(data):
    groups = {}
    if isinstance(data, dict) and "value" in data:
        for up in data["value"]:
            groups.setdefault(up.get("workItemId") or up.get("id"), []).append(up)
    else:
        for wi in data:
            groups[wi.get("id")] = wi.get("updates", [])
    items = []
    for wid, ups in groups.items():
        ups = sorted(ups, key=lambda u: u.get("rev") or u.get("id") or 0)
        item = {"id": str(wid), "type": "Item", "team": "", "created": None, "status": None,
                "labels": [], "transitions": []}
        for up in ups:
            f = up.get("fields") or {}
            changed, _ = _ado_new(f, "System.ChangedDate")
            created, _ = _ado_new(f, "System.CreatedDate")
            wtype, _ = _ado_new(f, "System.WorkItemType")
            area, _ = _ado_new(f, "System.AreaPath")
            title, _ = _ado_new(f, "System.Title")
            tags, _ = _ado_new(f, "System.Tags")
            new_state, old_state = _ado_new(f, "System.State")
            if created and not item["created"]:
                item["created"] = created
            if wtype:
                item["type"] = wtype
            if area:
                item["team"] = str(area).split("\\")[-1]
            if title:
                item["summary"] = title
            if tags is not None:
                item["labels"] = [t.strip() for t in str(tags).split(";") if t.strip()]
            if new_state is not None:
                if old_state is not None:
                    item["transitions"].append({"at": changed or up.get("revisedDate"),
                                                "from": old_state, "to": new_state})
                elif item["status"] is not None and item["status"] != new_state:
                    item["transitions"].append({"at": changed, "from": item["status"],
                                                "to": new_state})
                item["status"] = new_state
        if not item["created"] and ups:
            item["created"] = _ado_new(ups[0].get("fields") or {}, "System.ChangedDate")[0]
        items.append(item)
    return items, []


# --------------------------------------------------------------------------- CSV

ALIASES = {
    "id": ["id", "key", "issue", "issuekey", "issue key", "workitemid", "work item id"],
    "type": ["type", "issuetype", "issue type", "workitemtype", "work item type"],
    "team": ["team", "project", "areapath", "area path", "board"],
    "created": ["created", "createddate", "created date"],
    "from": ["from", "from_status", "from status", "fromstring"],
    "to": ["to", "to_status", "to status", "tostring"],
    "at": ["at", "timestamp", "changed", "changeddate", "changed date", "date", "transition date"],
    "state": ["state", "status"],
    "labels": ["labels", "tags"],
}


def _columns(header):
    low = {h.strip().lower(): h for h in header}
    cols = {}
    for key, names in ALIASES.items():
        for n in names:
            if n in low:
                cols[key] = low[n]
                break
    return cols


def from_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return [], ["The CSV file has no rows."]
    cols = _columns(rows[0].keys())
    if "id" not in cols:
        sys.exit(f"The CSV file has no id column. Columns: {list(rows[0].keys())}")
    get = lambda r, k: (r.get(cols[k]) or "").strip() if k in cols else ""  # noqa: E731
    items = {}
    transition_shape = "from" in cols and "to" in cols
    if not transition_shape and "state" not in cols:
        sys.exit("The CSV file needs from and to columns, or a state column.")
    for r in rows:
        iid = get(r, "id")
        it = items.setdefault(iid, {"id": iid, "type": get(r, "type") or "Item",
                                    "team": get(r, "team").split("\\")[-1], "created": get(r, "created") or None,
                                    "status": None, "labels": [], "transitions": [], "_rev": []})
        if get(r, "labels"):
            it["labels"] = [x.strip() for x in get(r, "labels").replace(";", ",").split(",") if x.strip()]
        if transition_shape:
            if get(r, "to"):
                it["transitions"].append({"at": get(r, "at"), "from": get(r, "from") or None,
                                          "to": get(r, "to")})
        else:
            it["_rev"].append((fl.parse_time(get(r, "at")), get(r, "state")))
    out = []
    for it in items.values():
        revs = sorted((t, s) for t, s in it.pop("_rev") if t)
        if revs:
            it["created"] = it["created"] or fl.iso(revs[0][0])
            prev = revs[0][1]
            for t, s in revs[1:]:
                if s != prev:
                    it["transitions"].append({"at": fl.iso(t), "from": prev, "to": s})
                    prev = s
            it["status"] = prev
        elif it["transitions"]:
            it["transitions"].sort(key=lambda x: fl.parse_time(x["at"]))
            it["status"] = it["transitions"][-1]["to"]
            it["created"] = it["created"] or it["transitions"][0]["at"]
        out.append(it)
    return out, []


# --------------------------------------------------------------------------- anonymize

def anonymize(items, salt=None, keep_labels=()):
    salt = salt or secrets.token_hex(16)
    teams = {}
    out = []
    for it in items:
        h = hashlib.sha256((salt + str(it.get("id"))).encode()).hexdigest()[:10]
        team = it.get("team") or ""
        if team and team not in teams:
            teams[team] = f"Team {len(teams) + 1}"
        out.append({
            "id": f"I-{h}",
            "type": it.get("type") or "Item",
            "team": teams.get(team, ""),
            "created": it.get("created"),
            "status": it.get("status"),
            "labels": [l for l in it.get("labels", []) if l in set(keep_labels)],
            "transitions": [{"at": t["at"], "from": t["from"], "to": t["to"]}
                            for t in it.get("transitions", [])],
        })
    return out


def _jsonable(items):
    for it in items:
        if isinstance(it.get("created"), fl.dt.datetime):
            it["created"] = fl.iso(it["created"])
        for t in it.get("transitions", []):
            if isinstance(t.get("at"), fl.dt.datetime):
                t["at"] = fl.iso(t["at"])
    return items


def status_inventory(items):
    c = Counter()
    for it in items:
        seen = set()
        for t in it["transitions"]:
            seen.update([t["from"], t["to"]])
        if it.get("status"):
            seen.add(it["status"])
        for s in seen:
            if s:
                c[s] += 1
    return c


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", choices=["jira", "ado", "csv", "flow"])
    ap.add_argument("input")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--team-from", default="project")
    ap.add_argument("--anonymize", action="store_true")
    ap.add_argument("--keep-labels", default="")
    ap.add_argument("--salt")
    ap.add_argument("--suggest-map")
    a = ap.parse_args(argv)

    if a.source == "jira":
        items, warnings = from_jira(fl.load_json(a.input), a.team_from)
    elif a.source == "ado":
        items, warnings = from_ado(fl.load_json(a.input))
    elif a.source == "csv":
        items, warnings = from_csv(a.input)
    else:
        data = fl.load_json(a.input)
        items, warnings = (data.get("items", data) if isinstance(data, dict) else data), []

    if a.anonymize:
        keep = [x.strip() for x in a.keep_labels.split(",") if x.strip()]
        items = anonymize(_jsonable(items), a.salt, keep)

    out = {"source": a.source, "anonymized": bool(a.anonymize), "items": _jsonable(items)}
    with open(a.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(f"Wrote {len(items)} items to {a.output}"
          + (" (anonymized)" if a.anonymize else " (NOT anonymized: do not share this file)"))
    for w in warnings[:20]:
        print("WARNING:", w)
    if len(warnings) > 20:
        print(f"WARNING: {len(warnings) - 20} more warnings.")

    if a.suggest_map:
        flow = fl.load_flow(a.output)
        smap = fl.suggest_map(flow["items"])
        with open(a.suggest_map, "w", encoding="utf-8") as f:
            json.dump(smap, f, indent=2)
        print(f"\nWrote a draft status map to {a.suggest_map}. Review it before you use it.")
        print("\nStatus                          Items  Guessed kind")
        for s, n in status_inventory(flow["items"]).most_common():
            print(f"{s[:30]:<30}  {n:>6}  {fl.guess_kind(s)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
