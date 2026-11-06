# AI · Agile · Jira

A **Scrum Master skill** for Claude, plus the playbook and tooling behind it. It helps a Scrum
Master run a team's backlog and sprints, and helps the Product Owner write epics and stories in
Jira that meet the **INVEST** criteria, each rated **Low**, **Good** or **TBD**. It also tracks
milestones and sprints and publishes a weekly status dashboard. Nothing is written to Jira
without your approval of a preview.

| Folder | What it is | Start with |
|---|---|---|
| [`skills/scrum-master/`](skills/scrum-master/) | The skill: workflows for refinement, story writing, sprint planning, retros, milestones and weekly status; the INVEST rubric and templates; an INVEST checker and sprint analytics scripts. | [SKILL.md](skills/scrum-master/SKILL.md) |
| [`commands/`](commands/) | Slash commands: `/refine`, `/new-story`, `/plan-sprint`, `/retro`, `/weekly-status`. | — |
| [`tools/jira-dashboard/`](tools/jira-dashboard/) | Weekly Jira pull, frozen weekly snapshots, the HTML status dashboard and an exec briefing. Runs offline on demo data. | [README.md](tools/jira-dashboard/README.md) |
| [`example-project/`](example-project/) | A complete Context Driven Development example for a fictional product: the method, sprint practices, a roadmap mirrored into Jira, open questions, decisions and a glossary. | [START_HERE.md](example-project/START_HERE.md) |

## Install

The repository is a Claude plugin (`.claude-plugin/plugin.json`).

- **Claude Code:** add this repository as a plugin, or copy `skills/scrum-master/` into your
  `~/.claude/skills/` folder.
- **Claude (desktop or web):** zip the repository and upload it as a plugin under Customize →
  Plugins, or zip `skills/scrum-master/` on its own and upload it as a skill.
- **Jira:** connect the Atlassian connector for reading and writing. Without it the skill reads
  through the REST scripts with an API token, or runs on demo data.

Rate the sample backlog to see the INVEST check:

```bash
python skills/scrum-master/scripts/invest_check.py skills/scrum-master/assets/sample_stories.json
python -m pytest -q tests      # the test suite
```

## The ideas in one minute

- **The spec is the context.** What the project knows (direction, open questions, decisions,
  vocabulary, rules) is written down in the repo *before* it is built, and changed only by
  reviewed pull request. People and AI assistants work from the same context.
  → [context-driven-development.md](example-project/docs/context-driven-development.md)
- **The roadmap leads; Jira follows.** Stories are written in `PROJECT_ROADMAP.md` with
  stable ids, then mirrored into Jira. Jira owns rank, points, sprint and assignee; the repo
  owns the story's text and status.
  → [PROJECT_ROADMAP.md#jira](example-project/PROJECT_ROADMAP.md#jira)
- **A refined story is one whose context is written.** The Definition of Ready reads like a
  CDD checklist, and Engineering decides what enters a sprint, by consensus.
  → [agile-practices.md](example-project/docs/agile-practices.md)
- **Report from Jira, freeze every week.** Progress is story-point-weighted with partial
  credit for work in flight, and each reporting week is locked so the trend can't drift.
  → [tools/jira-dashboard](tools/jira-dashboard/)

## Try the dashboard

```bash
cd tools/jira-dashboard
python seed_demo_db.py
JIRA_DEMO=1 python weekly.py 2026-11-06
python -m http.server 8743   # → http://localhost:8743/automation_margin_tracker_dashboard.html
```

Python 3.9+, standard library only. A pre-built output is in
[`tools/jira-dashboard/samples/`](tools/jira-dashboard/samples/).

## About the content

All products, companies, projects, objectives, people, Jira keys, dates and figures in this
repository are **fictional**. Organisation-specific names have been replaced with
`[placeholder]`. Real industry vocabulary (for example the X12 healthcare transactions in the
example glossary) is used as-is.

## License

See [LICENSE](LICENSE).
