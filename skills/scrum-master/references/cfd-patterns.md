# Patterns in a cumulative flow diagram

A cumulative flow diagram (CFD) has one band for each stage. The height of a band on a day is
the number of items in that stage. The top edge of the Done band is the number of items that
the system delivered so far. The horizontal distance between the line into the first work
stage and the line into Done is about the flow time.

`scripts/flow/cfd.py` finds the patterns on this page and writes one plain sentence for each
pattern. The sentence gives the evidence (the numbers) and the usual cause. It does not prove
the cause. Ask the teams before you act.

## The patterns

| Pattern | What you see | What the script measures | Usual causes | First action |
|---|---|---|---|---|
| Bulge | A band gets wider | The average width in the last quarter of the period is 1.5 times the first quarter or more, and 3 items more or more | If the band is a queue, the next stage is a bottleneck. If the band is a work stage, the work takes longer, or more work starts than people can finish. | Find the constraint. Limit the WIP before it. Help the constraint. |
| Stair-steps | A line goes up in large steps, with flat parts between them | 50% or more of the moves happened on 10% of the working days | Batches: commitment at planning, release at fixed dates, test in a weekly cycle, a review meeting | Make the batch smaller, or more frequent. Release on demand. |
| Divergence | The arrival line goes up faster than the Done line | In the last six weeks, arrivals are 1.2 times the departures or more | Teams start work before they finish work. The commitment is larger than the capacity. | Stop starting, and start finishing. Commit less. Set WIP limits. |
| Converging lines | The Done line goes up faster than the arrival line | In the last six weeks, arrivals are 0.8 times the departures or less | The system finishes old work and starts little new work | Make sure that enough work is ready, or the teams will wait for work. |
| Flat departures | The Done line stays flat for a long time | No item reached Done for 10 working days or more, or for two release periods | A release freeze, a broken environment, an incident, a holiday | Find what stopped the delivery. |
| Thin band | A band is almost empty | The average width is less than 0.3 items | The team skips the status, or moves items through it in one minute. The board does not match the real work. | Remove the status, or use it as the real work happens. |
| Backlog growth | The backlog band gets wider | The backlog band grows by 1.5 times and 10 items or more | More requests arrive than the system can start | Refine and remove old items. Agree on a limit for the backlog. |

## How to explain a CFD to stakeholders

Use three sentences:

1. What the diagram shows: "Each color is a stage. The height is the number of items in the
   stage on that day."
2. The largest pattern, with its numbers: "The band Ready for Test grew from 8 to 22 items in
   six months. Items wait there for a tester."
3. What it means for the business: "The wait adds about two weeks to each feature, so the
   release of the feature comes two weeks later."

Then give the action and the measure: "We will limit the work in development to 4 items, and the
developers will help with tests. We will look at the width of the band again after two
iterations."

## Connect a pattern to a cause

Do not write a cause as a fact when the data shows only a pattern. Write it as a hypothesis, and
name the data that supports it. For example:

"Hypothesis: the flow predictability falls because stories enter the iteration before they meet
the Definition of Ready. Evidence: 33% of the stories without the label dor-met came back from
test, against 7% of the stories with the label. Their median flow time is 1.5 times longer. Test:
for two iterations, the ART starts only stories that meet the Definition of Ready, and compares
the rework."

`flow_report.py --segment label:dor-met` gives the evidence for this hypothesis. Use the same
method with other labels, item types or teams.

## Limits

- A CFD from status data shows the status, not the real work. An item in an active status can
  wait.
- The script does not show discarded items, and items that a bulk move closed. The text says how
  many it removed.
- Weekends do not count in the analysis of steps. Holidays count, so a holiday can look like a
  flat part.
- A short period (less than six weeks) gives weak findings.
