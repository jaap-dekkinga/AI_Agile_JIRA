# CLAUDE.md — Harbor Claims Assistant (example)

Guidance for AI coding assistants working in this repository.

> **Example content.** This is the assistant-conventions file of the fictional product
> described in [START_HERE.md](START_HERE.md). It shows what a CDD project tells an AI
> assistant: where the context lives, which conventions are enforced by tests, and how work
> is tied back to roadmap stories and Jira. Module paths and commands are illustrative.

## What this is

A **product**, not a client solution: deterministic claim-status and denial recommendations
(engines and industry standards in the Core) configured per client through a **client pack**
(`clients/<client>/`). `spec/glossary.md` fixes the vocabulary (Claim, Payer, PMS, Client Pack,
Recommendation, Evidence, Confidence). `PROJECT_ROADMAP.md` says which slice is in progress.

The repository follows **Context Driven Development**
(`docs/context-driven-development.md`): questions, decisions, terms and rules are written
down before code, and code and tests cite them. `START_HERE.md` maps every document.

## Tech stack

- Go (version pinned in `go.mod`), module `github.com/[placeholder]/harbor-claims-assistant`
- `github.com/go-chi/chi/v5`, `github.com/spf13/cobra`, `github.com/lib/pq` (PostgreSQL only)
- Tests: stdlib `testing` + `pkg/testutil`. **No testify.**
- Reference UI: Vite + React + TypeScript + Tailwind

## Commands

```bash
make build    # ./bin/claims-assistant
make test     # go test -race ./... (DB tests skip without TEST_DATABASE_URL)
make check    # fmt-check + vet + test — run before handing work over
```

## Conventions

- **No client identifiers in the Core** (`cmd/`, `pkg/`, `spec/`, `docs/`, `frontend/`): no client
  names, systems, screens, SOP section numbers or payer codes. `TestNoClientIdentifiersInCore`
  fails the build otherwise. Product vocabulary everywhere; client words only in packs.
- **Spec first.** A behaviour change edits or adds a rule in `spec/<area>.md` (stable
  `area-NNN` id, never renumbered) and the test cites it: `// SPEC: spec/eligibility.md#eligibility-006`.
- Engines and capability packages are pure: no I/O except through injected sources, **no
  `time.Now()`** — callers pass the clock. Every capability output carries Evidence + Confidence.
- **Transport is not a capability.** Clearinghouse adapters may do network I/O and read the
  clock; they are ports. Interpreting a status is a capability and must not.
- **Never conflate a rejected inquiry with a denied claim.**
- Raw payer payloads are PHI: never a log line, a span attribute, an API response or a
  committed fixture.
- Precision over recall: no rule ⇒ no recommendation, never a guess.
- Fixtures are synthetic (`PAYER-A`, `CLM-0001`, `LASTA`/`FIRSTA`, no DOB);
  `TestNoPHIInTestdata` enforces the patterns.
- **Secrets never enter git, a log or a transcript.** API keys live in the environment or
  git-ignored files. Never `cat` a file that may hold a key.

## Adding things

- **A spec area**: `spec/<area>.md`, add it to `spec/INDEX.md`.
- **A decision**: `docs/adr/NNNN-title.md`, add it to `docs/adr/README.md`.
- **An open question**: next `Q-NNN` in `docs/platform/open-questions.md` — a table row plus a
  section carrying owner, what it blocks, options, what would settle it, and what we assume in
  its absence. Ids are stable; a duplicate is closed, never deleted. Add it to "Blocking now"
  only if it stops work today.
- **An improvement**: next `CI-NNN` in `docs/continuous-improvement.md`, a table row plus a
  section with source, owner, experiment, measure and review sprint. At most three are Trying.
  The `continuous-improvement` skill (`.claude/skills/`) adds, reviews and closes items.
- **Anything client-specific**: it goes in a client pack, not here.

## Commit and PR conventions

- The repository owner commits; assistants leave changes in the working tree for review.
- Commit subject in imperative mood; body explains what and why; reference spec rule IDs and
  roadmap slice IDs.
- **Jira issue keys use the `HCA` prefix** (`HCA-123`). Each open roadmap story has one Task,
  under its operating-model station's epic. Its key is in the story's **Jira** column
  (`PROJECT_ROADMAP.md#jira`).
  - Name the branch `HCA-123-s6-03-short-name`, and put both ids in the PR title
    (`… (S6-03, HCA-123)`).
  - Cite the key in the commit body and the PR description, alongside the spec rule and slice
    IDs.
  - Never cite it in `cmd/`, `pkg/`, `spec/`, `docs/` or `frontend/`, where
    `TestNoClientIdentifiersInCore` runs.
  - Change a story in the roadmap, never in Jira; the lead mirrors the roadmap into Jira after
    roadmap changes merge.
- PR body: `## What?` / `## Why?` / `## Details`.
