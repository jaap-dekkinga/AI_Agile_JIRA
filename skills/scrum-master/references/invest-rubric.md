# INVEST rubric

Every story gets **Low**, **Good** or **TBD** on each of the six INVEST criteria, and one overall
rating. INVEST is checked during backlog refinement, so stories are ready before sprint planning.
Developers add the technical view (feasibility, testability); the Product Owner owns the rest.

## The scale

| Rating | Means | Jira label |
|---|---|---|
| **Good** | The story meets the criterion, and the text shows it. | `invest-good` |
| **Low** | The story fails the criterion. It needs rework before it is Ready. | `invest-low` |
| **TBD** | There is not enough information to judge yet. Name who will supply it. | `invest-tbd` |

**Overall rating:** Low if any criterion is Low. TBD if none is Low but any is TBD. Good only if all
six are Good. A missing estimate is TBD, not Low. Every TBD names an owner or an open question.

## The criteria

| Criterion | Good | Low | TBD when |
|---|---|---|---|
| **Independent** — can be built and tested apart from other stories | No unresolved dependencies, or they are stubbed. Shares no files with other stories in flight. | Blocked by an unfinished story; hidden or circular dependencies; must ship together with another story. | A dependency is mentioned but not confirmed or linked. |
| **Negotiable** — a conversation starter, not a contract | States the outcome and the rules; leaves the "how" to the team. | Prescribes the implementation ("must use table X", "add column Y"). | Scope is still being agreed with the PO or a stakeholder. |
| **Valuable** — delivers clear value to a user or the business | The "so that …" names who benefits and how. | A technical task with no stated beneficiary, or value only after other stories ship. | No benefit is stated yet; the PO confirms it. |
| **Estimable** — the team can size it | The team agreed points in planning poker. | The team can't estimate it: an unknown domain or a blocking question with no assumption. Needs a spike. | Not estimated yet, or an open question needs a recorded assumption first. |
| **Small** — fits in one sprint | 8 points or fewer; one pull request merged within a few days. | 13 points or more, or spans sprints. Split it. | Size unknown because it isn't estimated. |
| **Testable** — clear criteria verify it | Given/When/Then acceptance criteria, measurable where it matters. | Vague criteria ("fast", "user-friendly", "works well") with nothing measurable, or an estimated story with no criteria at all. | Criteria not written yet on an unrefined story. |

## Splitting a story that is Low on Small

Split along a line that keeps each part valuable on its own:

1. **Workflow steps:** one story per step a user takes (search, filter, save).
2. **Business rules:** the main rule first, the exceptions as later stories.
3. **Data variations:** one data type, source or payer at a time.
4. **Happy path first:** the main success path, then error handling.
5. **Spike, then build:** a time-boxed spike when the team can't estimate.

## Fixing a story that is Low on Independent

Remove the dependency (reorder the backlog), combine the two stories if they can't ship apart, or
stub the missing piece so this one can be built and tested now.

## Worked examples

**Good:**

> **Offer the vendor's test requests by name** (5 points)
> As a billing specialist I want to pick one of the vendor's published test requests by name
> so that I can try eligibility in test mode without typing an identity by hand.
> - Given eligibility runs in test mode, When I open the Eligibility screen, Then each test request is listed by name
> - Given I choose one, When the form fills, Then nothing is sent until I submit

**Low** (Independent, Negotiable, Small and Testable fail; Valuable is TBD):

> **Re-status job** (13 points, blocked by HCA-152)
> Build the re-status job. Must use the existing batch table and add a column for the ceiling.
> Should be fast. — *Acceptance: works well under load.*

Rewrite: split into "select due claims" and "send under a daily ceiling", state the benefit
("so that follow-up happens without a person checking each claim"), drop the table instructions,
and replace "fast" with a number ("processes 1,000 due claims in under 10 minutes").

## Where the rating lives in Jira

- **Label:** exactly one of `invest-good`, `invest-low`, `invest-tbd` on each story. JQL and the
  dashboard count it without needing a Jira admin. Replace the old label when the rating changes.
- **Detail:** an "INVEST" section at the end of the description, or a comment, with the six
  ratings and reasons (`scripts/invest_check.py --format jira` produces it).
- **Optional:** a custom field or checklist app, if your Jira admin prefers one.

## How the check is run

`scripts/invest_check.py` makes a first pass from the story text: dependency links and wording,
prescriptive phrases, a "so that" clause, points, and the acceptance criteria. It is a
heuristic. Review each rating, override it where the text misleads the script, and say why. When
the information isn't there, the answer is TBD and a question to the PO, never a guess.
