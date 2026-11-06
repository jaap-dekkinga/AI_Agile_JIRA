# Epic template

An epic is a body of work that delivers one outcome and is too big for a sprint. It is made of
stories, and usually maps to one milestone.

```markdown
**Title:** <the outcome — "Automated re-status on connected payers">

### Goal
One sentence: what is true for users when this epic is done.

### Why now
The business reason and who asked for it.

### Scope
- In: <capabilities included>
- Out: <what is deliberately left for later>

### Success measure
How we will know it worked: a number and a date ("80% of due claims re-checked without a person
by 2026-12-04").

### Milestone
The Jira label that tracks it on the dashboard (`MS2`), its target date and its owner.

### Stories
The first stories, each one line. Each is written with the story template and rated on INVEST
before it enters a sprint.

### Risks and open questions
Each with an owner and the assumption we work on meanwhile.
```

## Jira fields

| Field | Value |
|---|---|
| Issue type | Epic (or the board's parent type, such as Workstream) |
| Summary | The title |
| Description | Everything above |
| Labels | The milestone label (`MS2`) so the dashboard counts its stories |
| Due date | The milestone's target date |

## Epic health check

An epic is ready to break into stories when it has a goal, a success measure, a scope with an
explicit "out" list, and an owner. The skill flags an epic whose stories are mostly `invest-low`
or `invest-tbd` as at risk for its milestone.
