#!/usr/bin/env python3
"""Get the status history of Jira items, for the flow scripts. It only reads.

  python pull_jira_flow.py "project in (CLM, ELG, PAY) AND updated >= -26w" -o flow-data/jira.json
  JIRA_DEMO=1 python pull_jira_flow.py "any" -o flow-data/jira.json   # fictional data, no Jira

Then:
  python flow_prepare.py jira flow-data/jira.json -o flow-data/flow.json --anonymize --suggest-map flow-data/map.json

Credentials, in this order (the same as tools/jira-dashboard/pull_jira.py):
  1. The environment variables JIRA_EMAIL, JIRA_API_TOKEN and JIRA_SITE (yourcompany.atlassian.net).
  2. A jira_config.json file in the current folder: {"email", "api_token", "site"}.
The script never prints the token.

The script uses the JQL search (/rest/api/3/search/jql) for the items, and the changelog of
each item (/rest/api/3/issue/{key}/changelog) for the full status history. The output has raw
item data, with summaries. Keep it in a folder that git ignores (flow-data/), and anonymize it
with flow_prepare.py before you share it. Standard library only.
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = "summary,issuetype,status,created,labels,project,components"


def load_cfg():
    site, email, token = (os.environ.get(k) for k in ("JIRA_SITE", "JIRA_EMAIL", "JIRA_API_TOKEN"))
    if not (site and email and token) and os.path.exists("jira_config.json"):
        with open("jira_config.json", encoding="utf-8") as f:
            c = json.load(f)
        site, email, token = site or c.get("site"), email or c.get("email"), token or c.get("api_token")
    if not (site and email and token):
        sys.exit("Missing credentials: set JIRA_EMAIL, JIRA_API_TOKEN and JIRA_SITE, or make jira_config.json.")
    return site, "Basic " + base64.b64encode(f"{email}:{token}".encode()).decode()


def get(site, auth, path, params):
    url = f"https://{site}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": auth, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Jira API error {e.code} for {path}: {e.read().decode()[:300]}")
    except urllib.error.URLError as e:
        sys.exit(f"Cannot connect to {site}: {e.reason}")


def search(site, auth, jql, limit):
    issues, token = [], None
    while True:
        params = {"jql": jql, "fields": FIELDS, "maxResults": 100}
        if token:
            params["nextPageToken"] = token
        data = get(site, auth, "/rest/api/3/search/jql", params)
        issues += data.get("issues", [])
        token = data.get("nextPageToken")
        if data.get("isLast", not token) or not token or (limit and len(issues) >= limit):
            return issues[:limit] if limit else issues


def changelog(site, auth, key):
    values, start = [], 0
    while True:
        data = get(site, auth, f"/rest/api/3/issue/{key}/changelog", {"startAt": start, "maxResults": 100})
        values += data.get("values", [])
        start += data.get("maxResults", 100)
        if data.get("isLast", True) or start >= data.get("total", 0):
            return values


def demo():
    sys.path.insert(0, HERE)
    import demo_flow
    issues = []
    for it in demo_flow.simulate():
        hist = [{"created": t["at"], "items": [{"field": "status", "fromString": t["from"],
                                                "toString": t["to"]}]} for t in it["transitions"]]
        issues.append({"key": it["id"], "fields": {
            "summary": f"Fictional item {it['id']}", "issuetype": {"name": it["type"]},
            "status": {"name": it["status"]}, "created": it["created"], "labels": it["labels"],
            "project": {"key": it["team"]}}, "changelog": {"values": hist}})
    return issues


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jql")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--limit", type=int, default=0, help="the most items to get (0 = all)")
    a = ap.parse_args(argv)
    if os.environ.get("JIRA_DEMO") == "1":
        issues = demo()
        print(f"Demo mode: {len(issues)} fictional items.")
    else:
        site, auth = load_cfg()
        issues = search(site, auth, a.jql, a.limit)
        print(f"Found {len(issues)} items. Getting the changelog of each item.")
        for i, iss in enumerate(issues, 1):
            iss["changelog"] = {"values": changelog(site, auth, iss["key"])}
            if i % 50 == 0:
                print(f"  {i} of {len(issues)}")
    os.makedirs(os.path.dirname(os.path.abspath(a.output)), exist_ok=True)
    with open(a.output, "w", encoding="utf-8") as f:
        json.dump({"issues": issues}, f)
    print(f"Wrote {a.output}. It has summaries: anonymize it with flow_prepare.py before you share it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
