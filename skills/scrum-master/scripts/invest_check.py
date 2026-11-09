#!/usr/bin/env python3
"""Score user stories against INVEST: Good / TBD / Low for each criterion, and a score out of 6.

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
    "depends_on": ["HCA-140"],                                # unresolved blockers
    "open_questions": ["Q-047"],                              # unanswered questions
    "labels": ["spike-needed"]                               # or "too-big"
  }

The team uses #NoEstimates, so the script does not use story points. A "story_points" field in
the input is ignored.

The rules are heuristics: a first pass that a person (or the assistant) reviews. They do not
make up certainty. When the text does not give enough to judge a criterion, the rating is TBD,
not Low, and the reason says what is missing. See ../references/invest-rubric.md.

The score is the number of criteria rated Good, out of 6. It is a tool for refinement. No score
and no rating stops a story. Standard library only.
"""
import argparse, json, re, sys

CRITERIA = ["Independent", "Negotiable", "Valuable", "Estimable", "Small", "Testable"]
MAX_CRITERIA = 6        # more acceptance criteria than this: ask if the story fits in one sprint
SPIKE_LABELS = {"spike-needed", "needs-spike", "unestimable"}
TOO_BIG_LABELS = {"too-big", "needs-split", "split-needed", "epic-sized"}

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
PREVIOUS = re.compile(r"#*\s*INVEST(?: score)?:\s*(\d/6|Good|TBD|Low)\b", re.I)
GWT = re.compile(r"\bgiven\b.+\bwhen\b.+\bthen\b", re.I | re.S)
SPANS_SPRINTS = re.compile(r"\b(several|multiple|two|three|more than one) sprints\b|\bacross sprints\b", re.I)


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


def normalise(item):
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


def criteria_of(s):
    return [a for a in s.get("acceptance_criteria") or [] if a.strip()]


def check_estimable(s, text):
    """#NoEstimates: estimable means that the team understands the work well enough to judge
    if it fits in one sprint. No story points."""
    labels = {l.lower() for l in s.get("labels") or []}
    if labels & SPIKE_LABELS:
        return "Low", "marked as needing a spike before the team can judge the work"
    if s.get("open_questions"):
        return "TBD", f"open questions {', '.join(s['open_questions'])}: record an assumption so the team can judge the work"
    if not criteria_of(s):
        return "TBD", "no acceptance criteria yet: the team cannot judge the work until they are written"
    return "Good", "the acceptance criteria tell the team what to build"


def check_small(s, text):
    """#NoEstimates: small means that the team can complete the story in one sprint."""
    labels = {l.lower() for l in s.get("labels") or []}
    if labels & TOO_BIG_LABELS:
        return "Low", "marked as too large for one sprint: split it (by workflow step, rule, or data variation)"
    m = SPANS_SPRINTS.search(text)
    if m:
        return "Low", f"the text says that the work spans sprints (\"{m.group(0)}\"): split it"
    ac = criteria_of(s)
    if not ac:
        return "TBD", "size unknown until the acceptance criteria are written"
    if len(ac) > MAX_CRITERIA:
        return "TBD", f"{len(ac)} acceptance criteria: the team confirms that it fits in one sprint, or splits it"
    return "Good", f"{len(ac)} acceptance {'criterion' if len(ac) == 1 else 'criteria'}: likely fits in one sprint; the team confirms in refinement"


def check_testable(s, text):
    ac = criteria_of(s)
    if not ac:
        return "TBD", "acceptance criteria not written yet: add Given/When/Then statements in refinement"
    joined = " ".join(ac)
    vague = VAGUE_WORDS.search(joined)
    if vague and not HAS_NUMBER.search(joined):
        return "Low", f"criteria are vague (\"{vague.group(0)}\") with nothing measurable: add a threshold or an example"
    if GWT.search(joined) or len(ac) >= 2:
        return "Good", f"{len(ac)} acceptance {'criterion' if len(ac) == 1 else 'criteria'}" + (" in Given/When/Then form" if GWT.search(joined) else "")
    return "TBD", "only one loose criterion: the team confirms it is enough to verify the story"


CHECKS = [check_independent, check_negotiable, check_valuable,
          check_estimable, check_small, check_testable]


def score(ratings):
    """The number of criteria rated Good, as "N/6". A tool for refinement, not a pass or a fail."""
    return f"{sum(1 for r in ratings if r == 'Good')}/{len(CRITERIA)}"


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
    sc = score([v["rating"] for v in results.values()])
    prev = PREVIOUS.search(story.get("description") or "")
    return {"key": story.get("key"), "summary": story.get("summary"), "score": sc,
            "previous": prev.group(1).title().replace("Tbd", "TBD") if prev else None,
            "criteria": results}


# ---------------------------------------------------------------------------
# output

def jira_section(r):
    """Markdown section for the issue description or a comment. The Atlassian MCP converts
    Markdown to Jira's document format; for the REST API, convert it to ADF first."""
    lines = [f"### INVEST score: {r['score']}", "", "| Criterion | Rating | Why |", "|---|---|---|"]
    for c in CRITERIA:
        v = r["criteria"][c]
        lines.append(f"| {c} | {v['rating']} | {v['reason'].replace('|', '/')} |")
    return "\n".join(lines)


def text_report(results):
    out = []
    out.append(f"INVEST scores: {len(results)} stories (the number of Good criteria, out of 6)\n")
    for r in results:
        was = f"  (was {r['previous']})" if r["previous"] and r["previous"] != r["score"] else ""
        out.append(f"{r['key'] or '(no key)'}  {r['summary']}\n  score: {r['score']}{was}")
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
    a = ap.parse_args(argv)
    results = [rate(normalise(s)) for s in load(a.path)]
    if a.format == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
    elif a.format == "jira":
        for r in results:
            print(f"== {r['key']}\n{jira_section(r)}\n")
    else:
        print(text_report(results))


if __name__ == "__main__":
    main()
