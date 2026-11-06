"""Tests for skills/scrum-master/scripts/invest_check.py. Run: python -m pytest tests"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "scrum-master"
sys.path.insert(0, str(SKILL / "scripts"))

import invest_check as ic  # noqa: E402


def good_story(**over):
    s = {
        "key": "T-1",
        "summary": "Filter products by price",
        "description": "As a shopper I want to filter products by price so that I only see items I can afford.",
        "acceptance_criteria": [
            "Given a catalogue page, When I set a max price of 50, Then only items at or under 50 are shown",
            "Given a filter is set, When I clear it, Then all items are shown again",
        ],
        "story_points": 3,
    }
    s.update(over)
    return ic.normalise(s)


def ratings(story):
    r = ic.rate(story)
    return r["overall"], {c: v["rating"] for c, v in r["criteria"].items()}


def test_good_story_is_good_on_all_six():
    overall, per = ratings(good_story())
    assert overall == "Good"
    assert set(per.values()) == {"Good"}


def test_overall_rule_low_beats_tbd():
    assert ic.overall(["Good", "TBD", "Low"]) == "Low"
    assert ic.overall(["Good", "TBD"]) == "TBD"
    assert ic.overall(["Good"] * 6) == "Good"


def test_unestimated_story_is_tbd_not_low():
    overall, per = ratings(good_story(story_points=None))
    assert per["Estimable"] == "TBD" and per["Small"] == "TBD"
    assert overall == "TBD"


def test_over_eight_points_is_low_on_small():
    _, per = ratings(good_story(story_points=13))
    assert per["Small"] == "Low"


def test_unresolved_dependency_is_low_on_independent():
    _, per = ratings(good_story(depends_on=["T-0"]))
    assert per["Independent"] == "Low"


def test_prescriptive_text_is_low_on_negotiable():
    _, per = ratings(good_story(description=good_story()["description"] + " Must use the orders table."))
    assert per["Negotiable"] == "Low"


def test_missing_benefit_is_tbd_and_technical_task_is_low():
    _, per = ratings(good_story(description="As a shopper I want a price filter."))
    assert per["Valuable"] == "TBD"
    _, per = ratings(good_story(summary="Refactor price service", description="Refactor it."))
    assert per["Valuable"] == "Low"


def test_vague_criteria_are_low_but_measurable_ones_pass():
    _, per = ratings(good_story(acceptance_criteria=["The page is fast"]))
    assert per["Testable"] == "Low"
    _, per = ratings(good_story(acceptance_criteria=["The page is fast: loads in under 2 seconds", "Works offline"]))
    assert per["Testable"] == "Good"


def test_no_criteria_tbd_when_unrefined_low_when_estimated():
    _, per = ratings(good_story(acceptance_criteria=[], story_points=None))
    assert per["Testable"] == "TBD"
    _, per = ratings(good_story(acceptance_criteria=[]))
    assert per["Testable"] == "Low"


def test_jira_issue_shape_and_adf_description():
    issue = {
        "key": "T-9",
        "fields": {
            "summary": "Export report",
            "customfield_10016": 5,
            "labels": [],
            "description": {"type": "doc", "content": [
                {"type": "paragraph", "content": [{"type": "text", "text":
                    "As an analyst I want to export the report so that I can share it with finance."}]},
                {"type": "heading", "content": [{"type": "text", "text": "Acceptance criteria"}]},
                {"type": "bulletList", "content": [
                    {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text":
                        "Given a report, When I click export, Then a CSV downloads"}]}]},
                ]},
            ]},
            "issuelinks": [{"type": {"inward": "is blocked by"},
                            "inwardIssue": {"key": "T-8", "fields": {"status": {"statusCategory": {"key": "indeterminate"}}}}}],
        },
    }
    s = ic.normalise(issue)
    assert s["story_points"] == 5
    assert s["depends_on"] == ["T-8"]
    assert any("CSV" in a for a in s["acceptance_criteria"])
    _, per = ratings(s)
    assert per["Independent"] == "Low" and per["Valuable"] == "Good"


def test_cli_on_sample_file_reports_all_three_ratings():
    out = subprocess.run([sys.executable, str(SKILL / "scripts" / "invest_check.py"),
                          str(SKILL / "assets" / "sample_stories.json"), "--format", "json"],
                         capture_output=True, text=True, check=True).stdout
    overall = {r["key"]: r["overall"] for r in json.loads(out)}
    assert overall == {"HCA-141": "Good", "HCA-153": "Low", "HCA-143": "TBD", "HCA-181": "Low"}
