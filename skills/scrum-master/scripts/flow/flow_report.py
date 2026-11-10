#!/usr/bin/env python3
"""Make a draft value stream map (VSM) and the flow metrics from flow data.

  python flow_report.py flow.json map.json                       # Markdown report
  python flow_report.py flow.json map.json --format json         # machine-readable
  python flow_report.py flow.json map.json --segment label:dor-met
  python flow_report.py flow.json map.json --emit-model model.json   # input for wip_sim.py

Options:
  --window DAYS        The period to measure, back from the latest time in the data (182 = six months).
  --as-of DATE         Use this date as "now", not the latest time in the data.
  --workdays           Count Monday to Friday only.
  --team NAME          Use the items of one team only.
  --segment KEY        Compare groups of items: label:NAME, type, team, or any field of an item.
  --pi-objectives F    A JSON list of {"pi", "team", "planned", "actual"} business values, for
                       the SAFe flow predictability measure.
  --bulk N             Transitions at the same minute for N or more items are a bulk move (default 8).
                       Items that were closed by a bulk move are not in the flow metrics.
  --keep-bulk          Keep the items that a bulk move closed.

The report is a draft for a workshop. It shows where items wait. People in the workshop
make sure that the map is correct, and find the causes. Standard library only.
"""
import argparse
import datetime as dt
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flowlib as fl  # noqa: E402


def bulk_minutes(items, threshold):
    c = Counter()
    for it in items:
        for t in {tr["at"].replace(second=0, microsecond=0) for tr in it["transitions"]}:
            c[t] += 1
    return {t for t, n in c.items() if n >= threshold}


def segment_value(res, key):
    if key.startswith("label:"):
        name = key.split(":", 1)[1]
        return f"{name}" if name in res["labels"] else f"not {name}"
    if key in ("type", "team"):
        return res.get(key) or "(none)"
    v = res["raw"].get(key)
    return str(v) if v is not None else "(none)"


def summarize(results):
    ft = [r["flow_days"] for r in results]
    eff_total = sum(r["active_days"] for r in results)
    flow_total = sum(r["flow_days"] for r in results)
    return {
        "completed": len(results),
        "flow_time_p50": fl.percentile(ft, 50),
        "flow_time_p85": fl.percentile(ft, 85),
        "flow_time_p95": fl.percentile(ft, 95),
        "flow_time_mean": fl.mean(ft),
        "flow_efficiency": (eff_total / flow_total) if flow_total else None,
        "flow_efficiency_median_item": fl.percentile([r["efficiency"] for r in results], 50),
        "rework_share": (sum(1 for r in results if r["backward_moves"]) / len(results)) if results else None,
    }


def analyze(flow, smap, window=182, as_of=None, workdays=False, team=None, segment=None,
            bulk=8, keep_bulk=False, pi_objectives=None):
    items = flow["items"]
    if team:
        items = [it for it in items if it.get("team") == team]
    as_of = fl.parse_time(as_of) if as_of else fl.as_of_time(items)
    if as_of is None:
        raise SystemExit("The flow data has no times.")
    items = fl.cut_at(items, as_of)
    start = as_of - dt.timedelta(days=window)
    bulk_set = bulk_minutes(items, bulk)

    results = [fl.analyze_item(it, smap, as_of, workdays) for it in items]
    quality = {"items": len(items), "unmapped": Counter(), "no_transitions": 0,
               "closed_without_flow": [], "bulk_closed": [], "bulk_moves": len(bulk_set),
               "reopened": 0, "stale_wip": [], "discarded": 0}
    completed, wip = [], []
    for r in results:
        it = r["raw"]
        quality["unmapped"].update(r["unmapped"])
        if not it["transitions"] and smap.kind_of(smap.stage_of(it.get("status"))) != "backlog":
            quality["no_transitions"] += 1
        if r["reopened"]:
            quality["reopened"] += 1
        if r["discarded"]:
            quality["discarded"] += 1
            continue
        if r["done"] is not None:
            if not (start <= r["done"] <= as_of):
                continue
            done_tr = [tr for tr in it["transitions"]
                       if smap.kind_of(smap.stage_of(tr["to"])) == "done"]
            is_bulk = bool(done_tr) and done_tr[-1]["at"].replace(second=0, microsecond=0) in bulk_set
            if is_bulk and not keep_bulk:
                quality["bulk_closed"].append(r["id"])
                continue
            if r["active_days"] == 0 and (r["flow_days"] or 0) < 0.01:
                quality["closed_without_flow"].append(r["id"])
                continue
            completed.append(r)
        elif r["committed"] is not None:
            wip.append(r)
            last = it["transitions"][-1]["at"] if it["transitions"] else r["committed"]
            if (as_of - last).days > 60:
                quality["stale_wip"].append(r["id"])

    flow_stages = smap.flow_stages()
    done_names = {s["name"] for s in smap.done_stages()}
    total_flow = sum(r["flow_days"] for r in completed) or 0.0

    # per stage
    stage_rows = []
    extra = [fl.BLOCKED, fl.UNMAPPED]
    for st in flow_stages + [{"name": n, "kind": "blocked" if n == fl.BLOCKED else "unmapped"} for n in extra]:
        name = st["name"]
        vals = [r["stage_days"][name] for r in completed if r["stage_days"].get(name, 0) > 0]
        if st["kind"] in ("blocked", "unmapped") and not vals:
            continue
        total = sum(vals)
        stage_rows.append({
            "stage": name, "kind": st["kind"],
            "visited_share": len(vals) / len(completed) if completed else 0,
            "p50": fl.percentile(vals, 50), "p85": fl.percentile(vals, 85), "mean": fl.mean(vals),
            "total_days": total, "share_of_flow_time": (total / total_flow) if total_flow else 0,
        })

    # throughput per week (full weeks back from as_of)
    weeks = max(1, window // 7)
    per_week = [0] * weeks
    for r in completed:
        b = int((as_of - r["done"]).total_seconds() // (7 * 86400))
        if 0 <= b < weeks:
            per_week[weeks - 1 - b] += 1
    tp_mean = fl.mean(per_week)
    tp_sd = (sum((x - tp_mean) ** 2 for x in per_week) / len(per_week)) ** 0.5 if per_week else 0
    days_per_week = 5 if workdays else 7

    # flow load: daily WIP over the window
    daily_wip, daily_stage = [], defaultdict(list)
    flow_names = {s["name"] for s in flow_stages} | {fl.BLOCKED, fl.UNMAPPED}
    d = start.date()
    while d <= as_of.date():
        if workdays and d.weekday() >= 5:
            d += dt.timedelta(days=1)
            continue
        t = fl.end_of_day(d)
        counts = Counter()
        for r in results:
            if r["committed"] is None or r["committed"] > t:
                continue
            s = fl.state_at(r["raw"], smap, t)
            if s in flow_names:
                counts[s] += 1
        daily_wip.append(sum(counts.values()))
        for st in flow_stages:
            daily_stage[st["name"]].append(counts.get(st["name"], 0))
        d += dt.timedelta(days=1)

    overall = summarize(completed)
    committed_in_window = sum(1 for r in results if r["committed"] and start <= r["committed"] <= as_of
                              and not r["discarded"] and r["id"] not in quality["bulk_closed"]
                              and r["id"] not in quality["closed_without_flow"])
    avg_wip = fl.mean(daily_wip)
    tp_day = (tp_mean / days_per_week) if tp_mean else None
    littles = {"avg_wip": avg_wip, "throughput_per_day": tp_day,
               "implied_flow_time": (avg_wip / tp_day) if (avg_wip is not None and tp_day) else None,
               "measured_flow_time_mean": overall["flow_time_mean"]}
    first_q = daily_wip[: max(1, len(daily_wip) // 4)]
    last_q = daily_wip[-max(1, len(daily_wip) // 4):]
    littles["wip_trend"] = (fl.mean(last_q) / fl.mean(first_q)) if fl.mean(first_q) else None

    # where items wait: the role of each stage, the largest wait, and the likely constraint
    order = [st["name"] for st in smap.stages]

    def role(stage_row):
        name = stage_row["stage"]
        if stage_row["kind"] == "blocked":
            return "blocked"
        if stage_row["kind"] == "active":
            return "work"
        if name not in order:
            return "unmapped"
        i = order.index(name)
        before = any(st["kind"] == "active" for st in smap.stages[:i])
        after = None
        for st in smap.stages[i + 1:]:
            if st["kind"] in ("active", "done"):
                after = st
                break
        if not before:
            return "start queue"
        if after is None or after["kind"] == "done":
            return "release queue"
        return "handoff queue"

    for row in stage_rows:
        row["role"] = role(row)
    bottleneck = None
    ranked = sorted(stage_rows, key=lambda r: -r["total_days"])
    if ranked:
        top = ranked[0]
        bottleneck = {"largest": {"stage": top["stage"], "role": top["role"],
                                  "share": top["share_of_flow_time"]}, "constraint": None}
        handoffs = [r for r in ranked if r["role"] == "handoff queue" and r["share_of_flow_time"] >= 0.1]
        if handoffs:
            q = handoffs[0]
            i = order.index(q["stage"])
            nxt = next(st for st in smap.stages[i + 1:] if st["kind"] == "active")
            bottleneck["constraint"] = {"queue": q["stage"], "stage": nxt["name"],
                                        "share": q["share_of_flow_time"]}
        elif top["role"] == "work":
            bottleneck["constraint"] = {"queue": None, "stage": top["stage"],
                                        "share": top["share_of_flow_time"]}

    # distribution
    dist = Counter(r["type"] for r in completed)
    wip_dist = Counter(r["type"] for r in wip)

    # teams
    teams = {}
    for tname in sorted({r["team"] for r in completed if r["team"]}):
        rs = [r for r in completed if r["team"] == tname]
        teams[tname] = summarize(rs)
        teams[tname]["throughput_per_week"] = len(rs) / weeks

    # segment
    seg = None
    if segment:
        groups = defaultdict(list)
        for r in completed:
            groups[segment_value(r, segment)].append(r)
        seg = {"key": segment, "groups": {g: summarize(rs) for g, rs in sorted(groups.items())}}

    # aging WIP
    p85 = overall["flow_time_p85"]
    aging = []
    for r in wip:
        age = fl.days_between(r["committed"], as_of, workdays)
        if p85 is not None and age > p85:
            aging.append({"id": r["id"], "team": r["team"], "stage": r["current_stage"],
                          "age_days": age})
    aging.sort(key=lambda x: -x["age_days"])

    # predictability
    predict = {"weekly_throughput_cv": (tp_sd / tp_mean) if tp_mean else None, "pi": None}
    if pi_objectives:
        rows = []
        for o in pi_objectives:
            if o.get("planned"):
                rows.append({**o, "achievement": o.get("actual", 0) / o["planned"]})
        predict["pi"] = rows

    return {
        "as_of": fl.iso(as_of), "window_days": window, "workdays": workdays, "team": team,
        "source": flow.get("source"), "anonymized": flow.get("anonymized"),
        "fictional": flow.get("fictional", False),
        "overall": overall, "stages": stage_rows, "bottleneck": bottleneck,
        "throughput": {"per_week": per_week, "mean_per_week": tp_mean, "sd_per_week": tp_sd},
        "load": {"current_wip": len(wip), "avg_daily_wip": avg_wip,
                 "current_by_stage": dict(Counter(r["current_stage"] for r in wip)),
                 "avg_by_stage": {k: fl.mean(v) for k, v in daily_stage.items()}},
        "commitments_per_week": committed_in_window / weeks,
        "littles_law": littles, "distribution": dict(dist), "wip_distribution": dict(wip_dist),
        "teams": teams, "segment": seg, "aging_wip": aging, "predictability": predict,
        "quality": {**quality, "unmapped": dict(quality["unmapped"])},
        "_bulk": bulk, "_completed": completed, "_smap": smap, "_daily_stage": daily_stage,
        "_done_names": done_names, "_days_per_week": days_per_week,
    }


# --------------------------------------------------------------------------- output

def rep_bulk(rep):
    return rep.get("_bulk", 8)


def mermaid(rep):
    rows = {s["stage"]: s for s in rep["stages"]}
    smap = rep["_smap"]
    bn = rep["bottleneck"] or {}
    con = bn.get("constraint") or {}
    hot = {(bn.get("largest") or {}).get("stage"), con.get("queue"), con.get("stage")}
    lines = ["```mermaid", "flowchart LR"]
    names = []
    for i, st in enumerate(smap.flow_stages()):
        r = rows.get(st["name"])
        nid = f"S{i}"
        names.append(nid)
        if r:
            label = (f"{st['name']}<br/>{st['kind']} · p50 {fl.fmt(r['p50'])} d<br/>"
                     f"{r['share_of_flow_time'] * 100:.0f}% of flow time")
        else:
            label = f"{st['name']}<br/>{st['kind']} · not used"
        if st["kind"] == "wait":
            lines.append(f'  {nid}{{{{"{label}"}}}}')
        else:
            lines.append(f'  {nid}["{label}"]')
    done = smap.done_stages()
    lines.append(f'  D(["{done[0]["name"] if done else "Done"}"])')
    for a, b in zip(names, names[1:] + ["D"]):
        lines.append(f"  {a} --> {b}")
    if fl.BLOCKED in rows:
        r = rows[fl.BLOCKED]
        lines.append(f'  B{{{{"Blocked<br/>p50 {fl.fmt(r["p50"])} d · {r["visited_share"] * 100:.0f}% of items"}}}}')
    lines.append("  classDef wait fill:#f0efec,stroke:#52514e")
    lines.append("  classDef hot fill:#fde2dd,stroke:#c0392b,stroke-width:2px")
    for i, st in enumerate(smap.flow_stages()):
        if st["name"] in hot:
            lines.append(f"  class S{i} hot")
        elif st["kind"] == "wait":
            lines.append(f"  class S{i} wait")
    lines.append("```")
    return "\n".join(lines)


def summary_sentences(rep):
    o, bn, tp, ll = rep["overall"], rep["bottleneck"], rep["throughput"], rep["littles_law"]
    unit = "working days" if rep["workdays"] else "days"
    out = []
    if not o["completed"]:
        return ["No item reached a done stage in the period. Make sure that the status map names the done statuses."]
    out.append(f"In the last {rep['window_days']} days, {o['completed']} items reached Done, "
               f"{fl.fmt(tp['mean_per_week'])} each week on average.")
    out.append(f"Half of the items took {fl.fmt(o['flow_time_p50'])} {unit} or less from commitment to Done. "
               f"85% took {fl.fmt(o['flow_time_p85'])} {unit} or less.")
    if o["flow_efficiency"] is not None:
        out.append(f"Somebody worked on an item for {o['flow_efficiency'] * 100:.0f}% of its flow time. "
                   f"For the other {100 - o['flow_efficiency'] * 100:.0f}%, the item waited.")
    if bn:
        lg, con = bn["largest"], bn["constraint"]
        share = f"{lg['share'] * 100:.0f}%"
        if lg["role"] == "start queue":
            out.append(f"The largest wait is in {lg['stage']} ({share} of all flow time), before work starts. "
                       f"Items are committed long before somebody starts them. A batch commitment at planning "
                       f"often causes this.")
        elif lg["role"] == "release queue":
            out.append(f"The largest wait is in {lg['stage']} ({share} of all flow time). Finished items "
                       f"wait for a release. This is a batch, not a team that is too slow.")
        elif lg["role"] == "blocked":
            out.append(f"Blocked work uses the most time ({share} of all flow time).")
        elif lg["role"] == "work":
            out.append(f"Items spend the most time in {lg['stage']} ({share} of all flow time).")
        else:
            out.append(f"The largest wait is in {lg['stage']} ({share} of all flow time).")
        if con and con.get("queue"):
            out.append(f"Between two work stages, the largest queue is {con['queue']} "
                       f"({con['share'] * 100:.0f}% of the flow time). It is before {con['stage']}, so "
                       f"{con['stage']} is the likely constraint.")
    trend = ll.get("wip_trend")
    if trend and trend > 1.25:
        out.append(f"The work in progress grew: the average of the last quarter of the period is "
                   f"{trend:.1f} times the average of the first quarter. By Little's law, the flow time "
                   f"will increase if this continues.")
    imp, meas = ll.get("implied_flow_time"), ll.get("measured_flow_time_mean")
    if imp and meas and abs(imp - meas) / meas > 0.3:
        out.append(f"Little's law gives a flow time of {imp:.1f} {unit}, but the measured mean is "
                   f"{meas:.1f} {unit}. The flow is not stable, or the board has items that stay open.")
    seg = rep.get("segment")
    if seg and len(seg["groups"]) == 2:
        (ga, a), (gb, b) = seg["groups"].items()
        if a["flow_time_p50"] and b["flow_time_p50"]:
            slow, fast = (ga, a), (gb, b)
            if a["flow_time_p50"] < b["flow_time_p50"]:
                slow, fast = (gb, b), (ga, a)
            ratio = slow[1]["flow_time_p50"] / fast[1]["flow_time_p50"]
            rw_s, rw_f = (slow[1]["rework_share"] or 0) * 100, (fast[1]["rework_share"] or 0) * 100
            parts = []
            if ratio >= 1.25:
                parts.append(f"The median flow time of the group \"{slow[0]}\" is {ratio:.1f} times the median "
                             f"of the group \"{fast[0]}\" ({fl.fmt(slow[1]['flow_time_p50'])} against "
                             f"{fl.fmt(fast[1]['flow_time_p50'])} {unit}).")
            if abs(rw_s - rw_f) >= 10:
                (hi_g, hi), (lo_g, lo) = sorted([(ga, (a["rework_share"] or 0) * 100),
                                                 (gb, (b["rework_share"] or 0) * 100)], key=lambda x: -x[1])
                parts.append(f"{hi:.0f}% of the items in the group \"{hi_g}\" moved back to an earlier "
                             f"stage, against {lo:.0f}% in the group \"{lo_g}\".")
            if parts:
                out.append(" ".join(parts) + " This is a correlation. Test the cause in the workshop.")
    return out


def questions(rep):
    q = []
    bn = rep["bottleneck"] or {}
    lg, con = bn.get("largest") or {}, bn.get("constraint") or {}
    asked = set()
    if lg.get("stage") and lg.get("role") != "work":
        q.append(f"Why do items wait in {lg['stage']}? Who pulls them out, and how often?")
        asked.add(lg["stage"])
    if con.get("queue") and con["queue"] not in asked:
        q.append(f"Why do items wait in {con['queue']}? Who pulls them out, and how often?")
        asked.add(con["queue"])
    if con.get("stage"):
        q.append(f"How many people can do the work of {con['stage']}? Who else can help there?")
    for s in rep["stages"]:
        if s["kind"] == "wait" and s["stage"] not in asked and s["share_of_flow_time"] > 0.1:
            q.append(f"{s['stage']} holds {s['share_of_flow_time'] * 100:.0f}% of the flow time. What does an item wait for there?")
    if rep["overall"].get("rework_share") and rep["overall"]["rework_share"] > 0.1:
        q.append(f"{rep['overall']['rework_share'] * 100:.0f}% of the items moved back to an earlier stage. What made them come back?")
    if fl.UNMAPPED in [s["stage"] for s in rep["stages"]] or rep["quality"]["unmapped"]:
        q.append("Some statuses are not in the status map. Which stage of the value stream are they?")
    q.append("Which steps happen outside the board (approvals, environments, other teams)? Add them to the map.")
    q.append("Does the map start and end at the right points for the customer?")
    return q


def markdown(rep):
    o = rep["overall"]
    unit = "working days" if rep["workdays"] else "days"
    L = []
    title = "Draft value stream map and flow metrics"
    if rep["team"]:
        title += f": {rep['team']}"
    L.append(f"# {title}")
    L.append("")
    scope = (f"Period: {rep['window_days']} days to {rep['as_of'][:10]}. Source: {rep['source']}. "
             f"Times are in {unit}.")
    if rep["fictional"]:
        scope += " The data is fictional."
    elif not rep["anonymized"]:
        scope += " The data is not anonymized. Do not share this report outside the team."
    L.append(scope)
    L.append("")
    L.append("This map is a draft from the board data. It shows where items wait. The workshop "
             "makes sure that it is correct and finds the causes.")
    L.append("")
    L.append("## Summary")
    L.append("")
    L.append(" ".join(summary_sentences(rep)))
    L.append("")
    L.append("## Draft value stream map")
    L.append("")
    L.append(mermaid(rep))
    L.append("")
    L.append("| Stage | Kind | Role | Items that visited | p50 (days) | p85 (days) | Share of flow time |")
    L.append("|---|---|---|---|---|---|---|")
    for s in rep["stages"]:
        L.append(f"| {s['stage']} | {s['kind']} | {s['role']} | {s['visited_share'] * 100:.0f}% | {fl.fmt(s['p50'])} | "
                 f"{fl.fmt(s['p85'])} | {s['share_of_flow_time'] * 100:.0f}% |")
    L.append("")
    L.append("## The six flow metrics")
    L.append("")
    tp = rep["throughput"]
    dist = rep["distribution"]
    total = sum(dist.values()) or 1
    pr = rep["predictability"]
    L.append("| Metric | Value | What it shows |")
    L.append("|---|---|---|")
    L.append(f"| Flow distribution | {', '.join(f'{k} {v * 100 / total:.0f}%' for k, v in sorted(dist.items(), key=lambda x: -x[1]))} | "
             f"The mix of the work types that reached Done |")
    L.append(f"| Flow velocity | {fl.fmt(tp['mean_per_week'])} items each week (standard deviation {fl.fmt(tp['sd_per_week'])}) | "
             f"The number of items that reached Done |")
    L.append(f"| Flow time | p50 {fl.fmt(o['flow_time_p50'])}, p85 {fl.fmt(o['flow_time_p85'])}, p95 {fl.fmt(o['flow_time_p95'])} {unit} | "
             f"The time from commitment to Done |")
    L.append(f"| Flow load | {rep['load']['current_wip']} items at this time, {fl.fmt(rep['load']['avg_daily_wip'])} on average | "
             f"The work in progress after the commitment point |")
    L.append(f"| Flow efficiency | {fl.fmt((o['flow_efficiency'] or 0) * 100, 0)}% (median item {fl.fmt((o['flow_efficiency_median_item'] or 0) * 100, 0)}%) | "
             f"The active time divided by the flow time |")
    if pr["pi"]:
        ach = ", ".join(f"{r.get('pi')} {r.get('team', '')}: {r['achievement'] * 100:.0f}%".replace("  ", " ") for r in pr["pi"])
        L.append(f"| Flow predictability | {ach} | The actual business value of the PI objectives divided by the planned value. The SAFe target is 80% to 100%. |")
    else:
        L.append(f"| Flow predictability | TBD. Proxy: the weekly throughput varies by {fl.fmt((pr['weekly_throughput_cv'] or 0) * 100, 0)}% (coefficient of variation) | "
                 f"SAFe measures it with the PI objectives. Give them with --pi-objectives. |")
    L.append("")
    L.append(f"Weekly throughput, oldest first: {', '.join(str(x) for x in tp['per_week'])}.")
    L.append("")
    if rep["teams"]:
        L.append("## Teams")
        L.append("")
        L.append("| Team | Done | Each week | Flow time p50 | Flow time p85 | Flow efficiency | Rework |")
        L.append("|---|---|---|---|---|---|---|")
        for t, s in rep["teams"].items():
            L.append(f"| {t} | {s['completed']} | {fl.fmt(s['throughput_per_week'])} | {fl.fmt(s['flow_time_p50'])} | "
                     f"{fl.fmt(s['flow_time_p85'])} | {fl.fmt((s['flow_efficiency'] or 0) * 100, 0)}% | "
                     f"{fl.fmt((s['rework_share'] or 0) * 100, 0)}% |")
        L.append("")
    if rep["segment"]:
        seg = rep["segment"]
        L.append(f"## Comparison by {seg['key']}")
        L.append("")
        L.append("| Group | Done | Flow time p50 | Flow time p85 | Flow efficiency | Rework |")
        L.append("|---|---|---|---|---|---|")
        for g, s in seg["groups"].items():
            L.append(f"| {g} | {s['completed']} | {fl.fmt(s['flow_time_p50'])} | {fl.fmt(s['flow_time_p85'])} | "
                     f"{fl.fmt((s['flow_efficiency'] or 0) * 100, 0)}% | {fl.fmt((s['rework_share'] or 0) * 100, 0)}% |")
        L.append("")
        L.append("A difference between groups is a correlation, not a proof of the cause.")
        L.append("")
    L.append("## Aging work in progress")
    L.append("")
    if rep["aging_wip"]:
        L.append(f"These items are older than the 85th percentile of the flow time ({fl.fmt(o['flow_time_p85'])} {unit}). "
                 "Talk about them at the next standup.")
        L.append("")
        L.append("| Item | Team | Stage | Age (days) |")
        L.append("|---|---|---|---|")
        for a in rep["aging_wip"][:15]:
            L.append(f"| {a['id']} | {a['team']} | {a['stage']} | {a['age_days']:.0f} |")
        if len(rep["aging_wip"]) > 15:
            L.append(f"| {len(rep['aging_wip']) - 15} more | | | |")
    else:
        L.append("No item in progress is older than the 85th percentile of the flow time.")
    L.append("")
    L.append("## Data quality")
    L.append("")
    qd = rep["quality"]
    L.append(f"- Items in the data: {qd['items']}. Items outside the backlog without a status change: {qd['no_transitions']}.")
    if qd["unmapped"]:
        L.append(f"- Statuses that are not in the status map: {', '.join(f'{k} ({v})' for k, v in qd['unmapped'].items())}. "
                 "Add them to the map.")
    if qd["bulk_moves"]:
        L.append(f"- Bulk moves: {qd['bulk_moves']} minute(s) with status changes for {rep_bulk(rep)} or more items. "
                 f"{len(qd['bulk_closed'])} items closed by a bulk move are not in the metrics.")
    if qd["closed_without_flow"]:
        L.append(f"- {len(qd['closed_without_flow'])} items went from the backlog to Done with no work stage. "
                 "They are not in the metrics.")
    if qd["reopened"]:
        L.append(f"- {qd['reopened']} items were reopened after Done.")
    if qd["stale_wip"]:
        L.append(f"- {len(qd['stale_wip'])} items in progress had no status change for more than 60 days.")
    L.append(f"- {qd['discarded']} items were discarded.")
    L.append("")
    L.append("## Questions for the workshop")
    L.append("")
    for x in questions(rep):
        L.append(f"- {x}")
    L.append("")
    return "\n".join(L)


def emit_model(rep, path):
    completed = rep["_completed"]
    stages = []
    queue = None
    for st in rep["_smap"].flow_stages():
        if st["kind"] == "wait":
            queue = st["name"]
            continue
        samples = sorted(round(r["stage_days"][st["name"]], 2) for r in completed
                         if r["stage_days"].get(st["name"], 0) > 0)
        avg_items = fl.mean(rep["_daily_stage"].get(st["name"], []))
        stages.append({
            "name": st["name"],
            "workers": max(1, round(avg_items or 1)),
            "workers_note": f"Estimate: on average {fl.fmt(avg_items)} items were in this stage at the same "
                            f"time. Replace it with the number of people who do this work.",
            "wip_limit": None,
            "queue_before": queue,
            "service_days": samples,
        })
        queue = None
    model = {
        "note": "Model for wip_sim.py, made by flow_report.py --emit-model. Each active stage has "
                "a number of workers, a WIP limit (null = no limit) and samples of the time that an "
                "item spent in the stage. The WIP limit of a stage counts the items in the stage and "
                "the finished items that wait for the next stage. Make sure that the workers are correct.",
        "days_per_week": rep["_days_per_week"],
        "release_every_days": None,
        "swarm_efficiency": 0.0,
        "arrivals_per_week": rep["commitments_per_week"],
        "commit_every_days": None,
        "history": {"throughput_per_week": rep["throughput"]["mean_per_week"],
                    "flow_time_p50": rep["overall"]["flow_time_p50"],
                    "flow_time_p85": rep["overall"]["flow_time_p85"],
                    "as_of": rep["as_of"], "window_days": rep["window_days"]},
        "stages": stages,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(model, f, indent=1)
    return model


def public(rep):
    return {k: v for k, v in rep.items() if not k.startswith("_")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("flow")
    ap.add_argument("map")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    ap.add_argument("--window", type=int, default=182)
    ap.add_argument("--as-of")
    ap.add_argument("--workdays", action="store_true")
    ap.add_argument("--team")
    ap.add_argument("--segment")
    ap.add_argument("--pi-objectives")
    ap.add_argument("--bulk", type=int, default=8)
    ap.add_argument("--keep-bulk", action="store_true")
    ap.add_argument("--emit-model")
    ap.add_argument("-o", "--output")
    a = ap.parse_args(argv)
    flow = fl.load_flow(a.flow)
    smap = fl.StatusMap(fl.load_json(a.map))
    pio = fl.load_json(a.pi_objectives) if a.pi_objectives else None
    rep = analyze(flow, smap, a.window, a.as_of, a.workdays, a.team, a.segment, a.bulk, a.keep_bulk, pio)
    text = markdown(rep) if a.format == "markdown" else json.dumps(public(rep), indent=1, default=str)
    if a.output:
        with open(a.output, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Wrote {a.output}")
    else:
        print(text)
    if a.emit_model:
        emit_model(rep, a.emit_model)
        print(f"Wrote the simulation model to {a.emit_model}. Make sure that the workers are correct.",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
