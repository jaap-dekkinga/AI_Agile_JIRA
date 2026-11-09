# AI · Agile · Jira

A working playbook for running software delivery with AI assistants, two-week Agile sprints
and Jira, where **the repository is the source of truth and Jira follows it**.

It has two parts:

| Folder | What it is | Start with |
|---|---|---|
| [`example-project/`](example-project/) | A complete **Context Driven Development (CDD)** setup for a fictional product: the method, the sprint rhythm, a roadmap mirrored into Jira, an open-questions register, a decision log, an improvement register, a glossary, a spec area and the conventions file an AI coding assistant reads. Copy it as a template. | [START_HERE.md](example-project/START_HERE.md) |
| [`tools/jira-dashboard/`](tools/jira-dashboard/) | A small Python tool that pulls epics and story points from Jira every week, freezes each week as a snapshot, and builds a self-contained HTML portfolio dashboard plus an executive briefing script. Runs offline on demo data. | [README.md](tools/jira-dashboard/README.md) |
| [`tools/ai-scrum-master/`](tools/ai-scrum-master/) | Five scheduled routines an AI assistant can run for a team: board hygiene, a Definition of Ready check, blocker ageing, retrospective follow-up and the weekly dashboard. Each one proposes and a person approves. They run as Claude Code scheduled tasks, or as [Conductor](https://github.com/shannonbay/Conductor) goals with per-action autonomy. | [README.md](tools/ai-scrum-master/README.md) |

## The ideas in one minute

- **The spec is the context.** What the project knows (direction, open questions, decisions,
  vocabulary, rules) is written down in the repo *before* it is built, and changed only by
  reviewed pull request. People and AI assistants work from the same context.
  → [context-driven-development.md](example-project/docs/context-driven-development.md)
- **The roadmap leads; Jira follows.** Stories are written in `PROJECT_ROADMAP.md` with
  stable ids, then mirrored into Jira. Jira owns rank, points, sprint and assignee; the repo
  owns the story's text and status.
  → [PROJECT_ROADMAP.md#jira](example-project/PROJECT_ROADMAP.md#jira)
- **A groomed story is one whose context is written.** The Definition of Ready reads like a
  CDD checklist, and Engineering decides what enters a sprint, by consensus.
  → [agile-practices.md](example-project/docs/agile-practices.md)
- **Report from Jira, freeze every week.** Progress is story-point-weighted with partial
  credit for work in flight, and each reporting week is locked so the trend can't drift.
  → [tools/jira-dashboard](tools/jira-dashboard/)
- **Close the loop on retrospectives.** Every improvement the team tries is a `CI-NNN` item with
  an owner, an experiment and a measure, and the next retrospective decides whether it worked.
  → [continuous-improvement.md](example-project/docs/continuous-improvement.md)

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
