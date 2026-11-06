#!/usr/bin/env python3
"""Rate user stories against INVEST: Low / Good / TBD per criterion, plus an overall rating.

  python invest_check.py stories.json                 # text report
  python invest_check.py stories.json --format json   # machine-readable
  python invest_check.py stories.json --format jira   # per story: a Markdown INVEST table for the Jira description

Input is either a list of stories in the simple shape below, or a Jira search response
({"issues": [{"key", "fields": {...}}]}) as returned by /rest/api/3/search/jql or the
Atlassian MCP.

  {
    "key": "HCA-141",
    "summary": "Offer vendor test requests by name",
    "description": "As an operator I want ... so that ...",
    "acceptance_criteria": ["Given ... When ... Then ..."],   # list or text
    "story_points": 5,                                        # null = not estimated
    "depends_on": ["HCA-140"],                                # unresolved blockers
    "open_questions": ["Q-047"],                              # unanswered questions
    "labels": ["spike-needed"]
  }

The rules are heuristics: a FIRST PASS that a person (or the assistant) reviews. They never
invent certainty. When the text does not say enough to judge a criterion, the rating is TBD,
not Low, and the reason says what is missing. See ../references/invest-rubric.md.

Overall: Low if any criterion is Low; TBD if none is Low but any is TBD; Good only if all six
are Good. Standard library only.
"""
import argparse, json, re, sys

CRITERIA = ["Independent", "Negotiable", "Valuable", "Estimable", "Small", "Testable"]
FIBONACCI = {0, 0.5, 1, 2, 3, 5, 8, 13, 20, 21, 34, 40, 100}
MAX_POINTS = 8          # agile-practices.md: 8 is the most a single story may be

DEPENDENCY_WORDS = re.compile(
    r"\b(depends on|dependent on|blocked by|after (?:story|ticket|[A-Z]+-\d+)|"
    r"together with|at the same time as|requires [A-Z]+-\d+|once [A-Z]+-\d+ (?:is|has))\b", re.I)
PRESCRIPTIVE_WORDS = re.compile(
    r"\b(must use|implement(?:ed)? (?:using|with|in)|use (?:table|column|class|library|framework)|"
    r"add (?:a )?column|create (?:a )?table|stored procedure|refactor .* into|"
    r"select .* from|alter table)\b", re.I)
UNSETTLED_WORDS = re.compile(r"\b(tbd|to be (?:decided|discussed|confirmed)|unclear|not sure|\?\?)\b", re.I)
TECHNICAL_ONLY = re.compile(
    r"^(refactor|upgrade|migrate|bump|rename|clean ?up|restructure|configure|set ?up|install)\b", re.I)
VAGUE_WORDS = re.compile(
    r"\b(fast|quick(?:ly)?|user[- ]friendly|intuitive|works? (?:well|properly|correctly)|"
    r"easy to use|seamless(?:ly)?|robust|as expected|nice|better)\b", re.I)
HAS_NUMBER = re.compile(r"\d")
SO_THAT = re.compile(r"\bso that\b\s+(.+)", re.I | re.S)
PREVIOUS = re.compile(r"#*\s*INVEST:\s*(Good|TBD|Low)\b", re.I)
GWT = re.compile(r"\bgiven\b.+\bwhen\b.+\bthen\b", re.I | re.S)


# ---------------------------------------------------------------------------
# input normalisation

def adf_to_text(node):
    """Flatten Atlassian Document Format (Jira Cloud descriptions) to plain text."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "\n".join(adf_to_text(n) for n in node)
    if node.get("type") == "text":
        return node.get("text", "")
    sep = "\n" if node.get("type") in ("paragraph", "listItem", "heading", "doc", "bulletList",
                                       "orderedList", "codeBlock") else ""
    return sep.join(adf_to_text(c) for c in node.get("content", []))


def split_criteria(text):
    """Pull acceptance criteria out of a description: lines under an 'Acceptance criteria'
    heading, or any Given/When/Then lines."""
    if not text:
        return []
    lines = [l.strip(" -*\t") for l in text.splitlines()]
    out, inside = [], False
    for l in lines:
        if re.match(r"^#*\s*acceptance criteria\b", l, re.I):
            inside = True
            continue
        if inside and re.match(r"^#+\s|^[A-Z][A-Za-z ]+:$", l) and not l.lower().startswith(("given", "when", "then", "and")):
            inside = False
        if inside and l:
            out.append(l)
        elif not inside and re.match(r"^(given|when|then)\b", l, re.I):
            out.append(l)
    return out


def normalise(item, sp_field="customfield_10016"):
    """Accept a simple story dict or a Jira issue; return the simple shape."""
    if "fields" in item:
        f = item["fields"]
        desc = adf_to_text(f.get("description"))
        links = []
        for l in f.get("issuelinks") or []:
            inward = l.get("inwardIssue")
            ltype = (l.get("type") or {}).get("inward", "")
            if inward and "block" in ltype.lower():
                cat = (((inward.get("fields") or {}).get("status") or {}).get("statusCategory") or {}).get("key")
                if cat != "done":
                    links.append(inward.get("key"))
        return {
            "key": item.get("key"),
            "summary": f.get("summary", ""),
            "description": desc,
            "acceptance_criteria": split_criteria(desc),
            "story_points": f.get(sp_field, f.get("story_points")),
            "depends_on": links,
            "open_questions": [],
            "labels": f.get("labels") or [],
        }
    s = dict(item)
    ac = s.get("acceptance_criteria")
    if isinstance(ac, str):
        s["acceptance_criteria"] = [l.strip(" -*") for l in ac.splitlines() if l.strip(" -*")]
    elif ac is None:
        s["acceptance_criteria"] = split_criteria(s.get("description", ""))
    s.setdefault("depends_on", [])
    s.setdefault("open_questions", [])
    s.setdefault("labels", [])
    return s


# ---------------------------------------------------------------------------
# the six checks — each returns (rating, reason)

def check_independent(s, text):
    deps = [d for d in s.get("depends_on") or [] if d]
    if deps:
        return "Low", f"blocked by unresolved {', '.join(deps)}: split, reorder, or stub the dependency"
    m = DEPENDENCY_WORDS.search(text)
    if m:
        return "TBD", f"text mentions a dependency (\"{m.group(0)}\"): confirm it, or link it in Jira"
    return "Good", "no unresolved dependencies recorded"


def check_negotiable(s, text):
    m = PRESCRIPTIVE_WORDS.search(text)
    if m:
        return "Low", f"prescribes the implementation (\"{m.group(0)}\"): state the outcome, leave the how to the team"
    m = UNSETTLED_WORDS.search(text)
    if m:
        return "TBD", f"scope still open (\"{m.group(0)}\"): settle it with the PO in refinement"
    return "Good", "states the outcome without fixing the technical approach"


def check_valuable(s, text):
    m = SO_THAT.search(text)
    if m and len(m.group(1).split()) >= 3:
        return "Good", "\"so that\" names the benefit"
    if TECHNICAL_ONLY.match((s.get("summary") or "").strip()):
        return "Low", "technical task with no stated beneficiary: add who benefits and why, or fold it into a story that does"
    return "TBD", "no \"so that …\" benefit stated: the PO confirms who it is for and why"


def check_estimable(s, text):
    labels = {l.lower() for l in s.get("labels") or []}
    if labels & {"spike-needed", "needs-spike", "unestimable"}:
        return "Low", "marked as needing a spike before it can be estimated"
    if s.get("open_questions"):
        return "TBD", f"open questions {', '.join(s['open_questions'])}: record an assumption so the team can estimate"
    if s.get("story_points") in (None, ""):
        return "TBD", "not estimated yet: size it in refinement (planning poker)"
    return "Good", f"estimated at {s['story_points']} points"


def check_small(s, text):
    pts = s.get("story_points")
    if pts in (None, ""):
        return "TBD", "size unknown until it is estimated"
    try:
        pts = float(pts)
    except (TypeError, ValueError):
        return "TBD", f"story points not a number ({pts!r})"
    if pts > MAX_POINTS:
        return "Low", f"{pts:g} points is over the {MAX_POINTS}-point limit: split it (by workflow step, rule, or data variation)"
    note = "" if pts in FIBONACCI else f" (note: {pts:g} is not on the Fibonacci scale)"
    return "Good", f"{pts:g} points fits in one sprint{note}"


def check_testable(s, text):
    ac = [a for a in s.get("acceptance_criteria") or [] if a.strip()]
    if not ac:
        if s.get("story_points") in (None, ""):
            return "TBD", "acceptance criteria not written yet: add Given/When/Then statements in refinement"
        return "Low", "estimated but has no acceptance criteria: add Given/When/Then statements the team can verify"
    joined = " ".join(ac)
    vague = VAGUE_WORDS.search(joined)
    if vague and not HAS_NUMBER.search(joined):
        return "Low", f"criteria are vague (\"{vague.group(0)}\") with nothing measurable: add a threshold or an example"
    if GWT.search(joined) or len(ac) >= 2:
        return "Good", f"{len(ac)} acceptance {'criterion' if len(ac) == 1 else 'criteria'}" + (" in Given/When/Then form" if GWT.search(joined) else "")
    return "TBD", "only one loose criterion: the team confirms it is enough to verify the story"


CHECKS = [check_independent, check_negotiable, check_valuable,
          check_estimable, check_small, check_testable]


def overall(ratings):
    if "Low" in ratings:
        return "Low"
    if "TBD" in ratings:
        return "TBD"
    return "Good"


def strip_invest_section(desc):
    """The description minus an earlier INVEST table, so old ratings don't sway the new check."""
    m = PREVIOUS.search(desc or "")
    return (desc or "")[:m.start()] if m else (desc or "")


def rate(story):
    text = " ".join([story.get("summary") or "", strip_invest_section(story.get("description"))])
    results = {}
    for name, fn in zip(CRITERIA, CHECKS):
        r, why = fn(story, text)
        results[name] = {"rating": r, "reason": why}
    o = overall([v["rating"] for v in results.values()])
    prev = PREVIOUS.search(story.get("description") or "")
    return {"key": story.get("key"), "summary": story.get("summary"), "overall": o,
            "previous": prev.group(1).title().replace("Tbd", "TBD") if prev else None,
            "criteria": results}


# ---------------------------------------------------------------------------
# output

def jira_section(r):
    """Markdown section for the issue description or a comment. The Atlassian MCP converts
    Markdown to Jira's document format; for the REST API, convert it to ADF first."""
    lines = [f"### INVEST: {r['overall']}", "", "| Criterion | Rating | Why |", "|---|---|---|"]
    for c in CRITERIA:
        v = r["criteria"][c]
        lines.append(f"| {c} | {v['rating']} | {v['reason'].replace('|', '/')} |")
    return "\n".join(lines)


def text_report(results):
    out = []
    counts = {k: sum(1 for r in results if r["overall"] == k) for k in ("Good", "TBD", "Low")}
    out.append(f"INVEST check: {len(results)} stories · {counts['Good']} Good · {counts['TBD']} TBD · {counts['Low']} Low\n")
    for r in results:
        was = f"  (was {r['previous']})" if r["previous"] and r["previous"] != r["overall"] else ""
        out.append(f"{r['key'] or '(no key)'}  {r['summary']}\n  overall: {r['overall']}{was}")
        for c in CRITERIA:
            v = r["criteria"][c]
            mark = {"Good": "+", "TBD": "?", "Low": "!"}[v["rating"]]
            out.append(f"   {mark} {c:<12}{v['rating']:<5} {v['reason']}")
        out.append("")
    return "\n".join(out)


def load(path):
    data = json.load(open(path, encoding="utf-8")) if path != "-" else json.load(sys.stdin)
    if isinstance(data, dict) and "issues" in data:
        data = data["issues"]
    elif isinstance(data, dict) and "stories" in data:
        data = data["stories"]
    if not isinstance(data, list):
        sys.exit("expected a list of stories, {\"stories\": [...]}, or a Jira search response {\"issues\": [...]}")
    return data


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("path", help="stories JSON file, or - for stdin")
    ap.add_argument("--format", choices=["text", "json", "jira"], default="text")
    ap.add_argument("--sp-field", default="customfield_10016",
                    help="Jira story-point field id, for Jira-shaped input")
    a = ap.parse_args(argv)
    results = [rate(normalise(s, a.sp_field)) for s in load(a.path)]
    if a.format == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
    elif a.format == "jira":
        for r in results:
            print(f"== {r['key']}\n{jira_section(r)}\n")
    else:
        print(text_report(results))


if __name__ == "__main__":
    main()
