#!/usr/bin/env python3
"""Make a cumulative flow diagram (CFD) from flow data, and find the known patterns in it.

  python cfd.py flow.json map.json                    # plain-language findings (Markdown)
  python cfd.py flow.json map.json --svg cfd.svg      # also draw the CFD
  python cfd.py flow.json map.json --csv cfd.csv      # also write the daily counts
  python cfd.py flow.json map.json --format json

Options: --window DAYS (default 182), --as-of DATE, --team NAME, --bulk N (default 8).

A CFD has one band for each stage. The height of a band on a day is the number of items in that
stage. The top line of the Done band is the number of items delivered so far.

The patterns (references/cfd-patterns.md explains each one):
  bulge            A band gets wider. Items arrive in the stage faster than they leave.
  stair-steps      A line goes up in large steps with flat parts between them. Work moves in batches.
  divergence       The arrival line goes up faster than the departure line. The WIP grows.
  flat departures  No item reaches Done for a long time.
  thin band        A stage is almost never used. The board does not match the work.
  backlog growth   The backlog grows faster than the system starts work.

Weekends do not count in the analysis of steps. Standard library only.
"""
import argparse
import csv
import datetime as dt
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flowlib as fl  # noqa: E402
from flow_report import bulk_minutes  # noqa: E402


def bands_of(smap):
    """The bands, from the backlog to Done: [{"name", "kind", "stages"}]."""
    bands = []
    backlog = [s["name"] for s in smap.stages if s["kind"] == "backlog"]
    if backlog:
        bands.append({"name": "Backlog", "kind": "backlog", "stages": backlog})
    for s in smap.flow_stages():
        bands.append({"name": s["name"], "kind": s["kind"], "stages": [s["name"]]})
    done = [s["name"] for s in smap.done_stages()]
    bands.append({"name": done[0] if len(done) == 1 else "Done", "kind": "done", "stages": done})
    return bands


def build(flow, smap, window=182, as_of=None, team=None, bulk=8):
    items = flow["items"]
    if team:
        items = [it for it in items if it.get("team") == team]
    as_of = fl.parse_time(as_of) if as_of else fl.as_of_time(items)
    items = fl.cut_at(items, as_of)
    start = (as_of - dt.timedelta(days=window)).date()
    bulk_set = bulk_minutes(items, bulk)
    bands = bands_of(smap)
    index = {st: i for i, b in enumerate(bands) for st in b["stages"]}
    keep, bulk_ids = [], set()
    for it in items:
        final = fl.state_at(it, smap, as_of)
        if final == "discarded":
            continue
        trs = it["transitions"]
        if trs and trs[-1]["at"].replace(second=0, microsecond=0) in bulk_set \
                and smap.kind_of(smap.stage_of(trs[-1]["to"])) == "done":
            bulk_ids.add(it.get("id"))
            continue
        keep.append(it)

    days = list(fl.daterange(start, as_of.date()))
    counts = []          # per day: number of items in each band
    for d in days:
        t = fl.end_of_day(d)
        row = [0] * len(bands)
        for it in keep:
            st = fl.state_at(it, smap, t)
            if st is None:
                continue
            if st in (fl.BLOCKED, fl.UNMAPPED):
                st = last_known(it, smap, t, index)
                if st is None:
                    continue
            if st in index:
                row[index[st]] += 1
        counts.append(row)
    return {"bands": bands, "days": days, "counts": counts, "as_of": as_of, "team": team,
            "bulk_excluded": sorted(bulk_ids), "fictional": flow.get("fictional", False)}


def last_known(item, smap, t, index):
    cur = item["transitions"][0]["from"] if item["transitions"] else item.get("status")
    known = smap.stage_of(cur) if smap.stage_of(cur) in index else None
    for tr in item["transitions"]:
        if tr["at"] > t:
            break
        st = smap.stage_of(tr["to"])
        if st in index:
            known = st
    return known


def cumulative(cfd):
    """lines[k][d]: the number of items in band k or a later band at the end of day d."""
    n = len(cfd["bands"])
    lines = []
    for k in range(n):
        lines.append([sum(row[k:]) for row in cfd["counts"]])
    return lines


def _workday_increments(days, series):
    inc = []
    prev = series[0]
    for d, v in zip(days[1:], series[1:]):
        step = max(0, v - prev)
        prev = v
        if d.weekday() >= 5:
            if inc:
                inc[-1] = (inc[-1][0], inc[-1][1] + step)
            continue
        inc.append((d, step))
    return inc


def _quarter_means(series):
    q = max(1, len(series) // 4)
    return fl.mean(series[:q]), fl.mean(series[-q:])


def analyze(cfd):
    bands, days = cfd["bands"], cfd["days"]
    lines = cumulative(cfd)
    widths = [[row[k] for row in cfd["counts"]] for k in range(len(bands))]
    flow_idx = [k for k, b in enumerate(bands) if b["kind"] in ("wait", "active")]
    done_k = len(bands) - 1
    first_flow = flow_idx[0] if flow_idx else done_k
    findings = []
    if max(lines[first_flow]) - min(lines[first_flow]) + lines[first_flow][0] < 10:
        return {"findings": [{"pattern": "too little data", "items": max(lines[first_flow])}],
                "wip_now": sum(widths[k][-1] for k in flow_idx),
                "delivered": lines[done_k][-1] - lines[done_k][0]}

    # bulge
    bulges = []
    for k in flow_idx:
        a, b = _quarter_means(widths[k])
        if b is not None and a is not None and b >= max(1.5 * a, a + 3):
            nxt = next((bands[j]["name"] for j in range(k + 1, len(bands))
                        if bands[j]["kind"] in ("active", "done")), None)
            bulges.append({"pattern": "bulge", "band": bands[k]["name"], "kind": bands[k]["kind"],
                           "from": a, "to": b, "next": nxt, "growth": b - a,
                           "start_queue": k == first_flow and bands[k]["kind"] == "wait"})
    bulges.sort(key=lambda x: -x["growth"])
    findings += bulges

    # stair-steps, for the line that enters each band after the backlog
    for k in range(first_flow, len(bands)):
        inc = _workday_increments(days, lines[k])
        total = sum(v for _, v in inc)
        if total < 10 or len(inc) < 20:
            continue
        vals = sorted((v for _, v in inc), reverse=True)
        m = max(1, math.ceil(0.1 * len(inc)))
        share = sum(vals[:m]) / total
        if share >= 0.5:
            avg = total / len(inc)
            step_idx = [i for i, (_, v) in enumerate(inc) if v >= 3 * avg]
            gaps = [b - a for a, b in zip(step_idx, step_idx[1:])]
            period = fl.percentile(gaps, 50) if gaps else None
            where = "into " + bands[k]["name"]
            if k == first_flow:
                role = "commitment"
            elif k == done_k:
                role = "release"
            else:
                role = "handoff"
            findings.append({"pattern": "stair-steps", "band": bands[k]["name"], "role": role,
                             "share": share, "days_share": m / len(inc), "period_days": period,
                             "where": where})

    # divergence over the last six weeks
    span = min(len(days) - 1, 42)
    if span >= 14:
        arr = (lines[first_flow][-1] - lines[first_flow][-1 - span]) / (span / 7)
        dep = (lines[done_k][-1] - lines[done_k][-1 - span]) / (span / 7)
        if dep > 0 and arr / dep >= 1.2:
            findings.append({"pattern": "divergence", "direction": "wip grows", "arrivals": arr,
                             "departures": dep})
        elif arr >= 0 and dep > 0 and arr / dep <= 0.8:
            findings.append({"pattern": "divergence", "direction": "wip falls", "arrivals": arr,
                             "departures": dep})
        elif dep == 0 and arr > 0:
            findings.append({"pattern": "divergence", "direction": "wip grows", "arrivals": arr,
                             "departures": 0.0})

    # flat departures
    inc = _workday_increments(days, lines[done_k])
    run = best = 0
    best_end = None
    for d, v in inc:
        run = run + 1 if v == 0 else 0
        if run > best:
            best, best_end = run, d
    batch = next((f for f in findings if f["pattern"] == "stair-steps" and f["role"] == "release"), None)
    limit = max(10, 2 * (batch["period_days"] or 0)) if batch else 10
    if best >= limit:
        findings.append({"pattern": "flat departures", "workdays": best, "until": best_end.isoformat()})

    # thin bands
    for k in flow_idx:
        if fl.mean(widths[k]) < 0.3:
            findings.append({"pattern": "thin band", "band": bands[k]["name"],
                             "average": fl.mean(widths[k])})

    # backlog growth
    if bands[0]["kind"] == "backlog":
        a, b = _quarter_means(widths[0])
        if a is not None and b >= max(1.5 * a, a + 10):
            findings.append({"pattern": "backlog growth", "from": a, "to": b})

    wip_now = sum(widths[k][-1] for k in flow_idx)
    return {"findings": findings, "wip_now": wip_now,
            "delivered": lines[done_k][-1] - lines[done_k][0]}


def sentence(f):
    p = f["pattern"]
    if p == "bulge":
        s = (f"The band {f['band']} bulges: it held {f['from']:.0f} items on average in the first quarter "
             f"of the period, and {f['to']:.0f} in the last quarter. Items arrive there faster than they leave.")
        if f.get("start_queue") and f["next"]:
            s += (f" {f['band']} is the queue before work starts. The teams commit more items than "
                  f"{f['next']} can start. Commit less at planning, or find what slows {f['next']}.")
        elif f["kind"] == "wait" and f["next"]:
            s += f" {f['band']} is a queue, so {f['next']} is the likely bottleneck."
        elif f["kind"] == "active":
            s += f" The work in {f['band']} takes longer, or more work starts there than the people can finish."
        return s
    if p == "stair-steps":
        per = f", about once every {f['period_days']:.0f} working days" if f.get("period_days") else ""
        what = {"commitment": "Work is committed in batches, for example at the start of each iteration. "
                              "Items then wait until somebody can start them.",
                "release": "Items reach Done in batches. This looks like a release at fixed dates, so "
                           "finished work waits for the release.",
                "handoff": f"Work moves {f['where']} in batches. A handoff waits for a batch, for example a "
                           f"test environment or a review meeting."}[f["role"]]
        return (f"The line {f['where']} has stair-steps: {f['share'] * 100:.0f}% of the moves happened on "
                f"{f['days_share'] * 100:.0f}% of the working days{per}. {what}")
    if p == "divergence":
        if f["direction"] == "wip grows":
            return (f"In the last six weeks, {f['arrivals']:.1f} items each week entered the flow and "
                    f"{f['departures']:.1f} reached Done. The lines diverge, so the work in progress grows. "
                    f"By Little's law, the flow time will grow too. Stop starting, and start finishing.")
        return (f"In the last six weeks, {f['arrivals']:.1f} items each week entered the flow and "
                f"{f['departures']:.1f} reached Done. The work in progress falls. Make sure that enough "
                f"work is ready, or the teams will wait for work.")
    if p == "flat departures":
        return (f"No item reached Done for {f['workdays']} working days, until {f['until']}. "
                f"Find out what stopped delivery in that period.")
    if p == "thin band":
        return (f"The band {f['band']} is almost empty ({f['average']:.1f} items on average). The team "
                f"skips this status, or moves items through it at the same time. Make sure that the board "
                f"matches the real work.")
    if p == "too little data":
        return (f"Only {f['items']} {'item' if f['items'] == 1 else 'items'} entered the flow in the period. This is too little data to find "
                f"patterns. Use a longer period, or more teams.")
    if p == "backlog growth":
        return (f"The backlog grew from {f['from']:.0f} to {f['to']:.0f} items on average. More work arrives "
                f"than the system starts. Refine and remove old items, and make the backlog limit explicit.")
    return str(f)


def markdown(cfd, res):
    L = ["# Cumulative flow diagram: findings", ""]
    scope = (f"Period: {cfd['days'][0].isoformat()} to {cfd['days'][-1].isoformat()}"
             + (f", team {cfd['team']}" if cfd["team"] else "") + ".")
    if cfd["fictional"]:
        scope += " The data is fictional."
    L += [scope, ""]
    if res["findings"]:
        L.append(" ".join(sentence(f) for f in res["findings"]))
    else:
        L.append("The CFD shows no known pattern. The bands keep their width, and the lines go up smoothly.")
    L.append("")
    L.append(f"At this time, {res['wip_now']} items are in progress. In the period, {res['delivered']} items "
             "reached Done.")
    if cfd["bulk_excluded"]:
        L.append(f"{len(cfd['bulk_excluded'])} items closed by a bulk move are not in the CFD.")
    L.append("")
    L.append("These findings are patterns in the data. Ask the teams what causes them before you act.")
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------- SVG

RAMP = ["#0d366b", "#184f95", "#2a78d6", "#5598e7", "#86b6ef"]   # validated ordinal ramp, dark to light
BACKLOG = "#b5b4ad"
SURFACE = "#fcfcfb"
INK, INK2 = "#0b0b0b", "#52514e"


def band_styles(bands):
    """Done is the darkest. Each active stage gets the next lighter step. A wait band takes the
    color of the stage that it waits for, with hatching."""
    styles = [None] * len(bands)
    n = len(bands)
    styles[n - 1] = (RAMP[0], False)
    step = 1
    for k in range(n - 2, -1, -1):
        b = bands[k]
        if b["kind"] == "backlog":
            styles[k] = (BACKLOG, False)
        elif b["kind"] == "active":
            styles[k] = (RAMP[min(step, len(RAMP) - 1)], False)
            step += 1
    for k in range(n - 2, -1, -1):
        if styles[k] is None:
            nxt = next(styles[j][0] for j in range(k + 1, n) if styles[j] and not styles[j][1])
            styles[k] = (nxt, True)
    return styles


def svg(cfd, res, path):
    bands, days, counts = cfd["bands"], cfd["days"], cfd["counts"]
    W, H = 960, 460
    ml, mr, mt, mb = 56, 150, 48, 64
    pw, ph = W - ml - mr, H - mt - mb
    tops = cumulative(cfd)
    ymax = max(tops[0]) or 1
    nice = 10 ** max(0, int(math.log10(ymax)))
    ymax = math.ceil(ymax / nice) * nice
    x = lambda i: ml + pw * i / max(1, len(days) - 1)  # noqa: E731
    y = lambda v: mt + ph - ph * v / ymax  # noqa: E731
    styles = band_styles(bands)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="system-ui, sans-serif" '
           f'role="img" aria-label="Cumulative flow diagram">',
           f'<rect width="{W}" height="{H}" fill="{SURFACE}"/>',
           "<defs>"]
    for i, (c, hatch) in enumerate(styles):
        if hatch:
            out.append(f'<pattern id="h{i}" width="6" height="6" patternUnits="userSpaceOnUse" '
                       f'patternTransform="rotate(45)"><rect width="6" height="6" fill="{SURFACE}"/>'
                       f'<rect width="3" height="6" fill="{c}"/></pattern>')
    out.append("</defs>")
    title = "Cumulative flow" + (f": {cfd['team']}" if cfd["team"] else "")
    out.append(f'<text x="{ml}" y="24" font-size="16" font-weight="600" fill="{INK}">{title}</text>')
    out.append(f'<text x="{ml}" y="40" font-size="12" fill="{INK2}">Items in each stage at the end of each day. '
               f'Hatched bands are queues.</text>')
    for t in range(0, int(ymax) + 1, max(1, int(ymax // 5))):
        out.append(f'<line x1="{ml}" x2="{ml + pw}" y1="{y(t):.1f}" y2="{y(t):.1f}" stroke="#e4e3df" stroke-width="1"/>')
        out.append(f'<text x="{ml - 8}" y="{y(t) + 4:.1f}" font-size="11" text-anchor="end" fill="{INK2}">{t}</text>')
    for k in range(len(bands)):
        upper = tops[k]
        lower = tops[k + 1] if k + 1 < len(bands) else [0] * len(days)
        pts = [f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(upper)]
        pts += [f"{x(i):.1f},{y(v):.1f}" for i, v in reversed(list(enumerate(lower)))]
        c, hatch = styles[k]
        fill = f"url(#h{k})" if hatch else c
        now = counts[-1][k]
        out.append(f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{SURFACE}" stroke-width="1.5">'
                   f'<title>{bands[k]["name"]} ({bands[k]["kind"]}): {now} items at the end</title></polygon>')
        mid = (upper[-1] + lower[-1]) / 2
        if (upper[-1] - lower[-1]) / ymax > 0.04:
            out.append(f'<text x="{ml + pw + 8}" y="{y(mid) + 4:.1f}" font-size="11" fill="{INK}">'
                       f'{bands[k]["name"]} {now}</text>')
    months = [i for i, d in enumerate(days) if d.day == 1]
    for i in months:
        out.append(f'<text x="{x(i):.1f}" y="{mt + ph + 18}" font-size="11" text-anchor="middle" '
                   f'fill="{INK2}">{days[i].strftime("%b %Y")}</text>')
    out.append(f'<line x1="{ml}" x2="{ml + pw}" y1="{mt + ph}" y2="{mt + ph}" stroke="{INK2}" stroke-width="1"/>')
    lx = ml
    ly = H - 18
    for k in range(len(bands) - 1, -1, -1):
        c, hatch = styles[k]
        fill = f"url(#h{k})" if hatch else c
        label = bands[k]["name"]
        out.append(f'<rect x="{lx}" y="{ly - 10}" width="12" height="12" rx="2" fill="{fill}" stroke="{INK2}" stroke-width="0.5"/>')
        out.append(f'<text x="{lx + 16}" y="{ly}" font-size="11" fill="{INK}">{label}</text>')
        lx += 16 + 7 * len(label) + 18
    out.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def write_csv(cfd, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date"] + [b["name"] for b in cfd["bands"]])
        for d, row in zip(cfd["days"], cfd["counts"]):
            w.writerow([d.isoformat()] + row)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("flow")
    ap.add_argument("map")
    ap.add_argument("--window", type=int, default=182)
    ap.add_argument("--as-of")
    ap.add_argument("--team")
    ap.add_argument("--bulk", type=int, default=8)
    ap.add_argument("--svg")
    ap.add_argument("--csv")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    a = ap.parse_args(argv)
    flow = fl.load_flow(a.flow)
    smap = fl.StatusMap(fl.load_json(a.map))
    cfd = build(flow, smap, a.window, a.as_of, a.team, a.bulk)
    res = analyze(cfd)
    if a.svg:
        svg(cfd, res, a.svg)
    if a.csv:
        write_csv(cfd, a.csv)
    if a.format == "json":
        print(json.dumps({"findings": res["findings"], "sentences": [sentence(f) for f in res["findings"]],
                          "wip_now": res["wip_now"], "delivered": res["delivered"],
                          "bands": [b["name"] for b in cfd["bands"]]}, indent=1, default=str))
    else:
        print(markdown(cfd, res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
