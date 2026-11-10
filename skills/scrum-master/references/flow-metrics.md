# Flow data and the flow metrics

This page tells you how to get flow data from Jira or Azure DevOps, how to clean it, and what
each flow metric means. The scripts are in `scripts/flow/`. They use the Python standard library
only.

## The pipeline

1. Get the status history of the items (Jira or Azure DevOps).
2. Make it flow data with `flow_prepare.py`, and make it anonymous.
3. Write the status map, which tells the scripts what each status means.
4. Start `flow_report.py` for the draft value stream map (VSM) and the metrics.
5. Start `cfd.py` for the cumulative flow diagram (CFD) and its patterns.
6. Start `wip_sim.py` for the what-if questions about WIP limits.

Keep raw exports in a `flow-data/` folder. Git ignores this folder. A raw export has summaries
and names of people. Do not share it, and do not paste it into a chat.

## 1. Get the status history

The flow metrics need the time of each status change. A list of the current statuses is not
sufficient.

| Source | How to get the history |
|---|---|
| Jira, REST | `python scripts/flow/pull_jira_flow.py "<JQL>" -o flow-data/jira.json`. It uses the `JIRA_*` credentials of `references/jira-access.md`. It only reads. It gets the full changelog of each item. |
| Jira, Atlassian MCP | Search with the JQL, and get each item with its changelog. Save the result as `{"issues": [...]}` in `flow-data/`. If the changelog of an item has more entries than the result, use the REST script. |
| Azure DevOps, REST | Get the updates of each work item (`_apis/wit/workitems/{id}/updates`). Save a list of `{"id": 12, "updates": [...]}`. |
| Azure DevOps, Analytics | Export the `WorkItemRevisions` view to a CSV file, with the columns `WorkItemId`, `WorkItemType`, `AreaPath`, `State` and `ChangedDate`. |
| Other tools | Write a CSV file with one row for each status change: `id`, `type`, `team`, `created`, `from`, `to`, `at`. |

A good JQL for an ART is `project in (A, B, C) AND issuetype in (Story, Bug, Enabler) AND
updated >= -26w`. Six months (26 weeks) of history gives a stable picture. Use the same item
types for the full ART.

For a demo, use `JIRA_DEMO=1`, or the sample files in `assets/`.

## 2. Make flow data, and make it anonymous

```bash
python scripts/flow/flow_prepare.py jira flow-data/jira.json -o flow-data/flow.json \
  --anonymize --keep-labels dor-met --suggest-map flow-data/map.json
```

With `--anonymize`, the script replaces each item key with a hash, and each team with
"Team 1", "Team 2" and so on. It removes the summaries, the names of people and all labels
except the labels that you name. The salt of the hash is random, and the script does not write
it. Thus nobody can find the original keys from the file.

Use `--anonymize` before you give flow data to an AI tool outside your organization. The
anonymous file keeps the item types, the statuses, the teams (as numbers) and the times. These
are sufficient for all the flow scripts.

## 3. Write the status map

Each team names its statuses in a different way. The status map puts all of them into one value
stream. `--suggest-map` writes a first map from the data, and prints each status with its count
and a guessed kind. Then do these steps with the Scrum Master or the Release Train Engineer (RTE):

1. Merge the statuses that are the same stage, for example "Ready for QA" and "Dev Complete".
2. Put the stages in the order of the value stream.
3. Give each stage its kind: `backlog`, `wait`, `active` or `done`.
4. Put the blocked statuses in the `blocked` list, and the statuses for discarded work in the
   `discarded` list.
5. Start `flow_report.py`. If its data quality section lists unmapped statuses, add them to the
   map.

`assets/sample_status_map.json` is an example for three teams.

| Kind | Meaning | In the flow time |
|---|---|---|
| `backlog` | Before the commitment point. Nobody promised to deliver the item. | No |
| `wait` | A queue or a handoff. The item waits for the next person or step. | Yes, as wait time |
| `active` | Somebody works on the item. | Yes, as active time |
| `done` | Delivered. The flow time stops at the last entry into a done stage. | No |
| `blocked` (list) | A blocker stops the item. | Yes, as wait time |
| `discarded` (list) | The item left without delivery. | The item is not counted |

The commitment point is the first stage after the backlog. Name it clearly with the ART. A
status such as "Selected for Development" is often the commitment point.

## 4. Clean the data

`flow_report.py` writes a data quality section. It removes these items from the metrics and
reports them:

- Bulk moves: eight or more items that changed status in the same minute. A board clean-up
  causes this. Use `--bulk N` to change the number, or `--keep-bulk` to keep the items.
- Items that went from the backlog to Done with no work stage. The team closed them, but did not
  deliver them through the flow.
- Discarded items.

It also reports the statuses that are not in the map, and the items that were reopened after
Done. It reports the items in progress without a status change for more than 60 days. Show these to the teams. They
are signs that the board does not match the real work.

## 5. The six flow metrics

SAFe uses six flow metrics. The scripts count items, not story points, so the metrics agree
with #NoEstimates.

| Metric | The script calculates | Notes |
|---|---|---|
| Flow distribution | The share of each item type that reached Done | Compare it with the planned balance of features, enablers, defects and debt |
| Flow velocity | Items that reached Done in each week | Velocity in SAFe means throughput. It is not story points. |
| Flow time | The time from the commitment point to Done: the median (p50), p85 and p95 | Use p85 for a forecast to a customer: 85% of items took this time or less |
| Flow load | The items after the commitment point and before Done: at this time, and the daily average | This is the WIP of the system |
| Flow efficiency | The active time divided by the flow time | 15% to 40% is usual for knowledge work. The status time is not the touch time, so the true value is lower. |
| Flow predictability | From the PI objectives: the actual business value divided by the planned value | Give the values with `--pi-objectives`. Without them, the script gives the variation of the weekly throughput as a proxy, and writes TBD. |

Little's law connects three of the metrics: the average flow time is the average WIP divided by
the average throughput. The report compares the two values. A large difference shows that the
WIP grows, or that the board has items that stay open.

### Rules for the metrics

- Measure the system, not people. Do not show a metric for each person.
- Show a range, not one number: p50 and p85, or p10 to p90.
- Compare a team with its own history, not with other teams.
- A difference between two groups (for example `--segment label:dor-met`) is a correlation. The
  workshop finds the cause.
- Times are calendar days. Use `--workdays` to count Monday to Friday only.
