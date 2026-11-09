<!-- spec-meta
id: eligibility
last_updated: 2026-11-09
-->

# Eligibility

> An example spec area from the fictional Harbor Claims Assistant. It shows the rule format
> that CDD uses: stable `area-NNN` ids, rules in plain language, **Forbidden** lists, and dated
> amendments in place. This example does not include the rules that it cites in other areas
> (`clearinghouse-NNN`, `batch-NNN`, `phi-NNN`).

## Overview

[glossary.md](glossary.md#industry-standards) defines the X12 transactions and code sets that
this page names.

Eligibility asks a payer if a member has a plan in force on a date of service, and what the plan
covers. It is the second transaction on the clearinghouse seam (`spec/clearinghouse.md`). All
that the seam area says applies here without change: vendor selection by Coverage, transport
outcomes, journaling and retention. This area gives only what is different for a 270/271.

Two things are different. First, a 271 describes a person. Thus we decided in advance what the
product keeps from it (ADR 0017 in the [decision log](../docs/adr/README.md)). Second, this area
calls the insurance of the member a Plan, never coverage. In this product, *Coverage* already
means if a vendor can get to a payer.

This area does not include two other checks. People often call them insurance verification, and
neither has a spec yet:

- *Insurance discovery* looks for the plans of a member from demographics, when the payer is not
  known. It answers with candidates, each with a confidence, not with facts. It cannot say which
  payer is primary. It gives the best results with an address and a Social Security number, and the product
  does not accept these ([`Q-047`](../docs/platform/open-questions.md#q-047)). Roadmap S8-08.
- *Coordination of benefits* starts from one known active plan. It finds the other plans of the
  member, and which plan is primary when this is possible to find. Roadmap S8-13.

The first Product Vendor offers both checks, but its test mode supports neither. Thus we can
make sure that they are correct only against production, with real patient data.

## Rules

### eligibility-001: One eligibility port, implemented by every vendor, the fake and the router

Eligibility has its own port, next to the claim status port (`clearinghouse-001`). Each
eligibility adapter, the in-memory fake and the router implement it. The router resolves payer
aliases first (`-020`). Then it selects a vendor by the Coverage of the payer for eligibility
(`clearinghouse-002`, `-010`). It reports no Coverage as a modeled answer (`-009`).

### eligibility-002: An inquiry is validated before a vendor is called, and every problem is reported

An eligibility inquiry names a payer, a provider and a subscriber. The provider has an
identifier and a name (an organization name, or a last name for an individual provider). The
subscriber has a member id, a first name and a last name.

The date of birth identifies the patient. When the subscriber is the patient, the date of birth
of the subscriber is required. When the patient is a dependent, the date of birth of the
dependent is required. A dependent needs a first name, a last name and a date of birth. Then the
date of birth of the subscriber is optional. When the patient is the child or the spouse of a
policyholder, the date of birth of the policyholder is often not known, and payers answer
without it. The inquiry sends a gender only with a date of birth. Service type codes are one or
two characters from the X12 code list.

The product reports each problem as a structured violation that names its rule
(`clearinghouse-003`, `-017`). Subscriber identity fails closed. We can recover from a blocked
inquiry, but not from an answer about the wrong person.

### eligibility-003: The date of service and the service types have stated defaults

An inquiry without a date of service asks about the day on which it is made. The result says
which day that was. An inquiry without service types asks about `30`, health benefit plan
coverage. This is the industry code for the full plan. A Client cannot choose either default. The
product puts no other limit on the date of service. A payer that does not answer for a date
rejects the inquiry, and the product reports it as a rejection (`eligibility-006`).

**Forbidden:**
- Leaving the date the answer is about implicit.

### eligibility-004: The canonical eligibility model is X12-271-shaped

A result carries the plans of the payer, its benefit rows, its rejections, its warnings, the
transport metadata and Evidence (ADR 0017). A plan carries its name, group, insurance type,
coverage level, begin date and end date.

A benefit row carries these elements: the benefit code and name, service type codes, coverage
level, insurance type, time period, amount, percent, in-network indicator and plan coverage
description. Under `eligibility-011`, it also carries the authorization indicator, the quantity
and its qualifier, and related entities. It also carries the messages of the payer, and the plan
and benefit dates of the row.

The product keeps each benefit row that the payer sent, with the elements in the two paragraphs
before this one. If the payer did not send an amount, a percent or a quantity, it is absent. It
is never zero.

A benefit row still does not carry some elements: service delivery patterns, composite procedure
identifiers, additional eligibility information, and the addresses and contact details of related
entities. The last element is absent by design (`eligibility-011`). The other elements wait for a
capability that needs them. No surface shows the rows as the complete statement of benefits of
the payer.

**Forbidden:**
- Reading a missing amount as zero.
- Removing benefit rows in the adapter because no current surface shows them.
- Reading a missing quantity as zero.
- Presenting the benefit rows as the payer's complete statement of benefits.

### eligibility-005: Plan status is read from the benefit code, and is never guessed

The plan status of a result is `ACTIVE` when a row for the requested service types carries
benefit code `1` (active coverage). It is `INACTIVE` when such a row carries `6` (inactive). A row
that names no service type answers for all service types. When the rows give neither code, the
status is `UNKNOWN`. When they give both codes, the status is `UNKNOWN`, with a warning that
names the conflict.

**Forbidden:**
- Reporting `ACTIVE` because the result has a plan or because no row said otherwise.
- Resolving a conflict by taking the first row.

### eligibility-006: A rejected inquiry is never reported as an inactive plan

A payer or a clearinghouse can reject the inquiry. This can be a request validation segment,
for example reason `72` (invalid member id) or `75` (subscriber not found). It can also be an EDI
acknowledgement. Then the result records a rejection with its reason and follow-up codes,
separately from the plans.

A result that has only rejections has no plan status, and its transport outcome is `REJECTED`. A
result with no plan and no rejection is `NO_MATCH`, and it also has no plan status. In these two
cases, the payer said nothing about a plan. The product reads the outcome from the payload,
because a vendor can send the rejection of a payer in a successful HTTP call.

This rule is `clearinghouse-006` for eligibility. If the product reports a rejection as
`INACTIVE`, it tells a patient that they have no insurance because of a typing error in a member
id.

### eligibility-007: The member's identity is never part of a result

The canonical result carries no name, date of birth, gender, address, member id or other
identifier of the subscriber or the dependent. This includes all identifiers that the payer sends
back. The adapter does not read them. As a result, they cannot get to an API response, a log
line, a span or a tool output. The raw payload carries them. The product keeps it only in the
transaction record, under its TTL (`clearinghouse-013`).

### eligibility-008: Every call is journaled with an allow-listed digest

The product journals each eligibility call as Evidence, like each other call
(`clearinghouse-012`), with the transaction type `ELIGIBILITY`. It makes the summaries of the call
from an allow-list: the payer, the provider identifier, the date of service, the service types,
the outcome, the plan status, the rejection codes and the number of benefit rows. It does not
summarize the benefits.

### eligibility-009: The eligibility route returns the canonical result

`POST /api/v1/eligibility` uses the same authentication as each other `/api/v1` route. It
accepts a payer, a provider, a subscriber, an optional dependent, an optional date of service and
optional service types. It returns the canonical result, the transport metadata, the Evidence and
the id of the journaled transaction. It reports invalid inquiries, no Coverage, enrollment gaps
and vendor failures in the same way as the claim status route (`clearinghouse-016`, `-017`).

Amended 2026-10-15: as on the claim status route, the answer gets to the caller, also when the
vendor takes a long time to give it, up to the timeout of the vendor. A vendor can keep a real-time
eligibility check open for two minutes.

Amended 2026-10-15: as on the claim status route, after the vendor answers, the answer gets the
full write deadline of the service, also when the call took a long time. This includes a fallback to a
second vendor after a timeout of the first vendor.

### eligibility-010: Without a vendor, the fake answers eligibility Demo Scenarios in Demo Mode only

In Demo Mode, when no vendor is configured, the in-memory fake answers the eligibility route.
The fake has a script of Demo Scenarios: an active plan, an inactive plan, and a rejected inquiry
(subscriber not found).

The fake also answers for the denied payer of the claim-status Demo Scenarios, with the inactive
plan. That plan ended before the date of service of that claim. Thus an eligibility check that
starts from the denied claim (`reference-ui-012`) shows why the claim was denied. The fake answers
no match for each other payer.

`GET /api/v1/eligibility/scenarios` lists the scenarios in the request shape of
`eligibility-009`. This route exists only while the fake answers the route, as with
`clearinghouse-022`. All scenario data is synthetic. Outside Demo Mode, eligibility without a
vendor key is not configured, as `clearinghouse-022` says of each transaction. The route answers
`503`, and the fake never answers.

### eligibility-011: A benefit row carries its detail, and still no person's identity

A benefit row carries these elements:

- Its authorization or certification indicator: `Y` (prior authorization is required), `N`, or
  `U` (unknown).
- Its quantity limit, and the qualifier that names what is counted (for example 20 visits).
- The free-text messages of the payer.
- Its plan and benefit dates.
- The entities that it names.

Related entities are the payers and providers that a row names. The row carries an organization
with its role, its name and its identifier. It carries a person only in a provider role (a
provider, a primary care provider, another physician, a contracted service provider), by NPI and
without a name. It does not carry a person in another role, for example the insured or a legal
representative.

The row carries an identifier only when it identifies an organization or a provider. Permitted
identifiers are an NPI, a payer id, a NAIC code, a CMS plan id and an ETIN. Tax, service
provider, facility and pharmacy processor numbers are also permitted. It never carries a member id, a Social
Security number or the health identifier of a person. It carries no address, no contact detail and
no relationship to the patient.

Other payers: the result also lists the entities on rows with benefit code `R` ("other or
additional payer") as its other payers. This is the signal in the 271 that the member has other
insurance. The list maps the code of the standard, as plan status does. It decides nothing about
which payer is primary.

Dates: the row carries a date only when it is a term of the plan or the benefit. These are plan,
benefit, eligibility, policy, period, service, continuation (COBRA) and added dates. It does not
carry dates of events in the life of the patient, for example a date of death, an admission, a
discharge or the latest visit.

Messages: these are the free text of the payer. The product redacts identifier patterns in them
(a Social Security number, a labeled date of birth, an email address, a telephone number). It
never journals messages (`eligibility-008`). Nobody can prove that free text has no name in it.
Thus a surface shows a message only with the rest of the result, never alone.

**Forbidden:**
- Carrying a person's name, address or contact detail from a related entity.
- Carrying a member id, a Social Security number or a person's health identifier as an entity's
  identifier.
- Deciding which payer is primary from the other payers.

### eligibility-020: In a vendor's test mode, the vendor's test requests are offered by name

The test mode of a vendor answers only the published mock requests of that vendor. It refuses
each other identity. When eligibility operates against a vendor in test mode, its adapter lists those
requests. Each request is complete and valid under `eligibility-002`, and has the Plan status that
the test mode answers with. `GET /api/v1/eligibility/samples` returns them in the request shape of
`eligibility-009`, in the same way as the Demo Scenarios (`eligibility-010`). The route exists only
in test mode. The Eligibility screen offers each request by name. When you choose one, it fills
in the form and sends nothing.

The mock requests carry the fictional test identities of the vendor, which its documentation
publishes. They are not patient data and not fixtures. They are in the adapter and in the vendor
guide, and committed fixtures stay synthetic (`phi-004`). The opt-in test of the adapter sends
each listed request to the test mode of the vendor, and makes sure that each Plan status is
correct. Thus the list that the screen offers is the list that the test proved.

**Forbidden:**
- Offering the test requests with a production key. There, a mock identity can get to a real payer.
- Sending a test request because it was chosen, without the form being submitted.
