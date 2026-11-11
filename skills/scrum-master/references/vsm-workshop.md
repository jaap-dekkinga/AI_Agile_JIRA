# A value stream mapping workshop with a draft from data

A value stream map (VSM) shows the steps from a request to the delivery of value, and the time
in each step. This page gives a workshop of four hours for an Agile Release Train (ART). The
workshop does not start with a blank whiteboard. It starts with a draft map from the board data,
and the people correct it.

The AI writes the draft and the what-if results. The people in the room correct the map, find
the causes and choose the experiments.

## Who attends

| Role | Why |
|---|---|
| Release Train Engineer (RTE) | Owns the flow of the ART and the follow-up |
| SAFe Practice Consultant (SPC) or Agile coach | Facilitates |
| Product Management | Knows where requests start and what value means |
| One or two people from each team, with the testers | Know what really happens at each step |
| System Architect, operations, release management | Know the steps outside the team boards |
| A Business Owner, for the first and last part | Agrees on the trigger, the value and the goal |

Keep the group at 15 people or fewer.

## Before the workshop (one week before)

1. Get six months of status history, and make it anonymous (`references/flow-metrics.md`).
2. Review the status map with the RTE. Agree on the commitment point and the done stage.
3. Start the report and the CFD:

   ```bash
   python scripts/flow/flow_report.py flow-data/flow.json flow-data/map.json \
     --workdays --segment label:dor-met --emit-model flow-data/model.json -o flow-data/vsm-draft.md
   python scripts/flow/cfd.py flow-data/flow.json flow-data/map.json --svg flow-data/cfd.svg
   ```

4. Start `flow_report.py` with `--team` for each team. A queue in one team can disappear in the
   numbers of the full ART.
5. Choose three items to follow from start to end: a fast item, a typical item (near p50) and a
   slow item (near p85 or more). Get their keys from the person who has the raw export.
6. Write the problem statement with the RTE in one sentence, for example: "Features take 14
   weeks from commitment to release, and the business needs 6."
7. Send the draft map and the questions of the report to the attendees. Ask each team to mark
   what is wrong.

Do not send the raw export. Send the report, which has no summaries and no names of people.

## Agenda (four hours)

| Time | Part | What happens |
|---|---|---|
| 15 min | Frame | The Business Owner gives the problem statement, the trigger and the value. Agree on the start and the end of the map. |
| 45 min | Walk the draft map | Go through each stage of the draft from left to right. The people who do the work say if it is correct. Add the steps that are not on the board, for example approvals, test environments, security reviews and other trains. Mark each number that the room does not believe. |
| 30 min | Follow three items | Follow the three items from start to end. Write the time in each step and each wait. Compare them with the draft. |
| 15 min | Break | |
| 30 min | Find the constraint | Look at the largest queues, the constraint of the report and the CFD patterns (`references/cfd-patterns.md`). For the largest wait, ask "why" five times. |
| 45 min | Future-state map | Draw the map that the ART wants in two Program Increments (PIs). Use the eight flow accelerators in the next table to find changes. |
| 30 min | Experiments | Choose three experiments or fewer. Write each one as an improvement item, with an owner, the change, the measure and the date of the review. For a WIP limit, start `wip_sim.py` in the room. |
| 15 min | Close | Agree on the measures to show each iteration, and the date of the next review. |

## From a finding to a flow accelerator

SAFe gives eight flow accelerators. The table connects each one to the signal in the data that
points to it.

| Flow accelerator | The signal in the data |
|---|---|
| Visualize and limit WIP | The flow load grows. The CFD lines diverge. The flow time grows. |
| Address bottlenecks | A queue between two work stages bulges. The constraint of the report. |
| Minimize handoffs and dependencies | Many wait stages. Items wait for another team. Low flow efficiency. |
| Get faster feedback | High rework: items go back from test to development. |
| Work in smaller batches | Stair-steps in the CFD. A long p85 compared with the p50. |
| Reduce queue length | A large start queue. A backlog that grows. |
| Optimize time "in the zone" | Low flow efficiency in active stages. Many items in work for each person. |
| Remediate legacy policies and practices | Release queues and approval steps that wait for a fixed date or a meeting. |

## What the AI does in the room

- It updates the status map when the room corrects a stage, and starts the report again.
- It answers what-if questions with `wip_sim.py` (`references/wip-simulation.md`).
- It writes the experiments as improvement items, in the format of the register.
- It writes the notes of the workshop.

The AI does not decide. It writes "TBD" when the data cannot answer a question, and it names the
person who can.

## When the teams resist WIP limits

Many teams think that a WIP limit makes them slower. Use these steps:

1. Use the data of the team, not an example from a book.
2. Let the team start the simulation. Ask them to choose the WIP limits, and to compare the
   result with the baseline.
3. Show the table of busy, blocked and starved time. A queue grows fast when the constraint is
   busy for more than about 80% of the time.
4. Make the WIP limit an experiment for two iterations, with a measure and a rule to stop it.
   The team can stop the experiment if the throughput falls by more than the agreed value.
5. Tell people what to do when the limit stops them: help the constraint, pair, review, or write
   tests. Then a WIP limit does not leave people idle.
6. Measure the system, not people. Never show a utilization for each person.

`references/flow-coach.md` gives short answers to the usual objections.

## After the workshop

1. Write the corrected map back into the status map, and keep it with the flow data.
2. Put the experiments into the improvement register (`docs/continuous-improvement.local.md`). An
   experiment that needs work becomes a story on the backlog.
3. Start the report again each iteration, and compare it with the baseline of the workshop.
4. Bring the results to the Inspect and Adapt (I&A) problem-solving workshop at the end of the PI.
