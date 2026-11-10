# AI · Agile · Jira

This repository is a working playbook for software delivery with AI assistants, two-week Agile
sprints and Jira. Its main rule is that the repository is the source of truth, and Jira follows
it.

It is also a Claude plugin with a Scrum Master skill. The skill helps a Scrum Master to manage
the backlog and the sprints of a team. It helps the Product Owner to write epics and stories in
Jira, each with an INVEST score. It helps a SAFe Practice Consultant (SPC) or a Release Train
Engineer (RTE) to find the bottlenecks in an Agile Release Train (ART), with a draft value
stream map, the flow metrics, the patterns of a cumulative flow diagram and a simulation of WIP
limits. The team uses #NoEstimates, so the skill counts stories and does not use story points.
The skill writes nothing to Jira until you approve a preview.

The repository has these parts:

| Folder | What it is | Start with |
|---|---|---|
| [`skills/scrum-master/`](skills/scrum-master/) | The skill: workflows for refinement, stories, sprint planning, retrospectives, milestones, the weekly status and the flow of an ART. It has the INVEST rubric, story and epic templates, an INVEST checker, scripts for sprint analytics, and flow scripts for Jira and Azure DevOps. | [SKILL.md](skills/scrum-master/SKILL.md) |
| [`commands/`](commands/) | Slash commands: `/refine`, `/new-story`, `/plan-sprint`, `/retro`, `/weekly-status`, `/sm-report`, `/flow-report`, `/vsm-workshop`, `/wip-sim` and `/flow-coach`. | — |
| [`example-project/`](example-project/) | A full Context Driven Development (CDD) setup for a fictional product. It holds the method, the sprint rhythm, a roadmap that is mirrored into Jira, an open-questions register, a decision log, an improvement register, a glossary, a spec area and the conventions file that an AI coding assistant reads. Copy it as a template. | [START_HERE.md](example-project/START_HERE.md) |
| [`tools/jira-dashboard/`](tools/jira-dashboard/) | A small Python tool. Each week, it gets epics and their stories from Jira and freezes the week as a snapshot. Then it makes a self-contained HTML portfolio dashboard and a script for the executive briefing. It can operate offline on demo data. | [README.md](tools/jira-dashboard/README.md) |
| [`tools/ai-scrum-master/`](tools/ai-scrum-master/) | Four routines that an AI assistant operates for a team on a schedule: a weekly Scrum Master report (board hygiene, sprint burndown, metrics, improvements and blockers), a Definition of Ready check, retrospective follow-up and the weekly dashboard. Each routine reports or proposes, and a person approves. They operate as Claude Code scheduled tasks, or as [Conductor](https://github.com/shannonbay/Conductor) goals with a level of autonomy for each kind of action. | [README.md](tools/ai-scrum-master/README.md) |

## The ideas in one minute

- The spec is the context. The project writes down what it knows (direction, open questions,
  decisions, vocabulary, rules) in the repository before anyone builds it. Only a reviewed
  pull request changes it. People and AI assistants use the same context.
  → [context-driven-development.md](example-project/docs/context-driven-development.md)
- The roadmap leads, and Jira follows. The team writes stories in `PROJECT_ROADMAP.md` with
  stable ids, then mirrors them into Jira. Jira owns rank, sprint and assignee. The
  repository owns the text and the status of each story.
  → [PROJECT_ROADMAP.md#jira](example-project/PROJECT_ROADMAP.md#jira)
- A refined story meets the Definition of Ready: a clear title, explicit value for the user,
  detailed acceptance criteria, a size of one sprint or less, listed dependencies and no
  blockers. Engineering decides by consensus what a sprint includes.
  → [agile-practices.md](example-project/docs/agile-practices.md)
- Report from Jira, and freeze every week. Progress counts the Done stories, with partial credit
  for work in progress. The team uses #NoEstimates, so it does not use story points. Each
  reporting week is locked, so the trend cannot change later.
  → [tools/jira-dashboard](tools/jira-dashboard/)
- Close the loop on retrospectives. Each improvement that the team tries is a `CI-NNN` item with
  an owner, an experiment and a measure. The next retrospective decides if it was successful.
  At this time, the Scrum Master keeps the register in a local file. The repository gives its
  format.
  → [continuous-improvement.md](example-project/docs/continuous-improvement.md)

- Find the bottleneck with data, then decide in a workshop. The flow scripts read the status
  history of Jira or Azure DevOps. They make a draft value stream map, the six SAFe flow
  metrics and the patterns of the cumulative flow diagram. A Monte Carlo simulation tests a WIP
  limit before the ART uses it. The people in the workshop correct the map and choose the
  experiments.
  → [flow-metrics.md](skills/scrum-master/references/flow-metrics.md),
  [vsm-workshop.md](skills/scrum-master/references/vsm-workshop.md)

## Install

The repository is a Claude plugin (`.claude-plugin/plugin.json`).

- Claude Code: add this repository as a plugin. Or copy `skills/scrum-master/` into your
  `~/.claude/skills/` folder.
- Claude (desktop or web): make a zip file of the repository, and upload it as a plugin under
  Customize → Plugins. Or make a zip file of `skills/scrum-master/` alone, and upload it as a
  skill.
- Jira: connect the Atlassian connector, to read and to write. Without it, the skill reads
  through the REST scripts with an API token, or uses demo data.

To see the INVEST score of the sample backlog, and to start the tests:

```bash
python skills/scrum-master/scripts/invest_check.py skills/scrum-master/assets/sample_stories.json
python -m pytest -q tests      # the test suite
```

## Try the flow scripts

The sample data is a fictional ART with three teams and six months of history.

```bash
cd skills/scrum-master
python scripts/flow/flow_report.py assets/sample_flow_data.json assets/sample_status_map.json --workdays --segment label:dor-met
python scripts/flow/cfd.py assets/sample_flow_data.json assets/sample_status_map.json --svg cfd.svg
python scripts/flow/wip_sim.py assets/sample_flow_model.json --set Development=4 --sweep Testing=1:6
```

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

All documentation, READMEs and skills in this repository obey the Strict mode of the
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
