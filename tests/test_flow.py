"""Tests for skills/scrum-master/scripts/flow/. Run: python -m pytest tests"""
import csv
import json
import pathlib
import random
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "scrum-master"
FLOW = SKILL / "scripts" / "flow"
sys.path.insert(0, str(FLOW))

import cfd  # noqa: E402
import flow_prepare as fp  # noqa: E402
import flow_report as fr  # noqa: E402
import flowlib as fl  # noqa: E402
import wip_sim as ws  # noqa: E402

SAMPLE = SKILL / "assets" / "sample_flow_data.json"
MAP = SKILL / "assets" / "sample_status_map.json"
MODEL = SKILL / "assets" / "sample_flow_model.json"

SMAP = fl.StatusMap({
    "stages": [
        {"name": "Backlog", "kind": "backlog", "statuses": ["To Do"]},
        {"name": "Dev", "kind": "active", "statuses": ["In Progress", "Coding"]},
        {"name": "Ready for Test", "kind": "wait", "statuses": ["Ready for QA"]},
        {"name": "Test", "kind": "active", "statuses": ["In QA"]},
        {"name": "Done", "kind": "done", "statuses": ["Done"]},
    ],
    "blocked": ["Blocked"],
    "discarded": ["Won't Do"],
})


def item(iid, *steps, created="2026-01-05T09:00:00Z", **extra):
    """steps: (iso time, to status). The first from-status is To Do."""
    trs, cur = [], "To Do"
    for at, to in steps:
        trs.append({"at": at, "from": cur, "to": to})
        cur = to
    d = {"id": iid, "type": "Story", "team": "A", "created": created, "status": cur,
         "labels": [], "transitions": trs}
    d.update(extra)
    return d


def flow_of(*items):
    data = {"items": [json.loads(json.dumps(i)) for i in items]}
    for it in data["items"]:
        it["created"] = fl.parse_time(it["created"])
        for t in it["transitions"]:
            t["at"] = fl.parse_time(t["at"])
    return data


# --------------------------------------------------------------------------- flowlib

def test_parse_time_accepts_jira_offset_without_colon():
    t = fl.parse_time("2026-05-04T10:15:00.000+0200")
    assert t.isoformat() == "2026-05-04T08:15:00+00:00"


def test_days_between_workdays_skips_the_weekend():
    fri = fl.parse_time("2026-01-09T12:00:00Z")
    mon = fl.parse_time("2026-01-12T12:00:00Z")
    assert abs(fl.days_between(fri, mon) - 3.0) < 1e-9
    assert abs(fl.days_between(fri, mon, workdays=True) - 1.0) < 1e-9


def test_guess_kind_handles_common_status_names():
    assert fl.guess_kind("Ready for QA") == "wait"
    assert fl.guess_kind("Dev Complete") == "wait"
    assert fl.guess_kind("Closed") == "done"
    assert fl.guess_kind("Won't Do") == "discarded"
    assert fl.guess_kind("On Hold") == "blocked"
    assert fl.guess_kind("Backlog") == "backlog"
    assert fl.guess_kind("Code Review") == "active"


def test_analyze_item_splits_active_and_wait_time():
    it = flow_of(item("X-1",
                      ("2026-01-05T09:00:00Z", "In Progress"),   # Mon
                      ("2026-01-07T09:00:00Z", "Ready for QA"),  # 2 days active
                      ("2026-01-10T09:00:00Z", "In QA"),         # 3 days wait
                      ("2026-01-11T09:00:00Z", "Done")))["items"][0]  # 1 day active
    r = fl.analyze_item(it, SMAP, fl.parse_time("2026-02-01T00:00:00Z"))
    assert abs(r["flow_days"] - 6) < 1e-9
    assert abs(r["active_days"] - 3) < 1e-9
    assert abs(r["wait_days"] - 3) < 1e-9
    assert abs(r["efficiency"] - 0.5) < 1e-9
    assert r["backward_moves"] == 0


def test_analyze_item_counts_rework_and_blocked_time():
    it = flow_of(item("X-2",
                      ("2026-01-05T09:00:00Z", "In Progress"),
                      ("2026-01-06T09:00:00Z", "Blocked"),
                      ("2026-01-08T09:00:00Z", "In Progress"),
                      ("2026-01-09T09:00:00Z", "In QA"),
                      ("2026-01-10T09:00:00Z", "Coding"),
                      ("2026-01-11T09:00:00Z", "In QA"),
                      ("2026-01-12T09:00:00Z", "Done")))["items"][0]
    r = fl.analyze_item(it, SMAP, fl.parse_time("2026-02-01T00:00:00Z"))
    assert r["backward_moves"] == 1
    assert abs(r["stage_days"][fl.BLOCKED] - 2) < 1e-9
    assert abs(r["wait_days"] - 2) < 1e-9


# --------------------------------------------------------------------------- flow_prepare

def test_jira_export_becomes_flow_data_and_anonymize_removes_names():
    export = {"issues": [{
        "key": "ACME-7",
        "fields": {"summary": "Secret customer feature", "issuetype": {"name": "Story"},
                   "status": {"name": "Done"}, "created": "2026-01-05T09:00:00.000+0000",
                   "labels": ["dor-met", "customer-acme"], "project": {"key": "ACME"}},
        "changelog": {"histories": [
            {"created": "2026-01-06T09:00:00.000+0000",
             "items": [{"field": "status", "fromString": "To Do", "toString": "In Progress"},
                       {"field": "assignee", "fromString": None, "toString": "Pat"}]},
            {"created": "2026-01-08T09:00:00.000+0000",
             "items": [{"field": "status", "fromString": "In Progress", "toString": "Done"}]}]},
    }]}
    items, warnings = fp.from_jira(export)
    assert warnings == []
    assert items[0]["team"] == "ACME"
    assert [t["to"] for t in items[0]["transitions"]] == ["In Progress", "Done"]
    anon = fp.anonymize(items, salt="s", keep_labels=["dor-met"])
    text = json.dumps(anon)
    assert "ACME" not in text and "Secret" not in text and "Pat" not in text
    assert anon[0]["labels"] == ["dor-met"]
    assert anon[0]["team"] == "Team 1"
    assert anon[0]["id"].startswith("I-")


def test_jira_export_warns_when_the_changelog_is_cut():
    export = {"issues": [{"key": "A-1", "fields": {"created": "2026-01-05T09:00:00Z"},
                          "changelog": {"histories": [], "total": 120, "maxResults": 100}}]}
    _, warnings = fp.from_jira(export)
    assert warnings and "pull_jira_flow.py" in warnings[0]


def test_ado_updates_become_transitions():
    data = [{"id": 12, "updates": [
        {"rev": 1, "fields": {"System.State": {"newValue": "New"},
                              "System.CreatedDate": {"newValue": "2026-01-05T09:00:00Z"},
                              "System.ChangedDate": {"newValue": "2026-01-05T09:00:00Z"},
                              "System.WorkItemType": {"newValue": "User Story"},
                              "System.AreaPath": {"newValue": "Train\\Team Blue"}}},
        {"rev": 2, "fields": {"System.State": {"oldValue": "New", "newValue": "Active"},
                              "System.ChangedDate": {"newValue": "2026-01-06T09:00:00Z"}}},
        {"rev": 3, "fields": {"System.Title": {"newValue": "x"}}},
        {"rev": 4, "fields": {"System.State": {"oldValue": "Active", "newValue": "Closed"},
                              "System.ChangedDate": {"newValue": "2026-01-09T09:00:00Z"}}}]}]
    items, _ = fp.from_ado(data)
    it = items[0]
    assert it["team"] == "Team Blue" and it["type"] == "User Story"
    assert [(t["from"], t["to"]) for t in it["transitions"]] == [("New", "Active"), ("Active", "Closed")]


def test_csv_revisions_and_transitions_give_the_same_flow(tmp_path):
    rev = tmp_path / "rev.csv"
    with open(rev, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["WorkItemId", "WorkItemType", "State", "ChangedDate"])
        w.writerows([[1, "Story", "To Do", "2026-01-05T09:00:00Z"],
                     [1, "Story", "To Do", "2026-01-05T10:00:00Z"],
                     [1, "Story", "In Progress", "2026-01-06T09:00:00Z"],
                     [1, "Story", "Done", "2026-01-08T09:00:00Z"]])
    trs = tmp_path / "trs.csv"
    with open(trs, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "type", "created", "from", "to", "timestamp"])
        w.writerows([["1", "Story", "2026-01-05T09:00:00Z", "To Do", "In Progress", "2026-01-06T09:00:00Z"],
                     ["1", "Story", "2026-01-05T09:00:00Z", "In Progress", "Done", "2026-01-08T09:00:00Z"]])
    a, _ = fp.from_csv(str(rev))
    b, _ = fp.from_csv(str(trs))
    strip = lambda its: [(t["from"], t["to"], fl.parse_time(t["at"])) for t in its[0]["transitions"]]  # noqa: E731
    assert strip(a) == strip(b)


# --------------------------------------------------------------------------- flow_report

def test_report_finds_the_queue_before_the_constraint():
    items = []
    for i in range(20):
        d = 5 + (i % 5)
        items.append(item(f"X-{i}",
                          (f"2026-02-{d:02d}T09:00:00Z", "In Progress"),
                          (f"2026-02-{d:02d}T17:00:00Z", "Ready for QA"),
                          (f"2026-02-{d + 10:02d}T09:00:00Z", "In QA"),
                          (f"2026-02-{d + 10:02d}T15:00:00Z", "Done")))
    rep = fr.analyze(flow_of(*items), SMAP, window=60)
    assert rep["overall"]["completed"] == 20
    assert rep["bottleneck"]["largest"]["stage"] == "Ready for Test"
    assert rep["bottleneck"]["constraint"]["stage"] == "Test"
    assert rep["overall"]["flow_efficiency"] < 0.1
    md = fr.markdown(rep)
    assert "Test is the likely constraint" in md
    assert "```mermaid" in md


def test_report_leaves_out_bulk_closed_and_never_worked_items():
    items = [item(f"B-{i}", ("2026-02-10T10:00:30Z", "Done")) for i in range(9)]
    items.append(item("G-1", ("2026-02-02T09:00:00Z", "In Progress"), ("2026-02-03T09:00:00Z", "Done")))
    items.append(item("Z-1", ("2026-02-04T09:00:00Z", "Done")))
    rep = fr.analyze(flow_of(*items), SMAP, window=60)
    assert rep["overall"]["completed"] == 1
    assert len(rep["quality"]["bulk_closed"]) == 9
    assert rep["quality"]["closed_without_flow"] == ["Z-1"]


def test_report_lists_unmapped_statuses():
    it = item("U-1", ("2026-02-02T09:00:00Z", "In Progress"), ("2026-02-03T09:00:00Z", "Peer Review"),
              ("2026-02-04T09:00:00Z", "Done"))
    rep = fr.analyze(flow_of(it), SMAP, window=60)
    assert rep["quality"]["unmapped"] == {"Peer Review": 1}


def test_sample_report_finds_the_planted_problems():
    flow = fl.load_flow(SAMPLE)
    smap = fl.StatusMap(fl.load_json(MAP))
    rep = fr.analyze(flow, smap, workdays=True, segment="label:dor-met")
    assert rep["bottleneck"]["constraint"]["stage"] == "Testing"
    assert rep["quality"]["bulk_closed"]
    g = rep["segment"]["groups"]
    assert g["not dor-met"]["rework_share"] > g["dor-met"]["rework_share"]


def test_emit_model_has_samples_for_each_active_stage(tmp_path):
    flow = fl.load_flow(SAMPLE)
    smap = fl.StatusMap(fl.load_json(MAP))
    rep = fr.analyze(flow, smap, workdays=True)
    m = fr.emit_model(rep, tmp_path / "m.json")
    assert [s["name"] for s in m["stages"]] == ["Development", "Testing"]
    assert m["stages"][1]["queue_before"] == "Ready for Test"
    assert all(s["service_days"] for s in m["stages"])
    assert m["arrivals_per_week"] > 0


# --------------------------------------------------------------------------- cfd

def test_cfd_finds_stair_steps_and_bulge_in_the_sample():
    flow = fl.load_flow(SAMPLE)
    smap = fl.StatusMap(fl.load_json(MAP))
    c = cfd.build(flow, smap)
    res = cfd.analyze(c)
    kinds = {(f["pattern"], f.get("band")) for f in res["findings"]}
    assert ("stair-steps", "Done") in kinds
    assert ("bulge", "Ready for Test") in kinds


def test_cfd_has_no_findings_for_smooth_flow():
    items = []
    t0 = fl.parse_time("2026-01-05T09:00:00Z")
    k = 0
    for day in range(70):
        d = t0 + fl.dt.timedelta(days=day)
        if d.weekday() >= 5:
            continue
        k += 1
        a = (d + fl.dt.timedelta(hours=1)).isoformat()
        b = (d + fl.dt.timedelta(days=1, hours=2)).isoformat()
        items.append(item(f"S-{k}", (a, "In Progress"), (b, "Done"), created=d.isoformat()))
    c = cfd.build(flow_of(*items), SMAP, window=60)
    found = cfd.analyze(c)["findings"]
    # Only the two stages that this flow never uses are reported, as thin bands.
    assert {(f["pattern"], f["band"]) for f in found} == {("thin band", "Ready for Test"), ("thin band", "Test")}


def test_cfd_svg_and_csv(tmp_path):
    flow = fl.load_flow(SAMPLE)
    smap = fl.StatusMap(fl.load_json(MAP))
    c = cfd.build(flow, smap)
    cfd.svg(c, cfd.analyze(c), tmp_path / "c.svg")
    cfd.write_csv(c, tmp_path / "c.csv")
    assert (tmp_path / "c.svg").read_text().startswith("<svg")
    rows = list(csv.reader(open(tmp_path / "c.csv")))
    assert rows[0][0] == "date" and rows[0][-1] == "Done"


# --------------------------------------------------------------------------- wip_sim

def simple_model(**over):
    m = {"days_per_week": 5, "arrivals_per_week": None, "commit_every_days": None,
         "release_every_days": None, "swarm_efficiency": 0.0,
         "stages": [{"name": "Dev", "workers": 3, "wip_limit": None, "service_days": [2.0, 3.0, 4.0]},
                    {"name": "Test", "workers": 1, "wip_limit": None, "service_days": [1.0]}]}
    m.update(over)
    return m


def test_capacity_is_set_by_the_constraint():
    r = ws.simulate(simple_model(), runs=20, days=100)
    assert 4.7 <= r["throughput_mean"] <= 5.01      # one tester, one item each day
    assert r["stages"][1]["utilization"] > 0.95


def test_wip_limits_cut_lead_time_without_losing_throughput():
    base = ws.simulate(simple_model(), runs=20, days=100)
    lim = ws.simulate(ws.apply_changes(simple_model(), ["Dev=3", "Test=2"]), runs=20, days=100)
    assert lim["throughput_mean"] >= 0.95 * base["throughput_mean"]
    assert lim["lead_p85"] < base["lead_p85"]
    assert lim["avg_wip"] < base["avg_wip"]
    assert lim["stages"][0]["idle_blocked"] > 0


def test_swarming_raises_throughput_when_developers_are_blocked():
    limited = ws.apply_changes(simple_model(), ["Dev.workers=5", "Dev=5", "Test=2"])
    swarm = ws.apply_changes(limited, ["swarm_efficiency=0.5"])
    a = ws.simulate(limited, runs=20, days=100)
    b = ws.simulate(swarm, runs=20, days=100)
    assert b["throughput_mean"] > a["throughput_mean"]


def test_apply_changes_and_delta():
    m = ws.apply_changes(simple_model(), ["Test=4", "Dev.workers=5", "release_every_days=10"])
    assert m["stages"][1]["wip_limit"] == 4 and m["stages"][0]["workers"] == 5
    assert m["release_every_days"] == 10
    m2 = ws.apply_changes(m, deltas=["Test=-2"])
    assert m2["stages"][1]["wip_limit"] == 2
    try:
        ws.apply_changes(simple_model(), deltas=["Dev=-1"])
    except SystemExit as e:
        assert "Use --set" in str(e)
    else:
        raise AssertionError("a delta on a stage without a limit must stop")


def test_simulation_is_repeatable():
    a = ws.simulate(simple_model(arrivals_per_week=4), runs=10, days=60, seed=3)
    b = ws.simulate(simple_model(arrivals_per_week=4), runs=10, days=60, seed=3)
    assert a == b


def test_sweep_recommends_a_limit_and_cli_runs():
    out = subprocess.run([sys.executable, str(FLOW / "wip_sim.py"), str(MODEL), "--runs", "30",
                          "--set", "Development=4", "--sweep", "Testing=1:4"],
                         capture_output=True, text=True, check=True).stdout
    assert "Recommendation: a WIP limit of" in out
    assert "History:" in out


def test_demo_data_is_reproducible(tmp_path):
    out = tmp_path / "d.json"
    subprocess.run([sys.executable, str(FLOW / "demo_flow.py"), "-o", str(out)], check=True,
                   capture_output=True)
    assert json.loads(out.read_text())["items"] == json.loads(SAMPLE.read_text())["items"]


def test_transitions_in_the_sample_are_in_time_order():
    for it in json.loads(SAMPLE.read_text())["items"]:
        times = [fl.parse_time(t["at"]) for t in it["transitions"]]
        assert times == sorted(times)
        for a, b in zip(it["transitions"], it["transitions"][1:]):
            assert a["to"] == b["from"]


def test_as_of_removes_later_changes():
    it = item("C-1", ("2026-02-02T09:00:00Z", "In Progress"), ("2026-02-20T09:00:00Z", "Done"))
    late = item("C-2", ("2026-03-02T09:00:00Z", "In Progress"), created="2026-03-01T09:00:00Z")
    rep = fr.analyze(flow_of(it, late), SMAP, window=60, as_of="2026-02-10T00:00:00Z")
    assert rep["overall"]["completed"] == 0
    assert rep["load"]["current_wip"] == 1
    assert rep["quality"]["items"] == 1


def test_cfd_says_when_there_is_too_little_data():
    it = item("T-1", ("2026-02-02T09:00:00Z", "In Progress"))
    res = cfd.analyze(cfd.build(flow_of(it), SMAP, window=30))
    assert [f["pattern"] for f in res["findings"]] == ["too little data"]
