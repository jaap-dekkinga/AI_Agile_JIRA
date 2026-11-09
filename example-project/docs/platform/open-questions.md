# Open questions

This page is the register of what the project does not know yet. Each question has a stable id,
an owner, what it blocks, the options, what can settle it, and the assumption. The assumption is
the basis for the work until the question gets an answer. We never renumber ids. A resolved or
duplicate question keeps its section.

> Example content. These questions belong to the fictional Harbor Claims Assistant.

## Blocking now

| Id | Question | Owner | Blocks |
|---|---|---|---|
| [Q-030](#q-030) | When must a status inquiry fall through to a second vendor? | Platform | S4 |
| [Q-047](#q-047) | Can the product accept an SSN and an address for insurance discovery? | Compliance | S5-06 |

## All questions

| Id | Question | Owner | Status |
|---|---|---|---|
| [Q-001](#q-001) | Does the new data platform replace the database of the claims system? | Platform | Resolved, misframed (2026-10-01) |
| [Q-022](#q-022) | Which follow-up window applies to a paper resubmission? | Product | Open |
| [Q-029](#q-029) | Who can approve an action that cannot be undone, such as a write-off? | Leadership | Open |
| [Q-030](#q-030) | When must a status inquiry fall through to a second vendor? | Platform | Open, blocking |
| [Q-047](#q-047) | Can the product accept an SSN and an address for insurance discovery? | Compliance | Open, blocking |
| Q-056 | Who can read the results of a batch? | Security | Reserved for S7-03 |
| Q-057 | Which agent can call which tool? | Platform | Reserved for S9-02 |

---

### Q-001

- Question: Does the new data platform replace the database of the claims system?
- Owner: Platform.
- Status: resolved, misframed (2026-10-01).

The listed options were replace, mirror, or leave in place. The answer was a fourth option. The
database moves to a managed PostgreSQL service, and its schema does not change. We corrected
the analysis that used the question in place. The change log of the roadmap records the work
that this answer unblocked.

### Q-022

- Question: Which follow-up window applies to a paper resubmission?
- Owner: Product.
- Blocks: nothing at this time.
- Assumption: 28 days. This is the window that the reference pack uses for electronic
  resubmissions.

### Q-029

- Question: Who can approve an action that cannot be undone, such as a write-off?
- Owner: Leadership.
- Blocks: each write-off gate.
- Assumption: the product only recommends. The system never does a write-off (ADR 0003).

### Q-030

- Question: When must a status inquiry fall through to a second vendor?
- Owner: Platform.
- Blocks: S4.
- Options: (a) only on a transport failure, (b) also on a "no match" answer, or (c) for each
  payer, from the client pack.
- What can settle it: the contract terms of the second vendor on billable retries.
- Assumption: (a). The product never sends the inquiry to another vendor after an answer from a
  payer.

### Q-047

- Question: Can the product accept a Social Security number and an address for insurance
  discovery?
- Owner: Compliance.
- Blocks: S5-06.
- Assumption: no. The product does not offer discovery until this question gets an answer.
