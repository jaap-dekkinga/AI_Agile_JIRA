# Story template

Use this shape for every user story the skill drafts. It keeps the focus on **who**, **what** and
**why**, and leaves the **how** to the team.

```markdown
**Title:** <short outcome, verb first — "Filter products by price">

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

### INVEST: <Good | TBD | Low>
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
| Description | Everything above from "As a" down |
| Parent | The epic's key |
| Story points | Set by the team in refinement, never by the skill |
| Labels | `invest-good` / `invest-tbd` / `invest-low`, plus any team labels |
| Sprint | Only after Engineering agrees at sprint planning |

## Checklist before a story is proposed for a sprint

- [ ] The "so that" names a real beneficiary.
- [ ] Two or more Given/When/Then criteria, measurable where it matters.
- [ ] Estimated at 8 points or fewer by the team.
- [ ] Dependencies linked in Jira, or none.
- [ ] Every open question has an owner and a recorded assumption.
- [ ] Overall INVEST rating is Good, or each TBD has an owner.
