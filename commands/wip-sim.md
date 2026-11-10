---
description: Simulate WIP limits, people and batch sizes for a kanban system, and recommend a WIP limit
argument-hint: "[model.json or team] [question, for example: best WIP limit for Testing]"
---
Use the "Design kanban WIP limits" workflow of the scrum-master skill and `references/wip-simulation.md` for $ARGUMENTS. If there is no model, make one with `scripts/flow/flow_report.py --emit-model`. Ask me for the number of people in each active stage, the current WIP limits, and the rhythm of commitment and release, before you use the model. Start the baseline of `scripts/flow/wip_sim.py`, and correct the model if it does not match the history. Then answer the question with `--sweep`, `--set` or `--delta`. Give the recommended limit, the change in lead time and throughput, and the blocked time of the people before the constraint. Propose the limit as an experiment for two iterations, with an owner, a measure and a rule to stop. The team decides.
