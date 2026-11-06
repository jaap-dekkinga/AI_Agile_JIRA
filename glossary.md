<!-- spec-meta
id: glossary
last_updated: 2026-09-29
-->

# Glossary

Defined Terms carry these meanings when capitalised anywhere in `spec/`, code comments and
documentation. The product speaks this vocabulary; a client's own words are mapped to it
in the client's pack (see *Client word* below) and never leak into the core.

Industry vocabulary — the X12 transactions and code sets the Core implements — is listed
separately at the end. Those are not Defined Terms: they are the names the industry already
uses, reproduced here so nobody has to leave the repository to read a rule.

> This glossary belongs to **Harbor Claims Assistant**, the fictional example product used
> throughout `example-project/`. The healthcare terms are real industry vocabulary; the
> product, its company and its neighbouring systems are invented.

## Defined Terms

| Term | Meaning |
|---|---|
| **Client** | An organisation the product is deployed and configured for. One deployment serves one Client today; the data model still carries the Client identity so that assumption can change. |
| **Client Pack** | The Client's configuration bundle: payer mappings, state rules, decision-table rows and thresholds, SOP playbooks, follow-up windows, reference codes. Loaded at startup, validated as a whole, versioned. Everything Client-specific lives here and nowhere else. |
| **Core** | The product code and the industry-standard data compiled into it: X12 grammars, CARC/RARC meanings, arithmetic and classification engines, the service. The Core contains no Client identifiers. |
| **Claim** | A billed encounter as the Client's practice-management system knows it, identified by the Client's claim identifier. Carries lines, payer, dates of service and balances. |
| **Payer** | The insurer or program a Claim was billed to, identified canonically (name, type, state, program). A Client's own payer code is mapped to the canonical Payer by its pack. |
| **PMS** | The Client's practice-management / billing system of record (the source of Claims and the destination of notes). Named generically; the specific system is a pack and adapter concern. |
| **Remit** | An 835 remittance advice: per-line paid/allowed amounts and adjustments (`{group, CARC, amount}`), plus RARCs. |
| **Status** | A 277 claim-status response tuple (category code 507, status code 508, entity, free text) for a Claim. Classification keys on the status code first: Payers do not apply category codes consistently, so the category decides only whether a Claim has adjudicated. |
| **Disposition** | The Core's coarse outcome for a Status: one of `ACCEPTED`, `FINALIZED_PAYMENT`, `FINALIZED_DENIAL`, `PENDING`, `REQUEST_INFO`, `ERROR`. Derived from the category code (507) alone, because that is the element X12 defines as whether a Claim has adjudicated. A closed set; an unmapped code is `ERROR`, never a guess. Not a Client's *disposition code* — see Outcome Code. |
| **Bucket** | The operator-facing classification of a Status — an id, a label and a tone. Unlike a Disposition it keys on the status code (508) first, because the same outcome reaches us under different category letters from different Payers. The id is Core vocabulary; the label is pack data. |
| **Outcome Code** | A Client's own code for how a worked Claim was left — the action taken or the state found (a resubmission, an escalation, a write-off, a patient balance, a hold to monitor) — together with the follow-up window it carries. Clients often call these *disposition codes* or *action status codes*; they are not a Disposition. A Disposition is the Core's closed reading of a Status; an Outcome Code is Client vocabulary, depends on what was done as well as what the Payer said, and lives in the Client Pack. A Recommendation may name one. |
| **Capability** | A deterministic function of the Core (e.g. CARC interpretation, timely-filing computation) exposed as a tool. Capabilities take their rule data from the Client Pack. |
| **Playbook** | The steps an Operator follows to work a path: numbered steps, the branches each may take on what the Operator finds, and notes. Client Pack data (`client-packs-013`); a branch's label is not an Outcome Code. |
| **SOP** | A Client's standard operating procedure document, carried in the Client Pack section by section and cited by section from a table row (`client-packs-012`). |
| **Recommendation** | A Capability's proposed next action for a Claim, with a path or playbook, a *why* sentence, Evidence and Confidence. A Recommendation is never acted on by the system. |
| **Evidence** | The list of `{source, ref, detail}` records explaining a Recommendation: which rule, which segment, which pack file. Every Capability output carries Evidence. |
| **Confidence** | A number in [0, 1] every Capability output carries. Precision over recall: no matching rule yields *no* Recommendation, never a low-confidence guess presented as one. |
| **Audit Record** | The append-only record of one Capability call: actor, tool, PHI-redacted inputs and outputs, Evidence, Confidence, time. |
| **Operator** | A human user of the Client who reviews Recommendations. |
| **Demo Mode** | The service running without OAuth; every request acts as the synthetic Demo User `demo@example.com`. |
| **Trusted-network mode** | The service running without a login on a private network that only one trusted caller can reach. Every request acts as that caller, and a user the caller names in `X-Acting-User` is recorded as asserted, never verified (`service-011`). Unlike Demo Mode, it may serve Client data. |
| **Demo Scenario** | A synthetic inquiry the in-memory fake clearinghouse answers with a scripted result (paid, denied, pending, rejected) when no vendor is configured, keyed by a reserved payer identifier. Exists so the product can be demonstrated; never a payer's answer. |
| **Reference UI** | The demonstration and developer UI in `frontend/`, served by the binary and built only on the public API. Not the product UI, which is built in Workbench, and not an Operator surface. |
| **Workbench** | The fictional company's operator application, where the product UI lives. A neighbouring system, not part of this product. |
| **Client word** | A Client's term for a product concept (for example a Client may call a Claim an "invoice"). Client words appear only in that Client's pack — as labels, template text and code mappings — and are rendered to Operators of that Client. Core code, specs and APIs use the product term. |
| **Clearinghouse** | A vendor that carries X12 transactions between providers and Payers. The product reaches Payers only through one. |
| **Product Vendor** | A Clearinghouse or data service the company itself contracts with: the same for every Client of a deployment, the company holds the credentials, and its adapter is Core code that may name it. Contrast a Client's own vendors, which stay in that Client's pack. |
| **Port** | A Core-defined interface to a system outside this service, with one adapter per system and an in-memory fake for tests and Demo Mode. A Port may perform network I/O and read the clock; a Capability may not. |
| **Transaction Type** | An X12 exchange the product performs with a Payer: claim status (276/277), eligibility (270/271), claim submission (837), remittance (835). |
| **Coverage** | Whether a Product Vendor can reach a given Payer for a given Transaction Type, and whether that requires Enrollment. Declared per (Payer, Transaction Type) pair. |
| **Plan** | The member's insurance as a Payer reports it in a 271: plan name and group, insurance type, coverage level and the plan's dates. Never called "coverage", which means vendor reachability (above). |
| **Plan Status** | `ACTIVE`, `INACTIVE` or `UNKNOWN`, read from a 271's benefit code for the service types asked about (`eligibility-005`). A rejected eligibility inquiry has none. |
| **Enrollment** | A Payer's authorisation for a specific Transaction Type through a specific Clearinghouse. It is the product's own knowledge, recorded by an Operator, and a Coverage sync never clears it. |
| **Re-status** | A claim status inquiry the product sends on its own schedule, without a person asking, to re-check a Claim whose follow-up window has passed. Sent by a job, not a Capability, because it reads the clock and spends billable calls, and only for a Payer turned on for it, one Payer at a time and apart from Coverage and Enrollment (`restatus-001`). An inquiry a person makes is not a Re-status, even when it re-checks a Claim. |
| **Transport Outcome** | The vendor-neutral classification of what happened on the wire, independent of what the Payer said about any Claim. It answers whether a call may be retried; a Status cannot. |
| **Batch** | Many inquiries of one transaction, handed over at once and answered later, by Workbench through the API, by an Operator from a file, or by the re-status job. How calls travel, not how Claims are worked: claim status fans out through the router, and eligibility goes in a vendor's native batch where there is one (`spec/batch.md`). |
| **Batch Item** | One inquiry in a Batch. It holds the patient's identity only while a later send can use it (`batch-006`). |
| **Vendor Batch** | One native submission to a vendor, holding Batch Items of one or more Batches, made under a name the vendor refuses to run twice (`batch-015`). |
| **Unresolved** | A Batch Item that may have been sent and whose answer is not known. It is never resent, because a second send could be billed twice, and it is not a failure, because the Payer may have answered (`batch-007`). |
| **Tool** | A Capability exposed to an external caller through the tool surface, with a stable name, a versioned schema and the standard envelope. A Tool output carries no PHI. |
| **Agent** | An autonomous, language-model-driven caller of Tools. An Agent calls Capabilities; it never spends a billable transaction and never acts on a Recommendation. |
| **Audit Ref** | The opaque identifier of an Audit Record or a clearinghouse transaction, carried on every Tool output so an Operator can follow a result back to the identified record behind it. It is the only bridge from an Agent's reasoning to PHI, and resolves only inside the service. |

## Industry standards

Not Defined Terms — reference. These are the transactions, code sets and segments the Core
speaks, named as the industry names them. A client's own codes are mapped onto these by
that client's pack.

### Transactions

| Term | Meaning |
|---|---|
| **X12** | The EDI standard family healthcare transactions are written in (ASC X12N). Each transaction has a number; the version in force under HIPAA is 005010. A transaction is a stream of segments, each a delimited list of elements. |
| **270 / 271** | Eligibility and benefit inquiry, and the payer's response. Answers "is this patient covered, for what, on this date". |
| **276 / 277** | Claim status inquiry, and the payer's response. Answers "what happened to this claim". We generate the 276 and consume the 277. |
| **277CA** | Claim acknowledgement. Reports whether a payer *accepted a submitted claim for adjudication* — a different transaction from a 277 status response, and easily confused with one. |
| **835** | Claim payment/advice: the remittance. Per-claim and per-line paid, allowed and adjustment amounts, with the reasons. The only source of adjustment arithmetic. Paired with the payment itself through a trace number. |
| **837** | Claim submission. Variants: 837P professional, 837I institutional, 837D dental. |
| **999** | Implementation acknowledgement. Reports whether a transaction was syntactically valid EDI — a rejection here means the question was malformed, not that a claim was denied. |

### Code sets

| Term | Meaning |
|---|---|
| **CARC** | Claim Adjustment Reason Code. Why an amount was adjusted, on an 835. Meaningless without its group code: `45` alone does not say who bears the amount. |
| **RARC** | Remittance Advice Remark Code. Supplementary explanation alongside a CARC, carried on the 835's `LQ` segment. |
| **Group code** | The two-letter X12 code saying *who bears* an adjusted amount: `CO` contractual obligation, `PR` patient responsibility, `OA` other, `PI` payer-initiated, `CR` correction. `PR` is the only group under which a balance may be transferred to a patient. |
| **CSCC** | Claim Status Category Code (external code list 507). The coarse outcome on a 277 — `F1` finalised/paid, `F2` finalised/denied, `P5` pending, `D0` search unsuccessful. Payers do not apply these consistently. |
| **CSC** | Claim Status Code (external code list 508). The specific reason on a 277. More reliable across payers than the category, and therefore what classification keys on first. |
| **HCPCS / CPT** | Procedure code sets naming the service billed. A claim line carries one, optionally with modifiers. |

### Terms and identifiers

| Term | Meaning |
|---|---|
| **Adjudication** | The payer's decision process on a claim, ending in payment, denial or a request for more information. A claim that has not adjudicated has no final answer to interpret. |
| **ERA** | Electronic Remittance Advice — the 835, referred to by its business name. "ERA enrolment" is the per-payer authorisation to receive them, which is paper-based and slow far more often than it is not. |
| **EOB** | Explanation of Benefits. The human-readable remittance, historically on paper. The 835 is its electronic equivalent. |
| **ICN** | Internal Control Number — the payer's own identifier for a claim, distinct from ours. What an appeal or a phone call has to quote. |
| **NPI** | National Provider Identifier. Ten digits identifying a provider or organisation; a claim carries a billing NPI and often a rendering one. |
| **ETIN** | Electronic Transmitter Identification Number. An alternative provider identifier some payers prefer on a status inquiry. |
| **TFL** | Timely Filing Limit. The window in which a payer will accept a claim, measured from a basis date that varies by payer and programme. Missing it usually forecloses payment entirely. |
| **COB** | Coordination of Benefits. The rules deciding which payer pays first when a patient has more than one, and what the later payers owe. |
| **Sequestration** | A mandatory percentage reduction applied to Medicare payments. Arithmetic, not a denial, and must not be treated as one. |

### Segments this repository cites

| Term | Meaning |
|---|---|
| **CLP** | The 835 loop carrying one claim's payment: our claim id, a status code, charged, paid and patient-responsibility totals, and the payer's ICN. |
| **CAS** | The 835 adjustment segment: repeating triples of (group code, CARC, amount). Where the money actually goes is decided here. |
| **STC** | The 277 status segment, carrying the CSCC/CSC pair, the entity it concerns, and free text. |
| **TRN** | Trace number. Correlates a response to the request that caused it, and on an 835 reassociates the advice with the payment that accompanied it. |
| **REF** | A qualified reference identifier. The qualifier says which kind — `EJ` our claim reference, `1K` the payer's ICN, `FJ` a line item control number, among many. |
| **C043** | The composite inside `STC01`: category code (507), status code (508) and entity identifier code (98). The claim status record stores each one as a row of `dm_claim_status_codes`. |
| **SVC** | The 276/277 service line segment: procedure code and modifiers (`SVC01`), charge (`SVC02`), payment (`SVC03`), revenue code (`SVC04`), units (`SVC07`). |
| **DTP\*472** | Service date, as a single date or an `RD8` range. |
| **AMT\*T3** | The total claim charge amount on a 276. |

### 276/277 loops the claim status record is named after

| Loop | Carries |
|---|---|
| **2100A** | The payer (information source). |
| **2100B / 2100C** | The information receiver and the provider of service: our billing and service providers. |
| **2100D / 2100E** | The subscriber, and the dependent when the patient is not the subscriber. PHI. |
| **2200D / 2200E** | One claim: `TRN` trace, `REF*EJ` / `REF*1K`, and in the 277 the claim-level `STC` with its effective date (`STC02`), charge (`STC04`), payment (`STC05`), adjudication date (`STC06`), check date (`STC08`) and check or EFT number (`STC09`). |
| **2210D / 2220D** | One service line, on the 276 and the 277 respectively. |
