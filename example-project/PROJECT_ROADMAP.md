# Project Roadmap — Harbor Claims Assistant

> **Example content.** Harbor Claims Assistant, Harborlight Health and every slice, story,
> date, owner and Jira key below are invented. They show how a CDD roadmap is structured and
> how it is mirrored into Jira; they do not describe a real product or team.

## How to use this file

**Status legend:** ✅ done (merged on `main`) · 🟡 in progress / partial · ⬜ not started ·
⛔ blocked on an open question · ⏸ deferred by decision.

**IDs.** Slices are `S1`…; stories within a slice are `S1-01`…. IDs are stable — never
renumber; append. Reference them in commit messages and PR bodies alongside spec rule IDs.

**Open questions.** Work that is blocked on an unresolved question cites it as `Q-NNN`, from
[`docs/platform/open-questions.md`](docs/platform/open-questions.md). A slice that resolves
one says so. The register carries the owner, so a blockage names who can clear it.

**Releases.** A release is a named set of slices and stories that ships together. It adds no
work of its own: every item in it is a story here, and every gap in it is an open question.

### Working in parallel

Several people work from this file at once. A story is the unit of work: one story, one
pull request, merged to `main` within a few days. There are no long-lived slice branches.
Work is planned in two-week sprints, and a story enters a sprint only once it is refined, at 8
story points or fewer ([Definition of Ready](docs/agile-practices.md#definition-of-ready)).
The sprint meetings and estimation are in [docs/agile-practices.md](docs/agile-practices.md).

**Story columns.** A story that is not yet done carries four columns beyond its status:
- **Jira**: its Task in Jira, or `—` before the first sync (see [Jira](#jira)).
- **Owns**: the paths it creates or changes.
- **Needs**: the story ids that must merge before it merges. Work may start earlier against
  the contract of a story it needs. That is why each capability's first story is its
  contract: the spec rules and the types, with no behaviour.
- **Demo**: the Reference UI surface that shows it, or `—`.

Landed stories keep the shorter `ID | Story | Status | Notes` form.

**The ownership rule.** Two stories in flight never own the same path. If they would, one
lists the other under **Needs**. A shared file with a registration seam (see
[Shared files](#shared-files)) is the one exception: each feature adds a single line, and such
a merge conflict is trivial by construction. A spec file may also be shared: **Owns** may name a
rule (`eligibility-012`) rather than the whole file.

**Numbers.** Migration numbers, ADR numbers, spec areas and rule ids, and question ids are
taken from [Reservations](#reservations) before use. They are never taken by whichever PR
merges first.

### Shared files

A few files change in almost every pull request. Each has a rule, so it stops being a
collision point.

| Files | Rule |
|---|---|
| `PROJECT_ROADMAP.md`, `spec/INDEX.md`, `spec/glossary.md`, `docs/adr/README.md`, `docs/platform/open-questions.md`, `START_HERE.md`, `CLAUDE.md` | **Changed in the PR that needs the change**, beside its spec, ADR and question files, so the rule is still written before the code. Keep each edit to the rows the story owns. |
| `pkg/server/server.go`, `frontend/src/App.tsx`, `frontend/src/components/layout.tsx` | **Registration seams.** Each feature adds one line and keeps its code in its own file. |
| `pkg/database/migrations/sql/` | Numbers come from [Reservations](#reservations). |

### Reservations

A PR uses only the numbers reserved for its story. To take a new number, add a row here in
the PR that needs it, before the number is used.

| Kind | Reserved | For |
|---|---|---|
| Migration | `007` | S6-02: re-status enablement per payer |
| Migration | `008`–`009` | Unassigned; ask the lead |
| ADR | `0014` | S7-01: queued inquiries hold patient identity only until no further send can use it |
| ADR | `0015` | S9-01: the agent tool surface carries no PHI |
| Spec area | `spec/restatus.md` (`restatus-001`…`008`) | S6-01 writes `001`–`006`; S6-03 `007`–`008` |
| Spec rules | `eligibility-012`–`015` | S5-06 (insurance discovery) |
| Question | `Q-056` · `Q-057` | S7-03 · S9-02 |

### Jira

Jira project [HCA](https://[placeholder].atlassian.net/browse/HCA) tracks this file for the
PM. Its epics are the stations of the claims follow-up operating model, and each open story
here is one Jira Task under its station's epic. This file leads and Jira follows. A story is
written here first, spec first. The lead then mirrors it into Jira after roadmap changes
merge.

| Epic | Station | Slices |
|---|---|---|
| HCA-2 Setup & Design | The foundation | S1, S2, S10 |
| HCA-4 Payer Routing | Vendor reachability and fallback | S3, S4 |
| HCA-5 Status Determination | ① The status cascade | S3 |
| HCA-6 Intake & Classify | ② Classify, filing limit first | S8 |
| HCA-7 Verify & Triage | ③ One evidence pass, then the gates | S5 |
| HCA-11 Follow-up & SLA Queue | ⑥ Re-status on the SLA clock | S6, S7 |
| HCA-13 Agent Tools | Tools an AI agent may call | S9 |

HCA-1, HCA-3 and HCA-9 (milestones, close-out, sign-off) belong to the PM. Nothing here
maps to them.

- **Where the key lives.** Each slice names its epic on a `**Jira epic:**` line. Each
  open-story table has a **Jira** column, which holds the story's Task.
- **Who owns what.** This file owns a Task's summary, description, epic, labels, its
  *blocks* links (taken from **Needs**) and its status. Status only moves forward: ⬜, ⛔
  and ⏸ are To Do, 🟡 is In Progress, ✅ is Done. Jira owns the assignee, sprint, story
  points, dates, priority, rank and comments, and the sync never writes them. Edit a Task's
  description here, not in Jira, because the next sync overwrites it.
- **Working a story.** Take the Task on the board and name the branch
  `HCA-123-s6-03-short-name`. Put both ids in the PR title (`… (S6-03, HCA-123)`) and the spec
  rules in its body. Never put a Jira key in `cmd/`, `pkg/`, `spec/`, `docs/` or `frontend/`.
- **Work that starts in Jira.** The next sync reports any Task under a station epic that
  carries neither `hca-roadmap` nor `not-hca`. The lead either writes the story here, spec
  first, with that Task's key in its **Jira** column, or labels the Task `not-hca`.

---

### S1 — Service scaffold ✅

**Jira epic:** HCA-2 (Setup & Design)

**Goal:** a running service with health checks, migrations, login, tracing and the repository
guards, so every later slice only adds a feature.

| ID | Story | Status | Notes |
|---|---|---|---|
| S1-01 | Service skeleton: router, health, version, error envelope | ✅ | `service-001`…`004` |
| S1-02 | Embedded migrations, every object `dm_`-prefixed | ✅ | ADR 0005 |
| S1-03 | Repository guards: no PHI in testdata, no client identifiers in the Core | ✅ | `phi-004`, `service-009` |

---

### S2 — Domain vocabulary ✅

**Jira epic:** HCA-2 (Setup & Design)

**Goal:** the product's words as types: Money in cents, civil Dates, Payer, Claim, Evidence and
Confidence, so no later slice invents its own.

| ID | Story | Status | Notes |
|---|---|---|---|
| S2-01 | `pkg/rcm` types and the glossary's Defined Terms | ✅ | |

---

### S3 — Claim status, end to end ✅

**Jira epic:** HCA-5 (Status Determination)

**Goal:** ask a payer what happened to a claim through one clearinghouse, and interpret the
answer into a Disposition, with Evidence.

| ID | Story | Status | Notes |
|---|---|---|---|
| S3-01 | Clearinghouse port and canonical 277 model | ✅ | ADR 0007 |
| S3-02 | First vendor adapter: claim status | ✅ | Verified against production on 2026-09-30 |
| S3-03 | Disposition and Bucket from a Status | ✅ | `disposition-001`…`006` |
| S3-04 | Reference UI: the claim status screen and its Demo Scenarios | ✅ | |

---

### S4 — Second vendor and fallback ⛔

**Jira epic:** HCA-4 (Payer Routing)

**Goal:** reach payers the first vendor cannot, and fall through to a second vendor when the
first fails.

When a status inquiry should fall through is [`Q-030`](docs/platform/open-questions.md#q-030),
which Platform owns. Until it is answered we assume fallback only on a transport failure, never
on a payer's answer.

| ID | Jira | Story | Owns | Needs | Demo | Status |
|---|---|---|---|---|---|---|
| S4-01 | HCA-131 | Fallback rules in `spec/clearinghouse.md`, under `Q-030`'s assumption | `spec/clearinghouse.md` (`clearinghouse-032`…`034`) | — | — | ⛔ |
| S4-02 | HCA-132 | Second vendor adapter: claim status | `pkg/clearinghouse/vendorb/` | S4-01 | Claim status | ⬜ |

---

### S5 — Eligibility (270/271) 🟡

**Jira epic:** HCA-7 (Verify & Triage)

**Goal:** ask whether a member's plan is active on a date of service, and what it covers,
without keeping the member's identity ([`spec/eligibility.md`](spec/eligibility.md)).

| ID | Jira | Story | Owns | Needs | Demo | Status |
|---|---|---|---|---|---|---|
| S5-01 | — | Eligibility port, canonical 271 model, validation | `spec/eligibility.md` (`001`–`004`) | — | — | ✅ |
| S5-02 | — | Plan status, and a rejected inquiry never reported as inactive | `eligibility-005`, `-006` | S5-01 | Eligibility | ✅ |
| S5-03 | — | Benefit row detail without a person's identity | `eligibility-011` | S5-01 | Eligibility | ✅ |
| S5-04 | HCA-141 | Vendor test mode: the vendor's mock requests offered by name | `eligibility-020`, `frontend/src/pages/eligibility.tsx` | S5-01 | Eligibility | 🟡 |
| S5-05 | HCA-142 | Batch eligibility through the vendor's native batch | `pkg/clearinghouse/eligibility_batch.go` | S7-01 | — | ⬜ |
| S5-06 | HCA-143 | Insurance discovery from demographics | `eligibility-012`…`015` | S5-02 | Eligibility | ⛔ `Q-047` |

---

### S6 — Scheduled re-status 🟡

**Jira epic:** HCA-11 (Follow-up & SLA Queue)

**Goal:** re-check a monitored claim's status when its follow-up window fires, without a
person, one payer at a time.

A job, not a Capability, because it reads the clock and spends billable calls. It is turned on
payer by payer ("top connected payers first, measured each time"), separately from Coverage.

| ID | Jira | Story | Owns | Needs | Demo | Status |
|---|---|---|---|---|---|---|
| S6-01 | — | Due-claim selection as a pure function | `spec/restatus.md` (`001`–`006`), `pkg/restatus/` | — | — | ✅ |
| S6-02 | HCA-152 | The rollout dial: per-payer enablement | migration `007`, `pkg/database/repositories/restatus_repository.go` | S6-01 | — | 🟡 |
| S6-03 | HCA-153 | The re-status job, under a daily ceiling | `restatus-007`, `-008`, `pkg/restatus/job.go` | S6-02, S7-01 | — | ⬜ |
| S6-04 | HCA-154 | Reference UI: claims due for re-status and the last run | `frontend/src/pages/restatus.tsx` | S6-03 | Re-status | ⬜ |

---

### S7 — Async submission 🟡

**Jira epic:** HCA-11 (Follow-up & SLA Queue)

**Goal:** accept many inquiries at once and answer them later, without ever sending one twice.

| ID | Jira | Story | Owns | Needs | Demo | Status |
|---|---|---|---|---|---|---|
| S7-01 | HCA-161 | The Batch model and its rules | `spec/batch.md`, ADR 0014 | — | — | 🟡 |
| S7-02 | HCA-162 | The batch runner with a per-vendor concurrency cap | `pkg/clearinghouse/batch/runner.go` | S7-01 | — | ⬜ |
| S7-03 | HCA-163 | Who may read a batch | `Q-056` | S7-01 | — | ⬜ |

---

### S8 — Timely-filing capability ✅

**Jira epic:** HCA-6 (Intake & Classify)

**Goal:** say whether a claim is still inside its payer's filing window, and whether proof of
timely filing is needed, from limits carried in the client pack.

| ID | Story | Status | Notes |
|---|---|---|---|
| S8-01 | Filing window, its anchor, proof of timely filing | ✅ | `timely-filing-001`…`009` |
| S8-02 | Limits from the pack's `lookups/` section | ✅ | `client-packs-009` |

---

### S9 — Agent tools ⬜

**Jira epic:** HCA-13 (Agent Tools)

**Goal:** expose the deterministic Capabilities as Tools an AI agent may call, with no PHI in
any output and an Audit Ref back to the record behind each one.

| ID | Jira | Story | Owns | Needs | Demo | Status |
|---|---|---|---|---|---|---|
| S9-01 | HCA-171 | The tool envelope and ADR 0015 | `spec/tools.md`, ADR 0015 | — | — | ⬜ |
| S9-02 | HCA-172 | Which agent may call which tool | `Q-057` | S9-01 | — | ⬜ |
| S9-03 | HCA-173 | First tools: Disposition, timely filing | `pkg/tools/` | S9-01 | Tools | ⬜ |

---

### S10 — Reference UI 🟡

**Jira epic:** HCA-2 (Setup & Design)

**Goal:** a demonstration screen per service over the public API, so every sprint demo can run
live on synthetic data. Not the product UI, which lives in Workbench.

| ID | Jira | Story | Owns | Needs | Demo | Status |
|---|---|---|---|---|---|---|
| S10-01 | — | Shell, navigation and design-system primitives | `frontend/` | — | — | ✅ |
| S10-02 | HCA-181 | Dark mode and print styles | `frontend/src/components/ds/` | S10-01 | All | ⬜ |

---

### Release 1 — automated status on connected payers 🟡

S1, S2, S3, S5-01 to S5-03, S6, S7-01 and S7-02, S8.

**Two-week targets** (fictional):

| Sprint | Goal |
|---|---|
| 2026-10-26 → 11-06 | The rollout dial and the Batch model land; eligibility test mode demoed |
| 2026-11-09 → 11-20 | The re-status job runs under its ceiling on two payers |
| 2026-11-23 → 12-04 | Release 1 sign-off |

---

## Decisions & constraints

- **Product, not solution.** Core plus client pack, never a fork — ADR 0001.
- **Deterministic Core.** Capabilities are pure; probabilistic judgement lives downstream — ADR 0002.
- **Recommend, never act.** Irreversible actions need an Operator's explicit decision — ADR 0003.
- **The canonical model is X12-shaped; adapters normalise inward** — ADR 0007.
- **Tools carry no PHI, transport is not agent-callable** — ADR 0015 (proposed).
- **The Reference UI is a demonstration surface over the public API, not the product UI** — ADR 0013.
- The repository owner commits; assistants leave changes in the working tree for review.

The full list is in the [decision log](docs/adr/README.md).

## Change log

| Date | Change |
|---|---|
| 2026-09-08 | Initial roadmap: S1 service scaffold. |
| 2026-09-15 | Added S2–S3; connectivity first, interpretation second. |
| 2026-09-22 | Added S5 (eligibility) and S8 (timely filing). Opened `Q-029`, `Q-030`. |
| 2026-10-01 | `Q-001` resolved, misframed: the claims database moves to a managed PostgreSQL with its schema intact. S4 marked ⛔ on `Q-030`. |
| 2026-10-13 | Added S6 (re-status) and S7 (async submission) from the operating model's second pass. |
| 2026-10-27 | Added S9 (agent tools). Release 1 defined. |
