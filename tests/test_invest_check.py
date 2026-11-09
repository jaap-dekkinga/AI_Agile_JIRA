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
    }
    s.update(over)
    return ic.normalise(s)


def ratings(story):
    r = ic.rate(story)
    return r["score"], {c: v["rating"] for c, v in r["criteria"].items()}


def test_good_story_is_good_on_all_six():
    score, per = ratings(good_story())
    assert score == "6/6"
    assert set(per.values()) == {"Good"}


def test_score_counts_good_criteria_and_has_no_failing_grade():
    assert ic.score(["Good", "TBD", "Low", "Good", "Good", "Good"]) == "4/6"
    assert ic.score(["Low"] * 6) == "0/6"
    assert not hasattr(ic, "overall")


def test_story_points_are_ignored():
    assert ratings(good_story(story_points=13)) == ratings(good_story(story_points=None))


def test_too_big_label_or_sprint_spanning_text_is_low_on_small():
    _, per = ratings(good_story(labels=["too-big"]))
    assert per["Small"] == "Low"
    _, per = ratings(good_story(description=good_story()["description"] + " This takes several sprints."))
    assert per["Small"] == "Low"


def test_many_criteria_is_tbd_on_small():
    many = [f"Given case {i}, When I filter, Then result {i} shows" for i in range(7)]
    _, per = ratings(good_story(acceptance_criteria=many))
    assert per["Small"] == "TBD"


def test_spike_label_is_low_and_open_question_is_tbd_on_estimable():
    _, per = ratings(good_story(labels=["spike-needed"]))
    assert per["Estimable"] == "Low"
    _, per = ratings(good_story(open_questions=["Q-047"]))
    assert per["Estimable"] == "TBD"


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


def test_no_criteria_is_tbd_on_estimable_small_and_testable():
    _, per = ratings(good_story(acceptance_criteria=[]))
    assert per["Testable"] == "TBD" and per["Small"] == "TBD" and per["Estimable"] == "TBD"


def test_jira_issue_shape_and_adf_description():
    issue = {
        "key": "T-9",
        "fields": {
            "summary": "Export report",
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
    assert "story_points" not in s
    assert s["depends_on"] == ["T-8"]
    assert any("CSV" in a for a in s["acceptance_criteria"])
    _, per = ratings(s)
    assert per["Independent"] == "Low" and per["Valuable"] == "Good"


def test_cli_on_sample_file_gives_a_score_for_each_story():
    out = subprocess.run([sys.executable, str(SKILL / "scripts" / "invest_check.py"),
                          str(SKILL / "assets" / "sample_stories.json"), "--format", "json"],
                         capture_output=True, text=True, check=True).stdout
    scores = {r["key"]: r["score"] for r in json.loads(out)}
    assert scores == {"HCA-141": "6/6", "HCA-153": "1/6", "HCA-143": "2/6", "HCA-181": "5/6"}


def test_previous_table_is_read_back_but_does_not_sway_the_check():
    desc = good_story()["description"] + "\n\n### INVEST score: 5/6\n\n| Criterion | Rating | Why |\n|---|---|---|\n| Negotiable | TBD | scope TBD |"
    r = ic.rate(good_story(description=desc))
    assert r["previous"] == "5/6"
    assert r["score"] == "6/6"             # the old table's "TBD" text is not re-read as open scope
    legacy = good_story()["description"] + "\n\n### INVEST: TBD\n"
    assert ic.rate(good_story(description=legacy))["previous"] == "TBD"
    assert "label" not in r
