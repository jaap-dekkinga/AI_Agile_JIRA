<!-- spec-meta
id: glossary
last_updated: 2026-11-09
-->

# Glossary

A Defined Term has the meaning on this page when it has a capital letter, in `spec/`, in code
comments and in documentation. The product uses this vocabulary. The pack of a client maps the
words of that client to it (see *Client word* in the table). Client words never get into the
Core.

The last part of this page lists the industry vocabulary: the X12 transactions and code sets
that the Core implements. These are not Defined Terms. They are the names that the industry
already uses. We repeat them here, so that nobody must leave the repository to read a rule.

> This glossary belongs to Harbor Claims Assistant, the fictional example product in
> `example-project/`. The healthcare terms are real industry vocabulary. The product, its
> company and the systems next to it are invented.

## Defined Terms

| Term | Meaning |
|---|---|
| Client | An organization for which we deploy and configure the product. Today, one deployment serves one Client. The data model still carries the identity of the Client, so that this assumption can change. |
| Client Pack | The configuration bundle of the Client: payer mappings, state rules, decision-table rows and thresholds, SOP playbooks, follow-up windows and reference codes. The service loads it at startup and validates it as a whole. It has a version. All that is specific to the Client is here, and nowhere else. |
| Core | The product code and the industry-standard data that is compiled into it: X12 grammars, CARC/RARC meanings, arithmetic and classification engines, and the service. The Core contains no Client identifiers. |
| Claim | A billed encounter as the practice-management system of the Client knows it, identified by the claim identifier of the Client. It carries lines, a payer, dates of service and balances. |
| Payer | The insurer or program that a Claim was billed to, with a canonical identity (name, type, state, program). The pack of a Client maps the payer code of that Client to the canonical Payer. |
| PMS | The practice-management or billing system of record of the Client. It is the source of Claims and the destination of notes. We use a general name for it. The specific system is a matter for the pack and the adapter. |
| Remit | An 835 remittance advice: paid and allowed amounts and adjustments for each line (`{group, CARC, amount}`), and RARCs. |
| Status | A 277 claim-status response tuple for a Claim: category code 507, status code 508, entity and free text. Classification uses the status code first. Payers do not apply category codes consistently, so the category decides only if a Claim is adjudicated. |
| Disposition | The coarse outcome of the Core for a Status: one of `ACCEPTED`, `FINALIZED_PAYMENT`, `FINALIZED_DENIAL`, `PENDING`, `REQUEST_INFO`, `ERROR`. It comes only from the category code (507), because X12 defines this element as the answer to whether a Claim is adjudicated. It is a closed set. A code without a mapping is `ERROR`, never a guess. It is not the *disposition code* of a Client. See Outcome Code. |
| Bucket | The classification of a Status that operators see: an id, a label and a tone. Unlike a Disposition, it uses the status code (508) first, because the same outcome comes to us under different category letters from different Payers. The id is Core vocabulary. The label is pack data. |
| Outcome Code | The code of a Client for the state in which a worked Claim was left, with the follow-up window that it carries. It names the action taken or the state found, for example a resubmission, an escalation, a write-off, a patient balance, or a hold to monitor. Clients often call these *disposition codes* or *action status codes*, but they are not a Disposition. A Disposition is the closed reading of a Status by the Core. An Outcome Code is Client vocabulary. It depends on what was done and on what the Payer said, and it is in the Client Pack. A Recommendation can name one. |
| Capability | A deterministic function of the Core that is available as a tool, for example CARC interpretation or the calculation of timely filing. Capabilities take their rule data from the Client Pack. |
| Playbook | The steps that an Operator follows to work a path: numbered steps, the branches that each step can take on what the Operator finds, and notes. It is Client Pack data (`client-packs-013`). The label of a branch is not an Outcome Code. |
| SOP | The standard operating procedure document of a Client. The Client Pack carries it section by section, and a table row cites it by section (`client-packs-012`). |
| Recommendation | The next action that a Capability proposes for a Claim, with a path or playbook, a *why* sentence, Evidence and Confidence. The system never acts on a Recommendation. |
| Evidence | The list of `{source, ref, detail}` records that explain a Recommendation: which rule, which segment, which pack file. Each Capability output carries Evidence. |
| Confidence | A number in [0, 1] that each Capability output carries. Precision is more important than recall. If no rule matches, the result is *no* Recommendation. It is never a guess with low confidence that looks like a Recommendation. |
| Audit Record | The append-only record of one Capability call: actor, tool, inputs and outputs with PHI redacted, Evidence, Confidence and time. |
| Operator | A human user of the Client who reviews Recommendations. |
| Demo Mode | The service runs without OAuth. Each request acts as the synthetic Demo User `demo@example.com`. |
| Trusted-network mode | The service runs without a login, on a private network that only one trusted caller can get to. Each request acts as that caller. When the caller names a user in `X-Acting-User`, the service records the user as asserted, never as verified (`service-011`). Unlike Demo Mode, this mode can serve Client data. |
| Demo Scenario | A synthetic inquiry that the in-memory fake clearinghouse answers with a scripted result (paid, denied, pending, rejected), when no vendor is configured. A reserved payer identifier selects it. It exists so that we can demonstrate the product. It is never the answer of a payer. |
| Reference UI | The demonstration and developer UI in `frontend/`. The binary serves it, and it is built only on the public API. It is not the product UI, which is built in Workbench. It is not a surface for Operators. |
| Workbench | The operator application of the fictional company, where the product UI is. It is a system next to this product, not a part of it. |
| Client word | The term of a Client for a product concept. For example, a Client can call a Claim an "invoice". Client words appear only in the pack of that Client, as labels, template text and code mappings. Operators of that Client see them. Core code, specs and APIs use the product term. |
| Clearinghouse | A vendor that carries X12 transactions between providers and Payers. The product gets to Payers only through a Clearinghouse. |
| Product Vendor | A Clearinghouse or a data service that the company itself has a contract with. It is the same for each Client of a deployment, and the company holds the credentials. Its adapter is Core code, which can name it. Compare this with the vendors of a Client, which stay in the pack of that Client. |
| Port | An interface that the Core defines to a system outside this service. It has one adapter for each system, and an in-memory fake for tests and Demo Mode. A Port can do network I/O and read the clock. A Capability cannot. |
| Transaction Type | An X12 exchange that the product does with a Payer: claim status (276/277), eligibility (270/271), claim submission (837) or remittance (835). |
| Coverage | Whether a Product Vendor can get to a given Payer for a given Transaction Type, and whether this needs Enrollment. It is declared for each (Payer, Transaction Type) pair. |
| Plan | The insurance of the member, as a Payer reports it in a 271: plan name and group, insurance type, coverage level and the dates of the plan. We never call it "coverage", because that word means vendor reachability (see Coverage). |
| Plan Status | `ACTIVE`, `INACTIVE` or `UNKNOWN`, read from the benefit code of a 271 for the requested service types (`eligibility-005`). A rejected eligibility inquiry has no Plan Status. |
| Enrollment | The authorization of a Payer for a specific Transaction Type through a specific Clearinghouse. It is the knowledge of the product. An Operator records it, and a Coverage sync never clears it. |
| Re-status | A claim status inquiry that the product sends on its own schedule, without a request from a person. It gets the status of a Claim again after the follow-up window of the Claim is past. A job sends it, not a Capability, because it reads the clock and spends billable calls. The job sends it only for a Payer that is turned on for it, one Payer at a time, separately from Coverage and Enrollment (`restatus-001`). An inquiry that a person makes is not a Re-status, also when it gets the status of a Claim again. |
| Transport Outcome | The vendor-neutral classification of what happened on the wire. It does not depend on what the Payer said about a Claim. It answers whether the product can retry a call. A Status cannot answer this. |
| Batch | Many inquiries of one transaction, given at the same time and answered later. Workbench gives them through the API, an Operator from a file, or the re-status job. A Batch is how calls travel, not how Claims are worked. Claim status fans out through the router. Eligibility goes in the native batch of a vendor, if the vendor has one (`spec/batch.md`). |
| Batch Item | One inquiry in a Batch. It holds the identity of the patient only while a later send can use it (`batch-006`). |
| Vendor Batch | One native submission to a vendor. It holds Batch Items of one or more Batches, under a name that the vendor refuses to run two times (`batch-015`). |
| Unresolved | A Batch Item that the product possibly sent, and whose answer is not known. The product never sends it again, because a second send can be billed two times. It is not a failure, because the Payer possibly answered (`batch-007`). |
| Tool | A Capability that is available to an external caller through the tool surface, with a stable name, a versioned schema and the standard envelope. A Tool output carries no PHI. |
| Agent | An autonomous caller of Tools, driven by a language model. An Agent calls Capabilities. It never spends a billable transaction and never acts on a Recommendation. |
| Audit Ref | The opaque identifier of an Audit Record or a clearinghouse transaction. Each Tool output carries it, so that an Operator can follow a result back to the identified record behind it. It is the only connection from the reasoning of an Agent to PHI, and it resolves only inside the service. |

## Industry standards

These are not Defined Terms. They are a reference. They are the transactions, code sets and
segments that the Core uses, with the names that the industry gives them. The pack of a client
maps the codes of that client onto them.

### Transactions

| Term | Meaning |
|---|---|
| X12 | The EDI standard family in which healthcare transactions are written (ASC X12N). Each transaction has a number. The version in force under HIPAA is 005010. A transaction is a stream of segments, and each segment is a delimited list of elements. |
| 270 / 271 | Eligibility and benefit inquiry, and the response of the payer. It answers "is this patient covered, for what, on this date". |
| 276 / 277 | Claim status inquiry, and the response of the payer. It answers "what happened to this claim". We make the 276 and read the 277. |
| 277CA | Claim acknowledgement. It reports whether a payer *accepted a submitted claim for adjudication*. It is a different transaction from a 277 status response, and people often confuse the two. |
| 835 | Claim payment and advice: the remittance. It gives paid, allowed and adjustment amounts for each claim and each line, with the reasons. It is the only source of adjustment arithmetic. A trace number connects it with the payment itself. |
| 837 | Claim submission. Variants: 837P professional, 837I institutional, 837D dental. |
| 999 | Implementation acknowledgement. It reports whether a transaction was syntactically valid EDI. A rejection here means that the question had an error, not that a claim was denied. |

### Code sets

| Term | Meaning |
|---|---|
| CARC | Claim Adjustment Reason Code. It tells why an amount was adjusted, on an 835. It has no meaning without its group code: `45` alone does not say who bears the amount. |
| RARC | Remittance Advice Remark Code. An additional explanation next to a CARC, carried on the `LQ` segment of the 835. |
| Group code | The two-letter X12 code that says *who bears* an adjusted amount: `CO` contractual obligation, `PR` patient responsibility, `OA` other, `PI` payer-initiated, `CR` correction. `PR` is the only group under which a balance can go to a patient. |
| CSCC | Claim Status Category Code (external code list 507). The coarse outcome on a 277: `F1` finalized/paid, `F2` finalized/denied, `P5` pending, `D0` search unsuccessful. Payers do not apply these codes consistently. |
| CSC | Claim Status Code (external code list 508). The specific reason on a 277. It is more reliable across payers than the category. For this reason, classification uses it first. |
| HCPCS / CPT | Procedure code sets that name the billed service. A claim line carries one, with optional modifiers. |

### Terms and identifiers

| Term | Meaning |
|---|---|
| Adjudication | The decision process of the payer on a claim. It ends in payment, denial or a request for more information. A claim that is not adjudicated has no final answer to interpret. |
| ERA | Electronic Remittance Advice: the 835, under its business name. "ERA enrollment" is the authorization for each payer to receive them. This authorization is on paper and slow much more often than not. |
| EOB | Explanation of Benefits. The remittance that people can read, in the past on paper. The 835 is its electronic equivalent. |
| ICN | Internal Control Number: the identifier of the payer for a claim, different from ours. An appeal or a telephone call must give it. |
| NPI | National Provider Identifier. Ten digits that identify a provider or an organization. A claim carries a billing NPI, and often a rendering NPI. |
| ETIN | Electronic Transmitter Identification Number. An alternative provider identifier that some payers prefer on a status inquiry. |
| TFL | Timely Filing Limit. The window in which a payer accepts a claim, measured from a basis date. The basis date is different for each payer and program. If you miss the limit, there is usually no payment at all. |
| COB | Coordination of Benefits. The rules that decide which payer pays first when a patient has more than one payer, and what the later payers owe. |
| Sequestration | A mandatory percentage reduction on Medicare payments. It is arithmetic, not a denial. Do not treat it as a denial. |

### Segments this repository cites

| Term | Meaning |
|---|---|
| CLP | The 835 loop that carries the payment of one claim: our claim id, a status code, the totals for charged, paid and patient responsibility, and the ICN of the payer. |
| CAS | The 835 adjustment segment: repeating triples of (group code, CARC, amount). This segment decides where the money goes. |
| STC | The 277 status segment. It carries the CSCC/CSC pair, the entity that it concerns, and free text. |
| TRN | Trace number. It connects a response to the request that caused it. On an 835, it connects the advice again with the payment that came with it. |
| REF | A qualified reference identifier. The qualifier tells which kind, for example `EJ` our claim reference, `1K` the ICN of the payer, or `FJ` a line item control number. There are many more. |
| C043 | The composite inside `STC01`: category code (507), status code (508) and entity identifier code (98). The claim status record stores each one as a row of `dm_claim_status_codes`. |
| SVC | The 276/277 service line segment: procedure code and modifiers (`SVC01`), charge (`SVC02`), payment (`SVC03`), revenue code (`SVC04`), units (`SVC07`). |
| DTP\*472 | Service date, as a single date or an `RD8` range. |
| AMT\*T3 | The total claim charge amount on a 276. |

### 276/277 loops the claim status record is named after

| Loop | Carries |
|---|---|
| 2100A | The payer (information source). |
| 2100B / 2100C | The information receiver and the provider of service: our billing and service providers. |
| 2100D / 2100E | The subscriber, and the dependent when the patient is not the subscriber. PHI. |
| 2200D / 2200E | One claim: `TRN` trace, `REF*EJ` / `REF*1K`, and in the 277 the claim-level `STC` with its effective date (`STC02`), charge (`STC04`), payment (`STC05`), adjudication date (`STC06`), check date (`STC08`) and check or EFT number (`STC09`). |
| 2210D / 2220D | One service line, on the 276 and the 277. |
