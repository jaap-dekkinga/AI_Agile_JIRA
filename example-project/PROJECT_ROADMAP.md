# Project Roadmap: Harbor Claims Assistant

> Example content. Harbor Claims Assistant, Harborlight Health and each slice, story, date,
> owner and Jira key on this page are invented. They show the structure of a CDD roadmap, and
> how it is mirrored into Jira. They do not describe a real product or team.

## How to use this file

Status legend: ✅ done (merged on `main`) · 🟡 in progress or partial · ⬜ not started ·
⛔ blocked on an open question · ⏸ deferred by a decision.

IDs: slices are `S1`… and the stories in a slice are `S1-01`…. IDs are stable. Never renumber
them. Add new ids at the end. Give them in commit messages and PR bodies, with the spec rule
ids.

Open questions: work that is blocked on an open question cites it as `Q-NNN`, from
[`docs/platform/open-questions.md`](docs/platform/open-questions.md). A slice that resolves a
question says so. The register gives the owner, so each blocker names the person who can
remove it.

Releases: a release is a named set of slices and stories that ship together. It adds no work
of its own. Each item in it is a story here, and each gap in it is an open question.

### Working in parallel

Many people use this file at the same time. A story is the unit of work: one story, one
pull request, merged to `main` in a few days. There are no slice branches that stay open for a
long time. The team plans work in two-week sprints. A story can be in a sprint only after it is
groomed, at 8 story points or less
([Definition of Ready](docs/agile-practices.md#definition-of-ready)). The sprint meetings and
estimation are in [docs/agile-practices.md](docs/agile-practices.md).

Story columns: a story that is not done has four columns in addition to its status:

- Jira: its Task in Jira, or `—` before the first sync (see [Jira](#jira)).
- Owns: the paths that it makes or changes.
- Needs: the story ids that must merge before it merges. Work can start earlier against the
  contract of a story that it needs. For this reason, the first story of each capability is
  its contract: the spec rules and the types, with no behavior.
- Demo: the Reference UI surface that shows it, or `—`.

Stories that are done keep the shorter `ID | Story | Status | Notes` form.

The ownership rule: two stories in progress never own the same path. If they do, one story
lists the other in its Needs column. A shared file with a registration seam (see
[Shared files](#shared-files)) is the only exception. Each feature adds a single line, so the
merge conflict is always small. A spec file can also be shared. In this case, Owns can name a
rule (`eligibility-012`) and not the full file.

Numbers: take migration numbers, ADR numbers, spec areas, rule ids and question ids from
[Reservations](#reservations) before you use them. The PR that merges first never takes a
number that is not reserved.

### Shared files

Some files change in almost each pull request. Each of these files has a rule, so it does not
cause conflicts.

| Files | Rule |
|---|---|
| `PROJECT_ROADMAP.md`, `spec/INDEX.md`, `spec/glossary.md`, `docs/adr/README.md`, `docs/platform/open-questions.md`, `docs/continuous-improvement.md`, `START_HERE.md`, `CLAUDE.md` | Change them in the PR that needs the change, with its spec, ADR and question files. Thus the rule is still written before the code. Change only the rows that the story owns. |
| `pkg/server/server.go`, `frontend/src/App.tsx`, `frontend/src/components/layout.tsx` | These files are registration seams. Each feature adds one line, and keeps its code in its own file. |
| `pkg/database/migrations/sql/` | The numbers come from [Reservations](#reservations). |

### Reservations

A PR uses only the numbers that are reserved for its story. To take a new number, add a row
here in the PR that needs it, before you use the number.

| Kind | Reserved | For |
|---|---|---|
| Migration | `007` | S6-02: re-status enablement per payer |
| Migration | `008`–`009` | Not assigned. Ask the lead |
| ADR | `0014` | S7-01: queued inquiries hold patient identity only until no further send can use it |
| ADR | `0015` | S9-01: the agent tool surface carries no PHI |
| Spec area | `spec/restatus.md` (`restatus-001`…`008`) | S6-01 writes `001`–`006`, and S6-03 writes `007`–`008` |
| Spec rules | `eligibility-012`–`015` | S5-06 (insurance discovery) |
| Spec rules | `eligibility-016`–`019` | S5-07 (coordination of benefits) |
| Question | `Q-056` · `Q-057` | S7-03 · S9-02 |

### Jira

Jira project [HCA](https://[placeholder].atlassian.net/browse/HCA) tracks this file for the PM.
Its epics are the stations of the operating model for claims follow-up. Each open story here is
one Jira Task under the epic of its station. This file leads, and Jira follows. A story is
written here first, with its spec first. After roadmap changes merge, the lead mirrors them
into Jira.

| Epic | Station | Slices |
|---|---|---|
| HCA-2 Setup & Design | The foundation | S1, S2, S10 |
| HCA-4 Payer Routing | Vendor reachability and fallback | S3, S4 |
| HCA-5 Status Determination | ① The status cascade | S3 |
| HCA-6 Intake & Classify | ② Classify, filing limit first | S8 |
| HCA-7 Verify & Triage | ③ One evidence pass, then the gates | S5 |
| HCA-11 Follow-up & SLA Queue | ⑥ Re-status on the SLA clock | S6, S7 |
| HCA-13 Agent Tools | Tools that an AI agent can call | S9 |

HCA-1, HCA-3 and HCA-9 (milestones, close-out, sign-off) belong to the PM. Nothing here maps to
them.

- Where the key is: each slice names its epic on a `**Jira epic:**` line. Each table of open
  stories has a Jira column, which holds the Task of the story.
- Who owns what: this file owns the summary, the description, the epic, the labels, the
  *blocks* links (from Needs) and the status of a Task. The status only changes to a later status. ⬜, ⛔
  and ⏸ are To Do, 🟡 is In Progress, and ✅ is Done. Jira owns the assignee, sprint, story
  points, dates, priority, rank and comments, and the sync never writes them. Change the
  description of a Task here, not in Jira, because the next sync overwrites it.
- How to do the work of a story: take the Task on the board, and name the branch
  `HCA-123-s6-03-short-name`. Put both ids in the PR title (`… (S6-03, HCA-123)`), and the spec
  rules in its body. Never put a Jira key in `cmd/`, `pkg/`, `spec/`, `docs/` or `frontend/`.
- Work that starts in Jira: the next sync reports each Task under a station epic that has
  neither the label `hca-roadmap` nor the label `not-hca`. The lead writes the story here, spec
  first, with the key of that Task in its Jira column. Or the lead gives the Task the label
  `not-hca`.

---

### S1: Service scaffold ✅

**Jira epic:** HCA-2 (Setup & Design)

Goal: a service that operates, with health checks, migrations, login, tracing and the repository
guards. Thus each later slice only adds a feature.

| ID | Story | Status | Notes |
|---|---|---|---|
| S1-01 | Service skeleton: router, health, version, error envelope | ✅ | `service-001`…`004` |
| S1-02 | Embedded migrations, every object `dm_`-prefixed | ✅ | ADR 0005 |
| S1-03 | Repository guards: no PHI in testdata, no client identifiers in the Core | ✅ | `phi-004`, `service-009` |

---

### S2: Domain vocabulary ✅

**Jira epic:** HCA-2 (Setup & Design)

Goal: the words of the product as types: Money in cents, civil Dates, Payer, Claim, Evidence
and Confidence. Thus no later slice makes its own types.

| ID | Story | Status | Notes |
|---|---|---|---|
| S2-01 | `pkg/rcm` types and the glossary's Defined Terms | ✅ | |

---

### S3: Claim status, end to end ✅

**Jira epic:** HCA-5 (Status Determination)

Goal: ask a payer through one clearinghouse what happened to a claim. Then interpret the
answer as a Disposition, with Evidence.

| ID | Story | Status | Notes |
|---|---|---|---|
| S3-01 | Clearinghouse port and canonical 277 model | ✅ | ADR 0007 |
| S3-02 | First vendor adapter: claim status | ✅ | Proved against production on 2026-09-30 |
| S3-03 | Disposition and Bucket from a Status | ✅ | `disposition-001`…`006` |
| S3-04 | Reference UI: the claim status screen and its Demo Scenarios | ✅ | |

---

### S4: Second vendor and fallback ⛔

**Jira epic:** HCA-4 (Payer Routing)

Goal: get to the payers that the first vendor cannot get to. When the first vendor fails, fall
through to a second vendor.

[`Q-030`](docs/platform/open-questions.md#q-030) asks when a status inquiry must fall through.
Platform owns this question. Until it gets an answer, we assume fallback only on a transport
failure, never on an answer from a payer.

| ID | Jira | Story | Owns | Needs | Demo | Status |
|---|---|---|---|---|---|---|
| S4-01 | HCA-131 | Fallback rules in `spec/clearinghouse.md`, under `Q-030`'s assumption | `spec/clearinghouse.md` (`clearinghouse-032`…`034`) | — | — | ⛔ |
| S4-02 | HCA-132 | Second vendor adapter: claim status | `pkg/clearinghouse/vendorb/` | S4-01 | Claim status | ⬜ |

---

### S5: Eligibility (270/271) 🟡

**Jira epic:** HCA-7 (Verify & Triage)

Goal: ask if the plan of a member is active on a date of service, and what it covers. Do not
keep the identity of the member ([`spec/eligibility.md`](spec/eligibility.md)).

| ID | Jira | Story | Owns | Needs | Demo | Status |
|---|---|---|---|---|---|---|
| S5-01 | — | Eligibility port, canonical 271 model, validation | `spec/eligibility.md` (`001`–`004`) | — | — | ✅ |
| S5-02 | — | Plan status, and a rejected inquiry never reported as inactive | `eligibility-005`, `-006` | S5-01 | Eligibility | ✅ |
| S5-03 | — | Benefit row detail without a person's identity | `eligibility-011` | S5-01 | Eligibility | ✅ |
| S5-04 | HCA-141 | Vendor test mode: the vendor's mock requests offered by name | `eligibility-020`, `frontend/src/pages/eligibility.tsx` | S5-01 | Eligibility | 🟡 |
| S5-05 | HCA-142 | Batch eligibility through the vendor's native batch | `pkg/clearinghouse/eligibility_batch.go` | S7-01 | — | ⬜ |
| S5-06 | HCA-143 | Insurance discovery from demographics | `eligibility-012`…`015` | S5-02 | Eligibility | ⛔ `Q-047` |
| S5-07 | HCA-144 | Coordination of benefits: the other plans of a member, and which plan is primary | `eligibility-016`…`019` | S5-02 | Eligibility | ⬜ |

---

### S6: Scheduled re-status 🟡

**Jira epic:** HCA-11 (Follow-up & SLA Queue)

Goal: get the status of a monitored claim again when its follow-up window starts, without a
person, one payer at a time.

This is a job, not a Capability, because it reads the clock and spends billable calls. We turn
it on one payer at a time ("top connected payers first, measured each time"), separately from
Coverage.

| ID | Jira | Story | Owns | Needs | Demo | Status |
|---|---|---|---|---|---|---|
| S6-01 | — | Due-claim selection as a pure function | `spec/restatus.md` (`001`–`006`), `pkg/restatus/` | — | — | ✅ |
| S6-02 | HCA-152 | The rollout dial: per-payer enablement | migration `007`, `pkg/database/repositories/restatus_repository.go` | S6-01 | — | 🟡 |
| S6-03 | HCA-153 | The re-status job, under a daily ceiling | `restatus-007`, `-008`, `pkg/restatus/job.go` | S6-02, S7-01 | — | ⬜ |
| S6-04 | HCA-154 | Reference UI: claims due for re-status and the last run | `frontend/src/pages/restatus.tsx` | S6-03 | Re-status | ⬜ |

---

### S7: Async submission 🟡

**Jira epic:** HCA-11 (Follow-up & SLA Queue)

Goal: accept many inquiries at the same time and answer them later. Never send an inquiry two
times.

| ID | Jira | Story | Owns | Needs | Demo | Status |
|---|---|---|---|---|---|---|
| S7-01 | HCA-161 | The Batch model and its rules | `spec/batch.md`, ADR 0014 | — | — | 🟡 |
| S7-02 | HCA-162 | The batch runner with a per-vendor concurrency cap | `pkg/clearinghouse/batch/runner.go` | S7-01 | — | ⬜ |
| S7-03 | HCA-163 | Who can read a batch | `Q-056` | S7-01 | — | ⬜ |

---

### S8: Timely-filing capability ✅

**Jira epic:** HCA-6 (Intake & Classify)

Goal: say if a claim is still in the filing window of its payer, and if it needs proof of
timely filing. The limits come from the client pack.

| ID | Story | Status | Notes |
|---|---|---|---|
| S8-01 | Filing window, its anchor, proof of timely filing | ✅ | `timely-filing-001`…`009` |
| S8-02 | Limits from the pack's `lookups/` section | ✅ | `client-packs-009` |

---

### S9: Agent tools ⬜

**Jira epic:** HCA-13 (Agent Tools)

Goal: make the deterministic Capabilities available as Tools that an AI agent can call. No
output has PHI, and each output has an Audit Ref to the record behind it.

| ID | Jira | Story | Owns | Needs | Demo | Status |
|---|---|---|---|---|---|---|
| S9-01 | HCA-171 | The tool envelope and ADR 0015 | `spec/tools.md`, ADR 0015 | — | — | ⬜ |
| S9-02 | HCA-172 | Which agent can call which tool | `Q-057` | S9-01 | — | ⬜ |
| S9-03 | HCA-173 | First tools: Disposition, timely filing | `pkg/tools/` | S9-01 | Tools | ⬜ |

---

### S10: Reference UI 🟡

**Jira epic:** HCA-2 (Setup & Design)

Goal: a demonstration screen for each service over the public API. Thus each sprint demo can
operate live on synthetic data. This is not the product UI, which is in Workbench.

| ID | Jira | Story | Owns | Needs | Demo | Status |
|---|---|---|---|---|---|---|
| S10-01 | — | Shell, navigation and design-system primitives | `frontend/` | — | — | ✅ |
| S10-02 | HCA-181 | Dark mode and print styles | `frontend/src/components/ds/` | S10-01 | All | ⬜ |

---

### Release 1: automated status on connected payers 🟡

S1, S2, S3, S5-01 to S5-03, S6, S7-01 and S7-02, S8.

Two-week targets (fictional):

| Sprint | Goal |
|---|---|
| 2026-10-26 → 11-06 | The rollout dial and the Batch model land. Eligibility test mode is shown at the demo |
| 2026-11-09 → 11-20 | The re-status job operates under its ceiling on two payers |
| 2026-11-23 → 12-04 | Release 1 sign-off |

---

## Decisions & constraints

- Product, not solution: a Core and a client pack, never a fork (ADR 0001).
- Deterministic Core: Capabilities are pure. Probabilistic judgment comes later in the chain
  (ADR 0002).
- Recommend, never act: an action that cannot be undone needs an explicit decision by an
  Operator (ADR 0003).
- The canonical model has the shape of X12. Adapters normalize data into it (ADR 0007).
- Tools carry no PHI, and an agent cannot call transport (ADR 0015, proposed).
- The Reference UI is a demonstration surface over the public API, not the product UI
  (ADR 0013).
- The repository owner commits. Assistants leave changes in the working tree for review.

The full list is in the [decision log](docs/adr/README.md).

## Change log

| Date | Change |
|---|---|
| 2026-09-08 | First roadmap: S1 service scaffold. |
| 2026-09-15 | Added S2–S3: connectivity first, interpretation second. |
| 2026-09-22 | Added S5 (eligibility) and S8 (timely filing). Opened `Q-029`, `Q-030`. |
| 2026-10-01 | `Q-001` resolved, misframed: the claims database moves to a managed PostgreSQL, and its schema does not change. S4 marked ⛔ on `Q-030`. |
| 2026-10-13 | Added S6 (re-status) and S7 (async submission) from the second pass of the operating model. |
| 2026-10-27 | Added S9 (agent tools). Defined Release 1. |
| 2026-11-09 | Added `docs/continuous-improvement.md` to the shared files. Added S5-07 (coordination of benefits), and reserved `eligibility-016`–`019` for it. |
