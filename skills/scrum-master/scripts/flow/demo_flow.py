#!/usr/bin/env python3
"""Make fictional flow data for an Agile Release Train (ART) with three teams.

  python demo_flow.py [-o ../../assets/sample_flow_data.json] [--seed 7]

All teams, keys and figures are fictional. The data has the problems that the flow scripts
must find:
  - Each team uses different status names for the same stage (data noise).
  - Two teams have one tester for three developers. Work waits before testing (a bottleneck).
  - Two teams release only at the end of each two-week iteration (batching).
  - Stories without the label dor-met (the Definition of Ready was not met) come back from
    testing more often (rework).
  - On 2026-08-14, a board clean-up moved many old items in one minute (bulk moves).

Standard library only.
"""
import argparse
import datetime as dt
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, "..", "..", "assets", "sample_flow_data.json")

START = dt.date(2026, 5, 4)      # a Monday
END = dt.date(2026, 11, 6)       # a Friday
CLEANUP = dt.date(2026, 8, 14)

TEAMS = {
    "CLM": {"devs": 3, "testers": 1, "plan": 7, "release": "iteration", "blocked": 0.0,
            "s": {"backlog": "To Do", "ready": "Selected for Development", "dev": "In Progress",
                  "q_test": "Ready for QA", "test": "In QA", "q_rel": "Ready for Release",
                  "done": "Done"}},
    "ELG": {"devs": 3, "testers": 2, "plan": 7, "release": "weekly", "blocked": 0.0,
            "s": {"backlog": "Backlog", "ready": "Ready", "dev": "In Development",
                  "q_test": "Dev Complete", "test": "Testing", "q_rel": "Awaiting Deploy",
                  "done": "Closed"}},
    "PAY": {"devs": 3, "testers": 1, "plan": 6, "release": "iteration", "blocked": 0.12,
            "s": {"backlog": "To Do", "ready": "Selected for Development", "dev": "In Progress",
                  "q_test": "Ready for QA", "test": "Testing", "q_rel": "Ready for Release",
                  "done": "Done"}},
}


def ts(day, hour, minute=0):
    return dt.datetime.combine(day, dt.time(hour, minute), tzinfo=dt.timezone.utc).isoformat()


def workdays(a, b):
    d = a
    while d <= b:
        if d.weekday() < 5:
            yield d
        d += dt.timedelta(days=1)


def lognorm(rng, median, sigma=0.5):
    return max(0.3, median * math.exp(rng.gauss(0, sigma)))


def simulate(seed=7):
    rng = random.Random(seed)
    items = []
    days = list(workdays(START, END))
    for key, cfg in TEAMS.items():
        s = cfg["s"]
        n = 0
        backlog, ready, q_test, q_rel = [], [], [], []
        devs = [None] * cfg["devs"]
        testers = [None] * cfg["testers"]
        blocked = []          # [item, days_left]

        def new_item(day, hour):
            nonlocal n
            n += 1
            r = rng.random()
            it = {"id": f"{key}-{n}", "type": "Story" if r < 0.7 else ("Bug" if r < 0.9 else "Enabler"),
                  "team": key, "created": ts(day, hour, rng.randrange(60)),
                  "labels": ["dor-met"] if rng.random() < 0.6 else [],
                  "transitions": [], "status": s["backlog"]}
            items.append(it)
            return it

        def move(it, to, day, hour):
            at = ts(day, hour, rng.randrange(60))
            last = it["transitions"][-1]["at"] if it["transitions"] else it["created"]
            if at <= last:
                at = (dt.datetime.fromisoformat(last) + dt.timedelta(minutes=rng.randrange(5, 90))).isoformat()
            it["transitions"].append({"at": at, "from": it["status"], "to": to})
            it["status"] = to

        for i in range(14):
            backlog.append(new_item(START - dt.timedelta(days=20 - i), 10))

        for idx, day in enumerate(days):
            iteration_day = idx % 10
            for _ in range(sum(1 for _ in range(3) if rng.random() < 0.3)):
                backlog.append(new_item(day, rng.randrange(9, 17)))
            if day == CLEANUP and key == "CLM":
                for j, it in enumerate(list(backlog[:12])):
                    to = "Done" if j < 4 else "Won't Do"
                    it["transitions"].append({"at": ts(day, 10, 0), "from": it["status"], "to": to})  # bulk move
                    it["status"] = to
                    backlog.remove(it)
            if iteration_day == 0:
                for _ in range(cfg["plan"]):
                    if backlog:
                        it = backlog.pop(0)
                        move(it, s["ready"], day, 10)
                        ready.append(it)
            # blocked items come back
            for b in list(blocked):
                b[1] -= 1
                if b[1] <= 0:
                    blocked.remove(b)
                    move(b[0], s["dev"], day, 9)
                    b[0]["_back"] = True
                    for k in range(len(devs)):
                        if devs[k] is None:
                            devs[k] = [b[0], b[0]["_rem"]]
                            break
                    else:
                        ready.insert(0, b[0])
            # developers pull (rework first, then ready)
            for k in range(len(devs)):
                if devs[k] is None and ready:
                    it = ready.pop(0)
                    if it.get("_rework"):
                        rem = lognorm(rng, 1.0, 0.4)
                    elif it.get("_back"):
                        rem = it["_rem"]
                    else:
                        rem = lognorm(rng, 2.0 if "dor-met" in it["labels"] else 3.2)
                    if it["status"] != s["dev"]:
                        move(it, s["dev"], day, rng.randrange(9, 12))
                    if not it.get("_rework") and rng.random() < cfg["blocked"]:
                        move(it, "Blocked", day, 15)
                        it["_rem"] = rem
                        blocked.append([it, rng.randrange(2, 6)])
                        continue
                    devs[k] = [it, rem]
            # testers pull
            for k in range(len(testers)):
                if testers[k] is None and q_test:
                    it = q_test.pop(0)
                    move(it, s["test"], day, rng.randrange(9, 12))
                    testers[k] = [it, lognorm(rng, 0.9, 0.45)]
            # work
            for k in range(len(devs)):
                if devs[k]:
                    devs[k][1] -= 1
                    if devs[k][1] <= 0:
                        it = devs[k][0]
                        move(it, s["q_test"], day, rng.randrange(13, 17))
                        it.pop("_rework", None)
                        q_test.append(it)
                        devs[k] = None
            for k in range(len(testers)):
                if testers[k]:
                    testers[k][1] -= 1
                    if testers[k][1] <= 0:
                        it = testers[k][0]
                        p_rework = 0.08 if "dor-met" in it["labels"] else 0.35
                        if rng.random() < p_rework and not it.get("_reworked"):
                            move(it, s["dev"], day, rng.randrange(13, 17))
                            it["_rework"] = it["_reworked"] = True
                            ready.insert(0, it)
                        else:
                            move(it, s["q_rel"], day, rng.randrange(13, 17))
                            q_rel.append(it)
                        testers[k] = None
            # release
            release = (cfg["release"] == "iteration" and iteration_day == 9) or \
                      (cfg["release"] == "weekly" and day.weekday() == 4)
            if release:
                for it in q_rel:
                    move(it, s["done"], day, 17)
                q_rel.clear()
    for it in items:
        for k in [k for k in it if k.startswith("_")]:
            del it[k]
    items.sort(key=lambda x: x["created"])
    return items


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--output", default=DEFAULT_OUT)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args(argv)
    items = simulate(a.seed)
    head = {"source": "demo", "anonymized": False, "fictional": True,
            "note": "Fictional data from demo_flow.py. Three teams of one ART."}
    with open(a.output, "w", encoding="utf-8") as f:
        f.write(json.dumps(head)[:-1] + ',\n "items": [\n')
        f.write(",\n".join("  " + json.dumps(it) for it in items))
        f.write("\n ]\n}\n")
    print(f"Wrote {len(items)} fictional items to {a.output}")


if __name__ == "__main__":
    main()
