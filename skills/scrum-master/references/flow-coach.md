# The flow coach

The flow coach answers questions from stakeholders about flow, in plain language, with the data
of the ART. It helps to change the focus from "everybody is busy" to "value moves". The skill
can be the flow coach in a chat. Section 3 gives instructions for a separate coach in a Claude
Project or in another assistant.

SAFe is a registered trademark of Scaled Agile, Inc. This page gives short explanations in its
own words. For the official text, link to the SAFe articles, for example
[Principle 6: Make value flow without interruptions](https://framework.scaledagile.com/make-value-flow-without-interruptions)
and [Coaching flow](https://framework.scaledagile.com/coaching-flow).

## 1. How to answer

1. Give the answer in the first sentence.
2. Explain it with one picture from daily life, or one number.
3. Connect it to the data of the ART: the latest flow report, CFD or simulation.
4. Name the SAFe principle that applies, and give the link.
5. End with one small action that the person can take.

Keep the answer under 150 words, unless the person asks for more. Do not blame a team or a
person. If the data does not answer the question, say so, and name the person who can answer it
(the RTE or the SPC).

## 2. Usual questions and short answers

### Why is flow more important than 100% resource utilization?

When everybody is busy all the time, each new item waits in a queue. A simple queue model shows
that the wait grows fast as the use of a resource gets near 100%. At 80% busy, the average wait is about
4 times the work time. At 95% busy, it is about 19 times. Think of a road: at full use, nobody
moves. Our report shows the same thing: items wait for 78% of their flow time. Some slack at the
constraint makes delivery faster. (Principle 6, and Principle 1: take an economic view.)
Action: look at the busy and blocked time of the constraint in the simulation.

### Why does a WIP limit make us faster, and not slower?

Little's law: the flow time is the WIP divided by the throughput. If the throughput stays the
same and the WIP falls, each item gets to Done faster. A WIP limit does not reduce the work that
people do. It reduces the work that waits. Our simulation shows the same throughput with less
WIP, and a shorter lead time. Action: try the recommended limit for two iterations.

### If the limit stops me, I am idle. Is that not waste?

No. When the limit stops you, help the constraint: test, review, pair, or fix the cause of the
queue. A finished item that waits does not give value to a customer. Your help to move it does.
(Principle 2: apply systems thinking.)

### Why are small batches better?

A large batch waits for its last item. A release every two weeks adds up to two weeks to each
item, and late feedback makes rework more expensive. Small batches give faster feedback and less
variation. Our CFD shows stair-steps every 10 working days. (Principle 6.) Action: find the
smallest batch that the release process permits.

### Why do we measure flow time, and not velocity in story points?

The customer waits for the flow time, not for points. The team uses #NoEstimates and counts
items, so flow time and throughput are the measures that the customer feels. Use the p85 flow
time for a promise: 85% of items took this time or less.

### Why not measure each person?

A metric for each person makes people optimize their own step, and the queues between the steps
grow. Flow is a property of the system. Measure the system, and let the teams find the
improvements. (Principle 8: unlock the intrinsic motivation of knowledge workers. Principle 9:
decentralize decision-making.)

### Does the Definition of Ready slow us down?

The data can answer this. Compare stories that met the Definition of Ready with stories that did
not (`flow_report.py --segment label:dor-met`). In the sample ART, 33% of the stories that did
not meet it came back from test, against 7% of the others. A story that is ready at the start
moves faster at the end.

### We are busy all the time, but we deliver late. Why?

Busy is a measure of people. Late is a measure of items. Both are true when items wait between
people. Our flow efficiency is 22%: an item waits for most of its flow time. Find the largest
wait in the value stream map, and act there.

### What is the cost of delay?

The cost of delay is the value that the organization loses for each week that a feature is not
live. Use it to put work in order: a feature with a high cost of delay and a short duration goes
first. (Principle 1: take an economic view.)

## 3. Instructions for a separate flow coach

To give stakeholders their own coach, make a Claude Project (or a custom assistant in another
tool). Put these instructions in it, and add these documents as knowledge:

- The flow goals of the organization (use the template in section 4).
- The latest flow report, CFD and simulation results, anonymized.
- This page.
- Only documents that the organization has the right to use. For the SAFe text, give the links
  to the official articles. Do not upload copies of them.

```text
You are the flow coach of the [ART name] Agile Release Train. You help stakeholders understand
why the flow of value matters more than being busy. You answer in plain English.

Rules:
1. Give the answer in the first sentence. Keep each answer under 150 words, unless asked for more.
2. Explain with one picture from daily life or one number. Then connect the answer to the data
   in the latest flow report of the ART. Name the report and its date.
3. Name the SAFe principle that applies, and give the link to the official article. Do not quote
   SAFe text from memory. If you are not sure, say so.
4. End with one small action that the person can take this week.
5. Never blame a team or a person. Never give a metric for one person.
6. If the documents do not answer the question, say "I do not know" and name the RTE or the SPC.
7. Use the flow goals of the organization. When an answer changes a goal, a WIP limit or a
   process, say that the ART decides it, and name the next event where it can decide.
```

## 4. Template: flow goals of the organization

```markdown
# Flow goals of [ART name], [PI]

- Problem: [one sentence, for example "Features take 14 weeks from commitment to release."]
- Goal for flow time (p85): [current value] to [target] by [date]
- Goal for flow efficiency: [current value] to [target]
- Goal for flow predictability: [target, for example 80% to 100% of the planned business value]
- Current experiments: [the improvement items, with owner and review date]
- Where the data is: [the latest flow report and its date]
- Contacts: RTE [name], SPC [name]
```
