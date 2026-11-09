# Epic template

An epic is a body of work that gives one result and is too large for one sprint. It has
stories, and usually has one milestone.

```markdown
**Title:** <the result — "Automated re-status on connected payers">

### Goal
One sentence: what is true for users when this epic is done.

### Why now
The business reason, and who asked for it.

### Scope
- In: <capabilities included>
- Out: <what is deliberately left for later>

### Success measure
How we will know it worked: a number and a date ("80% of due claims re-checked without a person
by 2026-12-04").

### Milestone
The Jira label that tracks it on the dashboard (`MS2`), its target date and its owner.

### Stories
The first stories, one line each. Each is written with the story template and gets an INVEST
score in refinement.

### Risks and open questions
Each with an owner and the assumption we work on meanwhile.
```

## Jira fields

| Field | Value |
|---|---|
| Issue type | Epic (or the parent type of the board, for example Workstream) |
| Summary | The title |
| Description | All the text of the template |
| Labels | The milestone label (`MS2`), so that the dashboard counts its stories |
| Due date | The target date of the milestone |

## Epic health check

An epic is ready to split into stories when it has a goal, a success measure, a scope with an
explicit "out" list, and an owner. If most stories of an epic have a low INVEST score, the skill
tells the user that the milestone of the epic is at risk.
