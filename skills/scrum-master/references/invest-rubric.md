# INVEST rubric

Each story gets Good, TBD or Low on each of the six INVEST criteria, and a score: the number of
criteria rated Good, out of 6. The team checks INVEST during backlog refinement, before sprint
planning. The developers give the technical view (if the work is possible, and if they can do a
test of it). The Product Owner owns the rest.

The score is a tool for refinement. It has no failing grade. No score and no rating stops a
story from being Ready. The [Definition of Ready](ceremonies.md#definition-of-ready) decides
that.

## The ratings

| Rating | Meaning |
|---|---|
| Good | The story meets the criterion, and the text shows it. |
| TBD | The story does not give enough information to judge the criterion. Name the person who can give the information. |
| Low | The story does not meet the criterion. It is a topic for refinement, for example a rewrite or a split. |

A missing piece of information is TBD, not Low. Each TBD rating names an owner or an open
question.

## The score

The score is the number of Good ratings, for example `4/6`. The INVEST table in the Jira
description starts with the score (`### INVEST score: 4/6`). When the score changes, a later
check shows the earlier score.

## The criteria

The team uses #NoEstimates, so Estimable and Small do not use story points.

| Criterion | Good | Low | TBD when |
|---|---|---|---|
| Independent: the team can build it and do a test of it separately from other stories | No unresolved dependencies, or they have a stub. It shares no files with other stories in progress. | An unfinished story blocks it. It has hidden or circular dependencies. It must ship together with another story. | The text names a dependency, but nobody made sure of it or linked it. |
| Negotiable: a start for a conversation, not a contract | It gives the result and the rules. It leaves the "how" to the team. | It gives the implementation ("must use table X", "add column Y"). | The scope is not agreed yet with the Product Owner or a stakeholder. |
| Valuable: it gives clear value to a user or the business | The "so that …" names who gets the benefit, and how. | A technical task with no named beneficiary, or value only after other stories ship. | No benefit is given yet. The Product Owner gives it. |
| Estimable: the team understands the work well enough to judge if it fits in one sprint | The acceptance criteria tell the team what to build. | The domain is not known, so the team needs a spike first. | An open question has no recorded assumption, or the acceptance criteria are not written yet. |
| Small: the team can complete it in one sprint | One pull request, merged in a few days. The criteria show no sign that the work is larger. | It spans sprints, or the team marked it as too large. Split it. | The criteria are not written yet, or there are more than six of them. The team decides the size. |
| Testable: clear criteria make sure that it is correct | Given/When/Then acceptance criteria, with numbers where they are important. | Vague criteria ("fast", "user-friendly", "works well") with nothing to measure. | The criteria are not written yet. |

## How to split a story that is Low on Small

Split along a line that keeps the value of each part:

1. Workflow steps: one story for each step that a user does (search, filter, save).
2. Business rules: the main rule first, and the exceptions as later stories.
3. Data variations: one data type, source or payer at a time.
4. The main success path first: then the error handling.
5. A spike, then the build: a spike with a time limit, when the team cannot judge the work.

## How to correct a story that is Low on Independent

Remove the dependency (change the order of the backlog). Or combine the two stories, if they
cannot ship separately. Or make a stub of the missing part, so that the team can build this story
and do a test of it.

## Examples

A story with the score 6/6:

> Offer the test requests of the vendor by name
>
> As a billing specialist I want to pick one of the published test requests of the vendor by
> name so that I can try eligibility in test mode without typing an identity by hand.
>
> - Given eligibility runs in test mode, When I open the Eligibility screen, Then each test request is listed by name
> - Given I choose one, When the form fills, Then nothing is sent until I submit

A story with the score 1/6 (Low on Independent, Negotiable, Small and Testable, TBD on Valuable):

> Re-status job (label `too-big`, blocked by HCA-152)
>
> Build the re-status job. Must use the existing batch table and add a column for the ceiling.
> Should be fast. Acceptance: works well under load.

A rewrite: split it into "select due claims" and "send under a daily ceiling". Give the benefit
("so that follow-up happens without a person who examines each claim"). Remove the instructions
about the table. Replace "fast" with a number ("processes 1,000 due claims in less than 10
minutes").

## The rating in Jira

The rating is in the description of the story, as an INVEST section at the end: a heading with
the score (`### INVEST score: 4/6`) and a table of the six criteria, each with its rating and
its reason. `scripts/invest_check.py --format jira` makes this section. It also reads the
section back from an existing description, so that a later check can show what changed. When
the score changes, update the table. Do not add a second table.

## The check

`scripts/invest_check.py` makes a first pass from the text of the story: dependency links and
words, words that give the implementation, a "so that" clause, labels such as `too-big` and
`spike-needed`, and the acceptance criteria. It is a heuristic. Review each rating, and change
it where the text gives the script a wrong result. Say why. When the information is not there,
the answer is TBD and a question to the Product Owner. Never guess.
