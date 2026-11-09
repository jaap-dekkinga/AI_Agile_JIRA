# Story template

Use this shape for each user story that the skill writes. It puts the focus on who, what and
why. It leaves the how to the team.

```markdown
**Title:** <short result, verb first — "Filter products by price">

As a <specific user or role>
I want <capability, in the user's words>
so that <the benefit to that user or the business>

### Acceptance criteria
- Given <starting context>, When <action>, Then <observable result>
- Given …, When …, Then …
- (measurable where it matters: "within 2 seconds", "at least 4.5:1 contrast")

### Notes
- Out of scope: <what this story deliberately leaves out>
- Dependencies: <linked issue keys, or "none">
- Open questions: <Q-NNN or the question, its owner, and the assumption meanwhile>

### INVEST score: <N/6>
| Criterion | Rating | Why |
|---|---|---|
| Independent | | |
| Negotiable | | |
| Valuable | | |
| Estimable | | |
| Small | | |
| Testable | | |
```

## Jira fields

| Field | Value |
|---|---|
| Issue type | Story |
| Summary | The title |
| Description | All the text from "As a" down |
| Parent | The key of the epic |
| Story points | Empty. The team uses #NoEstimates |
| Labels | The labels of the team, and the milestone label (`MS2`) if the story delivers one |
| Sprint | Only after Engineering agrees at sprint planning |

## Definition of Ready

Before you propose a story for a sprint, make sure that it meets the
[Definition of Ready](ceremonies.md#definition-of-ready):

- [ ] The title is clear.
- [ ] The value for the user is explicit.
- [ ] The acceptance criteria are written and detailed.
- [ ] The team can complete the story in one sprint.
- [ ] The dependencies are listed.
- [ ] No blocker stops the story, and each dependency is unblocked.

Show the INVEST score with the story. It helps the conversation, but it is not a condition.
