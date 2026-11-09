"""End-to-end tests for tools/jira-dashboard on the offline demo. Run: python -m pytest tests"""
import os
import pathlib
import shutil
import sqlite3
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DASH = ROOT / "tools" / "jira-dashboard"
ANALYTICS = ROOT / "skills" / "scrum-master" / "scripts" / "analytics"
SPRINTS = ROOT / "skills" / "scrum-master" / "assets" / "sample_sprint_data.json"


@pytest.fixture()
def work(tmp_path):
    d = tmp_path / "dash"
    shutil.copytree(DASH, d, ignore=shutil.ignore_patterns("tracker.db*", "__pycache__", "samples"))
    run(d, "seed_demo_db.py")
    return d


def run(cwd, *args, demo=True):
    env = dict(os.environ, JIRA_DEMO="1" if demo else "")
    return subprocess.run([sys.executable, *args], cwd=cwd, env=env,
                          capture_output=True, text=True, check=True).stdout


def test_weekly_job_adds_one_locked_week_and_keeps_history(work):
    con = sqlite3.connect(work / "tracker.db")
    before = con.execute("SELECT week, pct FROM project_week ORDER BY project_id, week").fetchall()
    con.close()
    run(work, "weekly.py", "2026-11-06")
    con = sqlite3.connect(work / "tracker.db")
    weeks = con.execute("SELECT week, state FROM weeks ORDER BY seq").fetchall()
    after = con.execute("SELECT week, pct FROM project_week WHERE week < '2026-11-06' "
                        "ORDER BY project_id, week").fetchall()
    con.close()
    assert weeks[-1] == ("2026-11-06", "locked")
    assert after == before            # locked history untouched
    assert (work / "automation_margin_tracker_dashboard.html").exists()
    assert (work / "exec-talk-script.md").exists()


def test_backups_have_distinct_timestamped_names(work):
    run(work, "weekly.py", "2026-11-06")
    baks = list(work.glob("tracker.db.bak-*"))
    assert baks and all("-0000-" not in b.name for b in baks)


def test_text_from_jira_cannot_inject_markup(work):
    con = sqlite3.connect(work / "tracker.db")
    con.execute("UPDATE epics SET name='</script><img src=x onerror=alert(1)>' WHERE id=1")
    con.execute("UPDATE projects SET name='R&D <b>Lab</b>' WHERE id=1")
    con.commit(); con.close()
    run(work, "build_dashboard.py")
    html = (work / "automation_margin_tracker_dashboard.html").read_text(encoding="utf-8")
    data = html.split("const DATA = ", 1)[1].split("</script>", 1)[0]
    assert "<img" not in data and "</script" not in data
    assert "<b>Lab</b>" not in html


@pytest.mark.parametrize("script", ["velocity_analyzer.py", "sprint_health_scorer.py",
                                    "retrospective_analyzer.py"])
def test_sprint_analytics_run_on_sample_data(script):
    out = subprocess.run([sys.executable, str(ANALYTICS / script), str(SPRINTS), "--format", "text"],
                         capture_output=True, text=True, check=True).stdout
    assert "REPORT" in out
