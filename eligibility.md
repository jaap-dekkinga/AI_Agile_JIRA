<!-- spec-meta
id: eligibility
last_updated: 2026-10-15
-->

# Eligibility

> An example spec area from the fictional **Harbor Claims Assistant**. It shows the rule format
> CDD uses: stable `area-NNN` ids, plain-language rules, **Forbidden** lists, and dated
> amendments in place. Rules it cites in other areas (`clearinghouse-NNN`, `batch-NNN`,
> `phi-NNN`) are not included in this example.

## Overview

X12 transactions and code sets named here are defined in
[glossary.md](glossary.md#industry-standards).

Eligibility asks a payer whether a member has a plan in force on a date of service, and what it
covers. It is the second transaction on the clearinghouse seam (`spec/clearinghouse.md`).
Everything that area says about the seam holds here unchanged: vendor selection by Coverage,
transport outcomes, journalling, retention. This area says only what is different about a
270/271.

Two things are. First, a 271 describes a person, so what the product keeps from it is decided up
front (ADR 0017 in the [decision log](../docs/adr/README.md)). Second, the member's insurance is
called a **Plan** here, never coverage, because *Coverage* in this product already means whether
a vendor can reach a payer.

**Not covered here.** Two other checks are often called insurance verification, and neither is
specified yet:
- *Insurance discovery* looks for a member's plans from demographics when the payer is unknown.
  It answers with candidates, each with a confidence, not facts, and cannot say which payer is
  primary. It works best with an address and a Social Security number, which the product does
  not accept ([`Q-047`](../docs/platform/open-questions.md#q-047)). Roadmap S8-08.
- *Coordination of benefits* starts from one known active plan and finds the member's other
  plans, and which is primary where that can be determined. Roadmap S8-13.

The first Product Vendor offers both, and supports neither in its test mode, so both can be
verified only against production, with real patient data.

## Rules

### eligibility-001: One eligibility port, implemented by every vendor, the fake and the router

Eligibility has its own port, beside the claim status port (`clearinghouse-001`). Every
eligibility adapter, the in-memory fake and the router implement it. The router selects a vendor
by the payer's Coverage for eligibility (`clearinghouse-002`, `-010`), resolves payer aliases
first (`-020`), and reports no Coverage as a modelled answer (`-009`).

### eligibility-002: An inquiry is validated before a vendor is called, and every problem is reported

An eligibility inquiry names a payer, a provider with an identifier and a name (an organization
name, or a last name for an individual provider), and a subscriber with a member id and a first
and last name. The date of birth identifies the patient: the subscriber's is required when the
subscriber is the patient, and a dependent's when the patient is a dependent. A dependent needs a
first and last name and a date of birth; the subscriber's date of birth is then optional, because
a policyholder's is often not known when the patient is their child or spouse, and payers answer
without it. A gender is sent only with a date of birth. Service type codes are one or two
characters of the X12 code list.

Every problem is reported, each as a structured violation naming its rule (`clearinghouse-003`,
`-017`). Subscriber identity fails closed: a blocked inquiry is recoverable, and one answered
about the wrong person is not.

### eligibility-003: The date of service and the service types have stated defaults

An inquiry with no date of service asks about the day it is made, and the result says which day
that was. An inquiry with no service types asks about `30`, health benefit plan coverage, the
industry's code for the plan as a whole. Neither default is a Client choice. The product does not
bound the date of service further: a payer that will not answer for a date rejects the inquiry,
and that is reported as a rejection (`eligibility-006`).

**Forbidden:**
- Leaving the date the answer is about implicit.

### eligibility-004: The canonical eligibility model is X12-271-shaped

A result carries the payer's plans, its benefit rows, any rejections, warnings, the transport
metadata and Evidence (ADR 0017). A plan carries its name, group, insurance type, coverage level
and begin and end dates. A benefit row carries the benefit code and name, service type codes,
coverage level, insurance type, time period, amount, percent, in-network indicator and plan
coverage description, and, under `eligibility-011`, the authorization indicator, the quantity and
its qualifier, related entities, the payer's messages and the row's plan and benefit dates.

Every benefit row the payer sent is kept, with the elements above. An amount, a percent or a
quantity the payer did not send is absent, never zero.

A few elements of a benefit row are still **not carried**: service delivery patterns, composite
procedure identifiers, additional eligibility information, and related entities' addresses and
contact details. The last is by design (`eligibility-011`); the rest wait for a capability that
needs them. No surface presents the rows as the payer's complete statement of benefits.

**Forbidden:**
- Reading a missing amount as zero.
- Dropping benefit rows in the adapter because no current surface shows them.
- Reading a missing quantity as zero.
- Presenting the benefit rows as the payer's complete statement of benefits.

### eligibility-005: Plan status is read from the benefit code, and is never guessed

A result's plan status is `ACTIVE` when a row answering for the service types asked about carries
benefit code `1` (active coverage), and `INACTIVE` when one carries `6` (inactive). A row naming
no service type answers for all of them. When the rows state neither, the status is `UNKNOWN`.
When they state both, the status is `UNKNOWN` with a warning naming the conflict.

**Forbidden:**
- Reporting `ACTIVE` because a plan is present or no row said otherwise.
- Resolving a conflict by taking the first row.

### eligibility-006: A rejected inquiry is never reported as an inactive plan

When a payer or clearinghouse rejects the inquiry (a request validation segment such as reason
`72`, invalid member id, or `75`, subscriber not found, or an EDI acknowledgement), the result
records a rejection with its reason and follow-up codes, separately from any plan. A result that
is only rejections has no plan status and the transport outcome `REJECTED`. A result with
neither a plan nor a rejection is `NO_MATCH` and has no plan status either: in neither case has
the payer said anything about a plan. The outcome is read from the payload, because a vendor may
answer a payer's rejection with a successful HTTP call.

This is `clearinghouse-006` for eligibility. Reporting a rejection as `INACTIVE` tells a patient
they are uninsured because a member id was mistyped.

### eligibility-007: The member's identity is never part of a result

The canonical result carries no name, date of birth, gender, address, member id or other
identifier of the subscriber or dependent, including whatever the payer echoes back. The adapter
reads past them. They therefore cannot reach an API response, a log line, a span or a tool
output. The raw payload, which does carry them, is kept only in the transaction record under its
TTL (`clearinghouse-013`).

### eligibility-008: Every call is journalled with an allow-listed digest

Every eligibility call is journalled as Evidence like any other (`clearinghouse-012`), with
transaction type `ELIGIBILITY`. Its summaries are built from an allow-list: the payer, the
provider identifier, the date of service, the service types, the outcome, the plan status, the
rejection codes and the number of benefit rows. Benefits themselves are not summarised.

### eligibility-009: The eligibility route returns the canonical result

`POST /api/v1/eligibility` sits behind the same authentication as every other `/api/v1` route.
It accepts a payer, a provider, a subscriber, an optional dependent, an optional date of service
and optional service types. It returns the canonical result, the transport metadata, the Evidence
and the id of the journalled transaction. Invalid inquiries, no Coverage, enrollment gaps and
vendor failures are reported as the claim status route reports them (`clearinghouse-016`,
`-017`).

Amended 2026-10-15: like the claim status route's, its answer reaches the caller however long the
vendor takes to give it, up to the vendor's own timeout. A vendor may hold a real-time
eligibility check open for two minutes.

Amended 2026-10-15: as on the claim status route, once the vendor has answered, the answer gets
the service's whole write deadline, however long the call took, including a fallback to a second
vendor after the first timed out.

### eligibility-010: Without a vendor, the fake answers eligibility Demo Scenarios in Demo Mode only

In Demo Mode, when no vendor is configured, the eligibility route is backed by the in-memory fake,
scripted with Demo Scenarios: an active plan, an inactive plan, and a rejected inquiry (subscriber
not found). The claim-status Demo Scenarios' denied payer is answered too, with the inactive plan,
which ended before that claim's date of service, so an eligibility check handed over from the
denied claim (`reference-ui-012`) shows why it was denied. Every other payer is answered no match.
`GET /api/v1/eligibility/scenarios` lists them in the request shape of `eligibility-009`, and
exists only while the fake backs the route, as with `clearinghouse-022`. All scenario data is
synthetic. Outside Demo Mode, eligibility with no vendor key is unconfigured, as
`clearinghouse-022` says of every transaction: the route answers `503` and the fake never answers.

### eligibility-011: A benefit row carries its detail, and still no person's identity

A benefit row carries its authorization or certification indicator (`Y`, prior authorization is
required; `N`; `U`, unknown), its quantity limit and the qualifier naming what is counted (for
example 20 visits), the payer's free-text messages, its plan and benefit dates, and the entities
it names.

**Related entities** are the payers and providers a row names. An organisation is carried with
its role, its name and its identifier. A person is carried only in a provider role (a provider,
a primary care provider, another physician, a contracted service provider), by NPI and without a
name. A person in any other role, such as the insured or a legal representative, is not carried
at all. Identifiers are carried only when they identify an organisation or a provider (an NPI, a
payer id, a NAIC code, a CMS plan id, a tax, service provider, facility or pharmacy processor
number, an ETIN); never a member id, a Social Security number or a person's health identifier.
No address, contact detail or relationship to the patient is carried.

**Other payers.** The entities named on rows with benefit code `R`, "other or additional payer",
are also listed on the result as its other payers: the 271's own signal that the member has other
insurance. It maps the standard's code, as plan status does, and decides nothing about which
payer is primary.

**Dates** are carried only when they are terms of the plan or the benefit: plan, benefit,
eligibility, policy, period, service, continuation (COBRA) and added dates. Dates that are events
in the patient's life, such as a date of death, an admission, a discharge or the latest visit, are
not carried.

**Messages** are the payer's free text. Identifier patterns in them (a Social Security number, a
labelled date of birth, an email address, a telephone number) are redacted, and messages are never
journalled (`eligibility-008`). Free text cannot be proved free of a name, so a surface shows a
message only alongside the rest of the result, never on its own.

**Forbidden:**
- Carrying a person's name, address or contact detail from a related entity.
- Carrying a member id, a Social Security number or a person's health identifier as an entity's
  identifier.
- Deciding which payer is primary from the other payers.

### eligibility-020: In a vendor's test mode, the vendor's test requests are offered by name

A vendor's test mode answers only the vendor's own published mock requests, and refuses any other
identity. When eligibility runs against a vendor in test mode, its adapter lists those requests,
each complete and valid under `eligibility-002` and each with the Plan status the test mode answers
with, and `GET /api/v1/eligibility/samples` returns them in the request shape of `eligibility-009`,
as the Demo Scenarios are returned (`eligibility-010`). The route exists only in test mode. The
Eligibility screen offers each one by name; choosing one fills the form and sends nothing.

The mock requests carry the vendor's fictional test identities, published in its documentation.
They are not patient data and not fixtures: they live in the adapter and in the vendor guide, and
committed fixtures stay synthetic (`phi-004`). The adapter's opt-in test sends every listed request
to the vendor's test mode and checks each Plan status, so the list offered is the list verified.

**Forbidden:**
- Offering the test requests with a production key, where a mock identity would reach a real payer.
- Sending a test request because it was chosen, without the form being submitted.
