#!/usr/bin/env python3
"""Shared code for the flow scripts: read flow data, map statuses to stages, and measure time.

Flow data is a JSON file in this shape (flow_prepare.py writes it from Jira, Azure DevOps or a
CSV file):

  {
    "source": "jira",
    "anonymized": true,
    "items": [
      {
        "id": "I-3f2a9c1b",
        "type": "Story",
        "team": "Team 1",
        "created": "2026-05-04T09:12:00+00:00",
        "status": "Done",                       # current status, optional
        "labels": ["dor-met"],                  # optional
        "transitions": [
          {"at": "2026-05-06T10:00:00+00:00", "from": "To Do", "to": "In Progress"}
        ]
      }
    ]
  }

A status map tells the scripts what each raw status means. It puts the statuses of all teams
into one list of stages, in the order of the value stream:

  {
    "stages": [
      {"name": "Backlog",     "kind": "backlog", "statuses": ["To Do", "Backlog"]},
      {"name": "Development", "kind": "active",  "statuses": ["In Progress", "In Development"]},
      {"name": "Ready for Test", "kind": "wait", "statuses": ["Ready for QA", "Dev Complete"]},
      {"name": "Testing",     "kind": "active",  "statuses": ["In QA", "Testing"]},
      {"name": "Done",        "kind": "done",    "statuses": ["Done", "Closed"]}
    ],
    "blocked": ["Blocked", "On Hold"],
    "discarded": ["Won't Do", "Cancelled"]
  }

Kinds:
  backlog   before the commitment point. Not part of the flow time.
  wait      in the flow, but nobody works on the item (a queue or a handoff).
  active    somebody works on the item.
  done      the item is delivered. The flow time stops at the last entry into a done stage.
  blocked   (the "blocked" list) a wait state outside the stage order. The time counts as wait.
  discarded (the "discarded" list) the item left the flow without delivery. It is not counted.

The flow time of an item starts when it first enters a stage after the backlog (the commitment
point). Standard library only.
"""
import datetime as dt
import json
import math
import re
from collections import Counter, defaultdict

KINDS = ("backlog", "wait", "active", "done")
FLOW_KINDS = ("wait", "active")

UNMAPPED = "(unmapped)"
BLOCKED = "Blocked"


# --------------------------------------------------------------------------- time

def parse_time(value):
    """Parse an ISO 8601 time. A time without a zone is UTC. Jira writes +0000 without a colon."""
    if value is None or value == "":
        return None
    if isinstance(value, dt.datetime):
        t = value
    else:
        s = str(value).strip().replace("Z", "+00:00")
        m = re.match(r"^(.*[T ]\d\d:\d\d(?::\d\d(?:\.\d+)?)?)([+-]\d\d)(\d\d)$", s)
        if m:
            s = f"{m.group(1)}{m.group(2)}:{m.group(3)}"
        if len(s) == 10:
            s += "T00:00:00"
        t = dt.datetime.fromisoformat(s)
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return t.astimezone(dt.timezone.utc)


def iso(t):
    return t.astimezone(dt.timezone.utc).isoformat(timespec="seconds")


def days_between(start, end, workdays=False):
    """The time from start to end, in days. With workdays=True, Saturdays and Sundays do not count."""
    if end <= start:
        return 0.0
    if not workdays:
        return (end - start).total_seconds() / 86400.0
    total = 0.0
    cur = start
    while cur < end:
        next_midnight = dt.datetime.combine(cur.date() + dt.timedelta(days=1), dt.time(),
                                            tzinfo=cur.tzinfo)
        seg_end = min(end, next_midnight)
        if cur.weekday() < 5:
            total += (seg_end - cur).total_seconds() / 86400.0
        cur = seg_end
    return total


def percentile(values, p):
    """The p-th percentile (0-100), with linear interpolation. None for an empty list."""
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return None
    if len(vals) == 1:
        return vals[0]
    k = (len(vals) - 1) * p / 100.0
    lo, hi = math.floor(k), math.ceil(k)
    return vals[lo] + (vals[hi] - vals[lo]) * (k - lo)


def mean(values):
    vals = [v for v in values if v is not None]
    return sum(vals) / len(vals) if vals else None


# --------------------------------------------------------------------------- data

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_flow(path):
    data = load_json(path)
    if isinstance(data, list):
        data = {"items": data}
    for it in data.get("items", []):
        it["created"] = parse_time(it.get("created"))
        trs = []
        for tr in it.get("transitions", []):
            at = parse_time(tr.get("at"))
            if at is None:
                continue
            trs.append({"at": at, "from": tr.get("from"), "to": tr.get("to")})
        trs.sort(key=lambda x: x["at"])
        it["transitions"] = trs
        it.setdefault("labels", [])
        it.setdefault("type", "Item")
        it.setdefault("team", "")
    return data


def cut_at(items, as_of):
    """The items as they were at as_of: later items and later status changes are removed."""
    out = []
    for it in items:
        created = it.get("created") or (it["transitions"][0]["at"] if it["transitions"] else None)
        if created is not None and created > as_of:
            continue
        trs = [t for t in it["transitions"] if t["at"] <= as_of]
        if len(trs) == len(it["transitions"]):
            out.append(it)
            continue
        cp = dict(it)
        cp["transitions"] = trs
        cp["status"] = trs[-1]["to"] if trs else (it["transitions"][0]["from"] if it["transitions"] else it.get("status"))
        out.append(cp)
    return out


def as_of_time(items):
    """The latest time in the data. The scripts use it as "now", so the same data gives the same report."""
    latest = None
    for it in items:
        for t in [it.get("created")] + [tr["at"] for tr in it["transitions"]]:
            if t and (latest is None or t > latest):
                latest = t
    return latest


# --------------------------------------------------------------------------- status map

class StatusMap:
    def __init__(self, spec):
        self.spec = spec
        self.stages = []          # [{"name", "kind", "order"}] in value-stream order
        self.lookup = {}          # lower-case raw status -> stage name
        for i, st in enumerate(spec.get("stages", [])):
            kind = st.get("kind", "active")
            if kind not in KINDS:
                raise ValueError(f"Stage {st.get('name')!r}: kind must be one of {KINDS}, not {kind!r}")
            self.stages.append({"name": st["name"], "kind": kind, "order": i})
            for raw in st.get("statuses", [st["name"]]):
                self.lookup[raw.strip().lower()] = st["name"]
        self.blocked = {s.strip().lower() for s in spec.get("blocked", [])}
        self.discarded = {s.strip().lower() for s in spec.get("discarded", [])}
        self.by_name = {s["name"]: s for s in self.stages}

    def stage_of(self, raw):
        """The stage name of a raw status: a stage, BLOCKED, "discarded" or UNMAPPED."""
        if raw is None:
            return UNMAPPED
        key = str(raw).strip().lower()
        if key in self.lookup:
            return self.lookup[key]
        if key in self.blocked:
            return BLOCKED
        if key in self.discarded:
            return "discarded"
        return UNMAPPED

    def kind_of(self, stage):
        if stage in self.by_name:
            return self.by_name[stage]["kind"]
        if stage == BLOCKED:
            return "blocked"
        if stage == "discarded":
            return "discarded"
        return "unmapped"

    def order_of(self, stage):
        s = self.by_name.get(stage)
        return s["order"] if s else None

    def flow_stages(self):
        return [s for s in self.stages if s["kind"] in FLOW_KINDS]

    def done_stages(self):
        return [s for s in self.stages if s["kind"] == "done"]


WAIT_WORDS = r"wait|^ready$|ready for|ready to|queue|pending|awaiting|to be |dev done|dev complete|" \
             r"development done|code complete|build done|selected|approved|accepted"
BLOCK_WORDS = r"block|on hold|impediment|parked|paused|stuck"
DONE_WORDS = r"^done$|closed|released|resolved|deployed|delivered|complete$|completed$|shipped|live$"
DISCARD_WORDS = r"won'?t|cancel|reject|duplicate|obsolete|abandon|invalid|removed|not needed"
BACKLOG_WORDS = r"^to ?do$|backlog|^open$|^new$|funnel|idea|proposed|draft|triage|analysis needed"


def guess_kind(status):
    s = status.strip().lower()
    if re.search(DISCARD_WORDS, s):
        return "discarded"
    if re.search(BLOCK_WORDS, s):
        return "blocked"
    if re.search(WAIT_WORDS, s):
        return "wait"
    if re.search(DONE_WORDS, s):
        return "done"
    if re.search(BACKLOG_WORDS, s):
        return "backlog"
    return "active"


def suggest_map(items):
    """A first status map from the data. A person must review it before it is used.

    The order of the stages comes from the median position at which each status is first
    entered. Each raw status becomes its own stage. The person merges the statuses of different
    teams that mean the same thing.
    """
    counts = Counter()
    positions = defaultdict(list)
    for it in items:
        seen = []
        first = it["transitions"][0]["from"] if it["transitions"] else it.get("status")
        if first:
            seen.append(first)
        for tr in it["transitions"]:
            if tr["to"] not in seen:
                seen.append(tr["to"])
        if not it["transitions"] and it.get("status") and it["status"] not in seen:
            seen.append(it["status"])
        for i, st in enumerate(seen):
            if st is None:
                continue
            counts[st] += 1
            positions[st].append(i / max(1, len(seen) - 1))
    rank = {"backlog": 0, "wait": 1, "active": 1, "done": 2}
    stages, blocked, discarded = [], [], []
    for st in sorted(counts, key=lambda s: (rank.get(guess_kind(s), 1),
                                            percentile(positions[s], 50), -counts[s])):
        kind = guess_kind(st)
        if kind == "blocked":
            blocked.append(st)
        elif kind == "discarded":
            discarded.append(st)
        else:
            stages.append({"name": st, "kind": kind, "statuses": [st], "items": counts[st]})
    return {"stages": stages, "blocked": blocked, "discarded": discarded,
            "note": "Draft from flow_prepare.py --suggest-map. Merge the statuses that mean the same "
                    "stage, put the stages in the order of the value stream, and correct each kind "
                    "(backlog, wait, active, done). Remove the 'items' and 'note' keys if you want."}


# --------------------------------------------------------------------------- per-item timeline

def intervals(item, smap, as_of):
    """The stays of an item: [(stage, start, end, raw_status)], from creation to as_of."""
    trs = item["transitions"]
    created = item.get("created") or (trs[0]["at"] if trs else None)
    if created is None:
        return []
    out = []
    if trs:
        cur_raw, cur_start = trs[0]["from"], created
        for tr in trs:
            if tr["at"] > cur_start or out == []:
                out.append((smap.stage_of(cur_raw), cur_start, max(cur_start, tr["at"]), cur_raw))
            cur_raw, cur_start = tr["to"], tr["at"]
        out.append((smap.stage_of(cur_raw), cur_start, max(cur_start, as_of), cur_raw))
    else:
        raw = item.get("status")
        out.append((smap.stage_of(raw), created, max(created, as_of), raw))
    return out


def analyze_item(item, smap, as_of, workdays=False):
    """Facts about one item: the commitment time, the done time, the time in each stage, and rework."""
    ivs = intervals(item, smap, as_of)
    res = {
        "id": item.get("id"), "type": item.get("type"), "team": item.get("team"),
        "labels": item.get("labels", []), "created": item.get("created"),
        "committed": None, "done": None, "discarded": False,
        "stage_days": defaultdict(float), "active_days": 0.0, "wait_days": 0.0,
        "flow_days": None, "efficiency": None, "backward_moves": 0, "reopened": 0,
        "unmapped": Counter(), "current_stage": None, "visited": [],
        "raw": item,
    }
    if not ivs:
        return res
    last_order = None
    was_done = False
    for stage, start, end, raw in ivs:
        kind = smap.kind_of(stage)
        if stage not in res["visited"]:
            res["visited"].append(stage)
        if kind == "unmapped":
            res["unmapped"][raw] += 1
        if kind in ("wait", "active", "blocked", "done") and res["committed"] is None:
            res["committed"] = start
        if kind == "done":
            if res["done"] is None or not was_done:
                res["done"] = start
            was_done = True
        else:
            if was_done and kind != "discarded":
                res["reopened"] += 1
                res["done"] = None
            was_done = False
        order = smap.order_of(stage)
        if order is not None:
            if last_order is not None and order < last_order and kind != "backlog":
                res["backward_moves"] += 1
            last_order = order
        res["discarded"] = kind == "discarded"
    res["current_stage"] = ivs[-1][0]
    end_flow = res["done"] if res["done"] else as_of
    for stage, start, end, raw in ivs:
        if res["committed"] is None:
            break
        s, e = max(start, res["committed"]), min(end, end_flow)
        if e <= s:
            continue
        d = days_between(s, e, workdays)
        kind = smap.kind_of(stage)
        if kind in ("active", "wait", "blocked", "unmapped", "backlog"):
            res["stage_days"][stage] += d
        if kind == "active":
            res["active_days"] += d
        elif kind in ("wait", "blocked", "backlog"):
            res["wait_days"] += d
    if res["committed"] is not None and not res["discarded"]:
        res["flow_days"] = days_between(res["committed"], end_flow, workdays)
        if res["flow_days"] and res["flow_days"] > 0:
            res["efficiency"] = res["active_days"] / res["flow_days"]
    return res


def state_at(item, smap, t):
    """The stage of an item at time t. None before the item exists."""
    created = item.get("created") or (item["transitions"][0]["at"] if item["transitions"] else None)
    if created is None or t < created:
        return None
    trs = item["transitions"]
    if not trs:
        return smap.stage_of(item.get("status"))
    cur = trs[0]["from"]
    for tr in trs:
        if tr["at"] <= t:
            cur = tr["to"]
        else:
            break
    return smap.stage_of(cur)


def daterange(start_date, end_date):
    d = start_date
    while d <= end_date:
        yield d
        d += dt.timedelta(days=1)


def end_of_day(d):
    return dt.datetime.combine(d, dt.time(23, 59, 59), tzinfo=dt.timezone.utc)


def fmt(x, nd=1):
    if x is None:
        return "TBD"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)
