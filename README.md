# AI · Agile · Jira

This repository is a working playbook for software delivery with AI assistants, two-week Agile
sprints and Jira. Its main rule is that the repository is the source of truth, and Jira follows
it.

The repository has three parts:

| Folder | What it is | Start with |
|---|---|---|
| [`example-project/`](example-project/) | A full Context Driven Development (CDD) setup for a fictional product. It holds the method, the sprint rhythm, a roadmap that is mirrored into Jira, an open-questions register, a decision log, an improvement register, a glossary, a spec area and the conventions file that an AI coding assistant reads. Copy it as a template. | [START_HERE.md](example-project/START_HERE.md) |
| [`tools/jira-dashboard/`](tools/jira-dashboard/) | A small Python tool. Each week, it gets epics and story points from Jira and freezes the week as a snapshot. Then it makes a self-contained HTML portfolio dashboard and a script for the executive briefing. It can operate offline on demo data. | [README.md](tools/jira-dashboard/README.md) |
| [`tools/ai-scrum-master/`](tools/ai-scrum-master/) | Five routines that an AI assistant runs for a team on a schedule: board hygiene, a Definition of Ready check, blocker aging, retrospective follow-up and the weekly dashboard. Each routine proposes, and a person approves. They run as Claude Code scheduled tasks, or as [Conductor](https://github.com/shannonbay/Conductor) goals with a level of autonomy for each kind of action. | [README.md](tools/ai-scrum-master/README.md) |

## The ideas in one minute

- The spec is the context. The project writes down what it knows (direction, open questions,
  decisions, vocabulary, rules) in the repository before anyone builds it. Only a reviewed
  pull request changes it. People and AI assistants work from the same context.
  → [context-driven-development.md](example-project/docs/context-driven-development.md)
- The roadmap leads, and Jira follows. The team writes stories in `PROJECT_ROADMAP.md` with
  stable ids, then mirrors them into Jira. Jira owns rank, points, sprint and assignee. The
  repository owns the text and the status of each story.
  → [PROJECT_ROADMAP.md#jira](example-project/PROJECT_ROADMAP.md#jira)
- A groomed story is a story whose context is written. The Definition of Ready reads like a
  CDD checklist. Engineering decides by consensus what goes into a sprint.
  → [agile-practices.md](example-project/docs/agile-practices.md)
- Report from Jira, and freeze every week. Progress is weighted by story points, with partial
  credit for work in progress. Each reporting week is locked, so the trend cannot change later.
  → [tools/jira-dashboard](tools/jira-dashboard/)
- Close the loop on retrospectives. Each improvement that the team tries is a `CI-NNN` item with
  an owner, an experiment and a measure. The next retrospective decides if it worked.
  → [continuous-improvement.md](example-project/docs/continuous-improvement.md)

## Try the dashboard

```bash
cd tools/jira-dashboard
python seed_demo_db.py
JIRA_DEMO=1 python weekly.py 2026-11-06
python -m http.server 8743   # → http://localhost:8743/automation_margin_tracker_dashboard.html
```

You need Python 3.9 or later, with the standard library only. A pre-built output is in
[`tools/jira-dashboard/samples/`](tools/jira-dashboard/samples/).

## Writing style

All documentation, READMEs and skills in this repository follow the Plain mode of the
[simple-english skill](.claude/skills/simple-english/SKILL.md). The rules of this skill come from
ASD-STE100 Simplified Technical English. If you write or change a document here, apply the skill
before you open the pull request. [CLAUDE.md](CLAUDE.md) gives the same rule to AI assistants.

## About the content

All products, companies, projects, objectives, people, Jira keys, dates and figures in this
repository are fictional. We replaced the names that belong to a real organization with
`[placeholder]`. We use real industry vocabulary as it is, for example the X12 healthcare
transactions in the example glossary.

## License

See [LICENSE](LICENSE).
