# Open questions

The register of what the project doesn't know yet. Each question has a stable id, an owner, what
it blocks, the options, what would settle it, and the **assumption** work proceeds on until it is
answered. Ids are never renumbered; a resolved or duplicate question keeps its section.

> **Example content.** These questions belong to the fictional Harbor Claims Assistant.

## Blocking now

| Id | Question | Owner | Blocks |
|---|---|---|---|
| [Q-030](#q-030) | When should a status inquiry fall through to a second vendor? | Platform | S4 |
| [Q-047](#q-047) | May the product accept an SSN and address for insurance discovery? | Compliance | S5-06 |

## All questions

| Id | Question | Owner | Status |
|---|---|---|---|
| [Q-001](#q-001) | Does the new data platform replace the claims system's database? | Platform | Resolved, misframed (2026-10-01) |
| [Q-022](#q-022) | Which follow-up window applies to a paper resubmission? | Product | Open |
| [Q-029](#q-029) | Who may approve an irreversible action such as a write-off? | Leadership | Open |
| [Q-030](#q-030) | When should a status inquiry fall through to a second vendor? | Platform | Open, blocking |
| [Q-047](#q-047) | May the product accept an SSN and address for insurance discovery? | Compliance | Open, blocking |
| Q-056 | Who may read a batch's results? | Security | Reserved for S7-03 |
| Q-057 | Which agent may call which tool? | Platform | Reserved for S9-02 |

---

### Q-001

**Question:** Does the new data platform replace the claims system's database?
**Owner:** Platform. **Status:** resolved, misframed (2026-10-01).

The options listed were replace, mirror, or leave in place. The answer was a fourth: the
database moves to a managed PostgreSQL service with its schema intact. Analysis built on the
question was corrected in place, and the roadmap's change log records what that unblocked.

### Q-022

**Question:** Which follow-up window applies to a paper resubmission?
**Owner:** Product. **Blocks:** nothing yet. **Assumption:** 28 days, the window the reference
pack uses for electronic resubmissions.

### Q-029

**Question:** Who may approve an irreversible action such as a write-off?
**Owner:** Leadership. **Blocks:** any write-off gate. **Assumption:** the product only
recommends; no write-off is ever executed by the system (ADR 0003).

### Q-030

**Question:** When should a status inquiry fall through to a second vendor?
**Owner:** Platform. **Blocks:** S4.
**Options:** (a) only on a transport failure; (b) also on a "no match" answer; (c) per payer,
from the client pack.
**What would settle it:** the second vendor's contract terms on billable retries.
**Assumption:** (a). A payer's answer is never retried elsewhere.

### Q-047

**Question:** May the product accept a Social Security number and an address for insurance
discovery?
**Owner:** Compliance. **Blocks:** S5-06.
**Assumption:** no. Discovery is not offered until this is answered.
