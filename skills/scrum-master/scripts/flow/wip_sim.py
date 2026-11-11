#!/usr/bin/env python3
"""Monte Carlo simulation of a kanban system: what a change in WIP limits or people does.

  python wip_sim.py model.json                               # baseline, and a check against history
  python wip_sim.py model.json --set Testing=4               # what if Testing has a WIP limit of 4?
  python wip_sim.py model.json --delta Testing=-2            # what if the limit of Testing is 2 lower?
  python wip_sim.py model.json --set Testing.workers=3       # what if Testing has 3 people?
  python wip_sim.py model.json --sweep Testing=1:10          # try each limit, and recommend one
  python wip_sim.py model.json --set swarm_efficiency=0.5 --sweep Development=2:12

Other settings for --set: release_every_days=N (or none), commit_every_days=N (or none),
arrivals_per_week=N (or unlimited), swarm_efficiency=0..1.

The model (flow_report.py --emit-model writes a first version):
  stages        The active stages in order. Each has "workers" (people), "wip_limit" (null for no
                limit) and "service_days" (samples of the time that an item spent in the stage).
                The WIP limit of a stage counts the items in its queue (for example "Ready for
                Test" for Testing), the items in work, and the finished items that cannot move
                on because the next stage is full. The commitment queue before the first stage
                and the items that wait for a release are outside all limits.
  arrivals_per_week   How many items the system commits each week. null or "unlimited": the
                      first stage always has work to pull (use it to find the capacity).
  commit_every_days   Commit the arrivals in one batch every N working days (sprint planning).
  release_every_days  Finished items leave only every N working days (a batch release).
  swarm_efficiency    0 to 1. Idle people of an earlier stage help a later stage at this rate.

The simulation steps one working day at a time. Each person works on one item at a time. A
stage pulls an item when a person is free and the stage is below its WIP limit. The service
times are samples from the history, so they include the normal interruptions of the team.

The output gives a range, not a promise. Standard library only.
"""
import argparse
import copy
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flowlib as fl  # noqa: E402


# --------------------------------------------------------------------------- model

def load_model(path):
    m = fl.load_json(path)
    for st in m.get("stages", []):
        if not st.get("service_days"):
            raise SystemExit(f"Stage {st.get('name')!r} has no service_days samples.")
        st.setdefault("workers", 1)
        st.setdefault("wip_limit", None)
    m.setdefault("days_per_week", 5)
    return m


def _num(v):
    if v is None or str(v).lower() in ("none", "null", "unlimited", "off"):
        return None
    f = float(v)
    return int(f) if f.is_integer() else f


def apply_changes(model, sets=(), deltas=()):
    m = copy.deepcopy(model)
    names = {s["name"].lower(): s for s in m["stages"]}
    for expr in sets:
        key, _, val = expr.partition("=")
        key = key.strip()
        if "." in key:
            sname, field = key.rsplit(".", 1)
        else:
            sname, field = key, "wip_limit"
        if sname.lower() in names:
            st = names[sname.lower()]
            if field not in ("wip_limit", "workers"):
                raise SystemExit(f"--set {expr}: a stage has wip_limit and workers.")
            st[field] = _num(val)
            if field == "workers" and (st[field] is None or st[field] < 1):
                raise SystemExit(f"--set {expr}: a stage needs one worker or more.")
        elif key in ("release_every_days", "commit_every_days", "arrivals_per_week", "swarm_efficiency"):
            m[key] = _num(val)
        else:
            raise SystemExit(f"--set {expr}: no stage or setting with the name {sname!r}. "
                             f"Stages: {', '.join(s['name'] for s in m['stages'])}.")
    for expr in deltas:
        key, _, val = expr.partition("=")
        sname, _, field = key.strip().partition(".")
        field = field or "wip_limit"
        st = names.get(sname.lower())
        if st is None:
            raise SystemExit(f"--delta {expr}: no stage with the name {sname!r}.")
        if st.get(field) is None:
            raise SystemExit(f"--delta {expr}: {st['name']} has no {field} at this time. Use --set.")
        st[field] = max(1, int(st[field] + float(val)))
    return m


def describe(model):
    parts = []
    for s in model["stages"]:
        lim = "no limit" if s.get("wip_limit") is None else f"WIP {s['wip_limit']}"
        who = "1 person" if s["workers"] == 1 else f"{s['workers']} people"
        parts.append(f"{s['name']} ({who}, {lim})")
    extra = []
    if model.get("arrivals_per_week") is None:
        extra.append("unlimited demand")
    else:
        extra.append(f"{fl.fmt(float(model['arrivals_per_week']))} arrivals each week")
    if model.get("commit_every_days"):
        extra.append(f"commit every {model['commit_every_days']} days")
    if model.get("release_every_days"):
        extra.append(f"release every {model['release_every_days']} days")
    if model.get("swarm_efficiency"):
        extra.append(f"swarming at {model['swarm_efficiency']:.0%}")
    return "; ".join(parts) + ". " + ", ".join(extra) + "."


# --------------------------------------------------------------------------- simulation

def poisson(rng, lam):
    if lam <= 0:
        return 0
    if lam > 30:
        return max(0, int(round(rng.gauss(lam, math.sqrt(lam)))))
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1


def run_once(model, rng, days, warmup):
    """One run. The WIP of a stage is its queue (the items that wait for it), its items in work,
    and its finished items that cannot move on because the next stage is full."""
    stages = model["stages"]
    n = len(stages)
    queue = [[] for _ in range(n)]      # queue[0] is the commitment queue, outside all WIP limits
    doing = [[] for _ in range(n)]      # items: dict(arr, rem, owner, rate)
    held = [[] for _ in range(n)]       # finished, the next stage is full
    release_q = []                      # finished by the last stage, waiting for a release
    unlimited = model.get("arrivals_per_week") is None
    per_day = (model.get("arrivals_per_week") or 0) / model["days_per_week"]
    commit_n = model.get("commit_every_days")
    release_n = model.get("release_every_days")
    swarm = float(model.get("swarm_efficiency") or 0)
    pending = 0.0
    exits, leads, wip_days = 0, [], []
    busy = [0.0] * n
    idle_blocked = [0.0] * n
    idle_starved = [0.0] * n

    def owned(j):
        return sum(1 for k in range(n) for it in doing[k] if it["owner"] == j)

    def wip(k):
        return (len(queue[k]) if k > 0 else 0) + len(doing[k]) + len(held[k])

    def room(k):
        lim = stages[k].get("wip_limit")
        return lim is None or wip(k) < lim

    def move_on():
        for k in range(n - 1, -1, -1):
            if k == n - 1:
                release_q.extend(held[k])
                held[k] = []
                continue
            while held[k] and room(k + 1):
                queue[k + 1].append(held[k].pop(0))

    def start(k, it, owner, rate):
        it.update(rem=rng.choice(stages[k]["service_days"]), owner=owner, rate=rate)
        doing[k].append(it)

    for d in range(days):
        if not unlimited:
            if commit_n:
                pending += per_day
                cnt = 0
                if d % int(commit_n) == 0:
                    cnt, pending = poisson(rng, pending), 0.0
            else:
                cnt = poisson(rng, per_day)
            queue[0].extend({"arr": d} for _ in range(cnt))
        move_on()
        # each free person pulls from the queue of the own stage
        for k in range(n - 1, -1, -1):
            free = stages[k]["workers"] - owned(k)
            if k == 0:
                while free > 0 and room(0) and (queue[0] or unlimited):
                    it = queue[0].pop(0) if queue[0] else {"arr": d}
                    if unlimited:
                        it["arr"] = d
                    start(0, it, 0, 1.0)
                    free -= 1
            else:
                while free > 0 and queue[k]:
                    start(k, queue[k].pop(0), k, 1.0)
                    free -= 1
        # free people help a later stage that has a queue
        if swarm > 0:
            for k in range(n - 1, 0, -1):
                for j in range(k - 1, -1, -1):
                    while queue[k] and stages[j]["workers"] - owned(j) > 0:
                        start(k, queue[k].pop(0), j, swarm)
        if d >= warmup:
            for j in range(n):
                free = stages[j]["workers"] - owned(j)
                if free <= 0:
                    continue
                if j == 0 and (queue[0] or unlimited) and not room(0):
                    idle_blocked[j] += free
                elif j > 0 and held[j]:
                    idle_blocked[j] += free
                else:
                    idle_starved[j] += free
        for k in range(n):
            still = []
            for it in doing[k]:
                it["rem"] -= it["rate"]
                if d >= warmup:
                    busy[it["owner"]] += 1
                (still if it["rem"] > 1e-9 else held[k]).append(it)
            doing[k] = still
        move_on()
        if not release_n or d % int(release_n) == int(release_n) - 1:
            for it in release_q:
                if d >= warmup:
                    exits += 1
                    leads.append(d - it["arr"] + 1)
            release_q = []
        if d >= warmup:
            wip_days.append((0 if unlimited else len(queue[0])) + sum(wip(k) for k in range(n))
                            + len(release_q))
    span = days - warmup
    weeks = span / model["days_per_week"]
    cap = [stages[j]["workers"] * span for j in range(n)]
    return {
        "throughput_per_week": exits / weeks,
        "leads": leads,
        "avg_wip": fl.mean(wip_days),
        "end_queue": len(queue[0]),
        "utilization": [busy[j] / cap[j] for j in range(n)],
        "idle_blocked": [idle_blocked[j] / cap[j] for j in range(n)],
        "idle_starved": [idle_starved[j] / cap[j] for j in range(n)],
    }


def simulate(model, runs=300, days=130, warmup=30, seed=42):
    rs = [run_once(model, random.Random(seed + i), days + warmup, warmup) for i in range(runs)]
    n = len(model["stages"])
    tp = [r["throughput_per_week"] for r in rs]
    pooled = [x for r in rs for x in r["leads"]]
    return {
        "model": describe(model),
        "runs": runs, "days": days,
        "throughput_mean": fl.mean(tp), "throughput_p10": fl.percentile(tp, 10),
        "throughput_p90": fl.percentile(tp, 90),
        "lead_p50": fl.percentile(pooled, 50), "lead_p85": fl.percentile(pooled, 85),
        "avg_wip": fl.mean([r["avg_wip"] for r in rs]),
        "queue_growth": fl.mean([r["end_queue"] for r in rs]),
        "stages": [{
            "name": model["stages"][j]["name"],
            "utilization": fl.mean([r["utilization"][j] for r in rs]),
            "idle_blocked": fl.mean([r["idle_blocked"][j] for r in rs]),
            "idle_starved": fl.mean([r["idle_starved"][j] for r in rs]),
        } for j in range(n)],
    }


# --------------------------------------------------------------------------- output

def pct(x):
    return "TBD" if x is None else f"{x * 100:.0f}%"


def result_table(rows, label="Scenario"):
    names = [s["name"] for s in rows[0][1]["stages"]]
    head = (f"| {label} | Items each week (p10 to p90) | Lead time p50 | Lead time p85 | Average WIP | "
            + " | ".join(f"{n}: busy, blocked, starved" for n in names) + " |")
    out = [head, "|" + "---|" * (5 + len(names))]
    for name, r in rows:
        cells = [name, f"{r['throughput_mean']:.1f} ({r['throughput_p10']:.1f} to {r['throughput_p90']:.1f})",
                 fl.fmt(r["lead_p50"], 0), fl.fmt(r["lead_p85"], 0), fl.fmt(r["avg_wip"])]
        for s in r["stages"]:
            cells.append(f"{pct(s['utilization'])}, {pct(s['idle_blocked'])}, {pct(s['idle_starved'])}")
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def overload(model, r):
    arr = model.get("arrivals_per_week")
    if arr is None or not r["throughput_mean"]:
        return None
    if arr > r["throughput_mean"] * 1.05:
        return (f"The system commits {arr:.1f} items each week but finishes {r['throughput_mean']:.1f}. "
                f"The commitment queue grows, so the lead time grows during the run "
                f"(on average {r['queue_growth']:.0f} {'item waits' if round(r['queue_growth']) == 1 else 'items wait'} at the end). WIP limits cannot correct this. "
                f"Commit fewer items, or add capacity at the constraint.")
    return None


def calibration(model, base):
    h = model.get("history") or {}
    if not h.get("throughput_per_week"):
        return None
    tp_h, tp_s = h["throughput_per_week"], base["throughput_mean"]
    lines = [f"History: {tp_h:.1f} items each week, flow time p50 {fl.fmt(h.get('flow_time_p50'), 0)} days. "
             f"Baseline simulation: {tp_s:.1f} items each week, lead time p50 {fl.fmt(base['lead_p50'], 0)} days."]
    if abs(tp_s - tp_h) / tp_h > 0.25:
        lines.append("The baseline does not match the history (more than 25% difference in throughput). "
                     "Make sure that the workers, the arrivals and the batches in the model are correct "
                     "before you use a what-if result.")
    else:
        lines.append("The throughput of the baseline is within 25% of the history.")
    return " ".join(lines)


def sweep(model, spec, runs, days, warmup, seed, tolerance, max_blocked):
    sname, _, rng_txt = spec.partition("=")
    lo, _, hi = rng_txt.partition(":")
    lo, hi = int(lo), int(hi or lo)
    names = [s["name"].lower() for s in model["stages"]]
    if sname.strip().lower() not in names:
        raise SystemExit(f"--sweep {spec}: no stage with the name {sname!r}.")
    idx = names.index(sname.strip().lower())
    rows = []
    for lim in list(range(lo, hi + 1)) + [None]:
        m = apply_changes(model, [f"{model['stages'][idx]['name']}={lim if lim is not None else 'none'}"])
        rows.append((lim, simulate(m, runs, days, warmup, seed)))
    best = max(r["throughput_mean"] for _, r in rows)
    ok = [(lim, r) for lim, r in rows if lim is not None and r["throughput_mean"] >= (1 - tolerance) * best]
    calm = [(lim, r) for lim, r in ok
            if all(st["idle_blocked"] <= max_blocked for st in r["stages"][:idx])]
    rec = min(calm or ok, key=lambda x: x[0]) if ok else None
    return idx, rows, rec, best, bool(calm)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("model")
    ap.add_argument("--set", action="append", default=[], dest="sets")
    ap.add_argument("--delta", action="append", default=[])
    ap.add_argument("--sweep")
    ap.add_argument("--runs", type=int, default=300)
    ap.add_argument("--days", type=int, default=130, help="working days to measure (130 = six months)")
    ap.add_argument("--warmup", type=int, default=30)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--tolerance", type=float, default=0.05,
                    help="--sweep: the lowest limit with a throughput within this share of the best")
    ap.add_argument("--max-blocked", type=float, default=0.15,
                    help="--sweep: the most time that the people of earlier stages can be blocked")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    a = ap.parse_args(argv)

    model = load_model(a.model)
    base = simulate(model, a.runs, a.days, a.warmup, a.seed)
    out = {"baseline": base, "calibration": calibration(model, base)}
    L = ["# Kanban simulation", "",
         f"{a.runs} runs of {a.days} working days each, after {a.warmup} days to fill the system. "
         "Lead time is in working days, from commitment to Done. "
         "Busy, blocked and starved are shares of the time of the people of each stage: "
         "blocked means that the people finished work but a WIP limit stopped it, and starved means that no work waited for them.",
         "", f"Baseline: {base['model']}", ""]
    if out["calibration"]:
        L += [out["calibration"], ""]
    if overload(model, base):
        L += [overload(model, base), ""]

    scen = None
    if a.sets or a.delta:
        m2 = apply_changes(model, a.sets, a.delta)
        scen = simulate(m2, a.runs, a.days, a.warmup, a.seed)
        out["scenario"] = scen
        L += ["## What if", "", f"Scenario: {scen['model']}", "",
              result_table([("Baseline", base), ("Scenario", scen)]), ""]
        dtp = scen["throughput_mean"] - base["throughput_mean"]
        dl = (scen["lead_p85"] or 0) - (base["lead_p85"] or 0)
        L.append(f"The throughput changes by {dtp:+.1f} items each week "
                 f"({dtp / base['throughput_mean'] * 100:+.0f}%). The lead time at the 85th percentile "
                 f"changes by {dl:+.0f} working days.")
        if overload(m2, scen):
            L.append(overload(m2, scen))
        L.append("")
    else:
        L += [result_table([("Baseline", base)]), ""]
    if a.sweep:
        src = apply_changes(model, a.sets, a.delta) if (a.sets or a.delta) else model
        idx, rows, rec, best, calm = sweep(src, a.sweep, a.runs, a.days, a.warmup, a.seed, a.tolerance,
                                           a.max_blocked)
        sname = src["stages"][idx]["name"]
        out["sweep"] = {"stage": sname, "rows": [{"wip_limit": lim, **r} for lim, r in rows],
                        "recommended": rec[0] if rec else None}
        L += [f"## WIP limits for {sname}", "",
              result_table([(str(lim) if lim is not None else "no limit", r) for lim, r in rows],
                           label="WIP limit"), ""]
        upstream_open = [s["name"] for s in src["stages"][:idx] if s.get("wip_limit") is None]
        if upstream_open:
            L.append(f"{', '.join(upstream_open)} has no WIP limit. A limit on {sname} alone moves the "
                     f"wait into the earlier stage, and the lead time does not change. Give the earlier "
                     f"stage a limit too, for example --set {upstream_open[-1]}=N.")
            L.append("")
        if rec:
            lim, r = rec
            none_row = rows[-1][1]
            rule = (f"throughput within {a.tolerance:.0%} of the best, with the people of the earlier stages "
                    f"blocked for {a.max_blocked:.0%} of the time or less" if calm else
                    f"throughput within {a.tolerance:.0%} of the best. No limit keeps the people of the earlier "
                    f"stages blocked for {a.max_blocked:.0%} of the time or less")
            L.append(f"Recommendation: a WIP limit of {lim} for {sname}. It is the lowest limit with a "
                     f"{rule} ({r['throughput_mean']:.1f} against "
                     f"{best:.1f} items each week). The lead time at the 85th percentile is "
                     f"{fl.fmt(r['lead_p85'], 0)} working days, against {fl.fmt(none_row['lead_p85'], 0)} "
                     f"with no limit.")
            for j, st in enumerate(r["stages"][:idx]):
                if st["idle_blocked"] > 0.1:
                    L.append(f"At this limit, the people of {st['name']} are blocked {pct(st['idle_blocked'])} "
                             f"of the time. Let them help {sname} (try --set swarm_efficiency=0.5), or move "
                             f"capacity, before you lower the limit more.")
            if src.get("commit_every_days") or src.get("release_every_days"):
                L.append("The batches (commit_every_days, release_every_days) decide most of the lead time. "
                         "To see the effect of the WIP limit alone, try --set commit_every_days=none "
                         "--set release_every_days=none.")
            L.append("Use the result as the start of an experiment of two iterations, not as a final number.")
        L.append("")
    if a.format == "json":
        print(json.dumps(out, indent=1, default=str))
    else:
        print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
