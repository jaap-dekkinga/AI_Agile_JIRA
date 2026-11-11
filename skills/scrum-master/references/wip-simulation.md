# Kanban design and WIP simulation

A WIP limit is the largest number of items that a stage can hold at the same time. A good limit
cuts the flow time and keeps the throughput. `scripts/flow/wip_sim.py` does a Monte Carlo
simulation of the kanban system, so the ART can test a limit before it uses it. A Monte Carlo
simulation operates the same model many times with random samples from the history, and reports
the range of the results.

## 1. Make the model

`flow_report.py --emit-model model.json` writes a first model from the flow data. Then correct
these values with the team:

| Field | What to write |
|---|---|
| `stages[].workers` | The number of people who do the work of this stage. The first value is an estimate from the data. Replace it. |
| `stages[].wip_limit` | The current limit, or `null` for no limit. |
| `arrivals_per_week` | The items that the team commits each week. The first value comes from the history. Use `null` for "always work to pull" to find the capacity. |
| `commit_every_days` | 10 if the team commits at sprint planning every two weeks. `null` if the team commits each day. |
| `release_every_days` | 10 if the team releases at the end of each iteration. `null` for a release on demand. |
| `swarm_efficiency` | 0 if people help only in their own stage. 0.5 if a developer can test at half the speed of a tester. |

Make one model for each team. A model for the full ART adds the testers of all teams together,
and can hide the queue of one team.

The service time of each stage is a sample of the times in the history. It is the time in the
status, so it includes the normal interruptions of the team.

`assets/sample_flow_model.json` is a fictional model for one team, with 3 developers and 1
tester.

## 2. Make sure that the model matches the history

Start the baseline:

```bash
python scripts/flow/wip_sim.py flow-data/model.json
```

The output compares the simulation with the history. If the throughput differs by more than
25%, correct the workers, the arrivals and the batches first. Do not use a what-if result from a
model that does not match.

If the output says that the commitment queue grows, the team commits more items than it can
finish. WIP limits cannot correct this. Commit less, or add capacity at the constraint.

## 3. Ask the what-if questions

| Question | Command |
|---|---|
| What is the best WIP limit for Testing? | `--sweep Testing=1:8` |
| What if the limit of Testing is 2 lower? | `--delta Testing=-2` |
| What if Development has a limit of 4? | `--set Development=4` |
| What if developers help with tests? | `--set swarm_efficiency=0.5` |
| What if we release on demand? | `--set release_every_days=none` |
| What if we commit each day, not at planning? | `--set commit_every_days=none` |
| What if we add a tester? | `--set Testing.workers=2` |
| What is the capacity of the system? | `--set arrivals_per_week=unlimited` |

You can combine settings: `--set Development=4 --set swarm_efficiency=0.5 --sweep Testing=1:6`.

## 4. Read the result

The table gives, for each scenario:

- Items each week: the mean, and the range from p10 to p90 of the repetitions.
- Lead time p50 and p85, in working days, from commitment to Done.
- Average WIP.
- For each stage, the share of the time of its people that is busy, blocked or starved. Blocked
  means that the people finished work, but a WIP limit stopped it. Starved means that no work
  waited for them.

A sweep recommends the lowest limit that keeps the throughput within 5% of the best value. The
limit must also keep the people of the earlier stages blocked for 15% of the time or less. Use `--tolerance` and
`--max-blocked` to change these values.

## 5. Rules for a WIP limit

- A limit on one stage alone moves the queue into the earlier stage. Limit the stage before the
  constraint too, or limit the full system.
- The constraint must not wait. Put a small queue before it, and limit the stages before it.
- When the limit stops people, they help the constraint. Agree before the experiment what each
  role can do.
- Batches can hide the effect of a limit. A commitment or a release every two weeks adds up to
  two weeks to each item.
- Start with the recommended limit for two iterations. Measure the flow time, the throughput and
  the blocked time. Then keep, change or stop the limit.

## Example: one team, 3 developers and 1 tester

The sample model (`assets/sample_flow_model.json`) commits each two weeks and releases each two
weeks. These are the steps for the question "What WIP limit for Testing keeps the flow without
idle developers?":

1. `wip_sim.py assets/sample_flow_model.json`: the baseline matches the history (3.2 items each
   week in the simulation against 2.8 in the history). The tester is busy for 95% of the time.
   The team commits a little more than it can finish.
2. `--sweep Testing=1:6`: a limit on Testing alone changes nothing, because Development has no
   limit. The output says so.
3. `--set Development=4 --sweep Testing=1:6`: the recommended limit for Testing is 4. Developers
   are blocked for 13% of the time.
4. `--set Development=4 --set Testing=4 --set swarm_efficiency=0.5 --set commit_every_days=none
   --set release_every_days=none`: developers help with tests, the team commits each day, and it
   releases on demand. The lead time at p85 falls from 30 to 14 working days. The throughput goes
   up by 7%, to 3.4 items each week, near the 3.5 items that the team commits.

The ART can discuss a change with data: smaller batches, a limit on development, and
developers who help with tests.
