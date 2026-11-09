# CLAUDE.md: Harbor Claims Assistant (example)

Instructions for AI coding assistants that do work in this repository.

> Example content. This file gives the assistant conventions of the fictional product that
> [START_HERE.md](START_HERE.md) describes. It shows what a CDD project tells an AI assistant:
> where the context is, which conventions the tests enforce, and how each change connects to
> roadmap stories and Jira. The module paths and the commands are examples only.

## What this is

Harbor Claims Assistant is a product, not a solution for one client. It gives deterministic
recommendations for claim status and denials. The engines and the industry standards are in
the Core. A client pack (`clients/<client>/`) holds the configuration for each client.
`spec/glossary.md` sets the vocabulary (Claim, Payer, PMS, Client Pack, Recommendation,
Evidence, Confidence). `PROJECT_ROADMAP.md` shows which slice is in progress.

The repository uses Context Driven Development (`docs/context-driven-development.md`). The team
writes down questions, decisions, terms and rules before the code. Then the code and the tests
cite them. `START_HERE.md` gives a map of all documents.

## Tech stack

- Go (the version is pinned in `go.mod`), module `github.com/[placeholder]/harbor-claims-assistant`
- `github.com/go-chi/chi/v5`, `github.com/spf13/cobra`, `github.com/lib/pq` (PostgreSQL only)
- Tests: stdlib `testing` + `pkg/testutil`. Do not use testify.
- Reference UI: Vite + React + TypeScript + Tailwind

## Commands

```bash
make build    # ./bin/claims-assistant
make test     # go test -race ./... (DB tests skip without TEST_DATABASE_URL)
make check    # fmt-check + vet + test — run before handing work over
```

Start `make check` before you give your work to the owner.

## Conventions

- Do not put client identifiers in the Core (`cmd/`, `pkg/`, `spec/`, `docs/`, `frontend/`). This
  includes client names, systems, screens, SOP section numbers and payer codes.
  `TestNoClientIdentifiersInCore` stops the build if it finds one. Use product vocabulary
  everywhere. Client words go only in client packs.
- Write the spec first. A change in behavior adds or changes a rule in `spec/<area>.md`, with a
  stable `area-NNN` id that is never renumbered. The test cites the rule:
  `// SPEC: spec/eligibility.md#eligibility-006`.
- Engines and capability packages are pure. They do no I/O, except through sources that the
  caller injects. They do not call `time.Now()`, because the caller gives the clock. Each
  capability output has Evidence and Confidence.
- Transport is not a capability. Clearinghouse adapters are ports, so they can do network I/O
  and read the clock. To interpret a status is a capability, so that code must not do these
  things.
- A rejected inquiry is not a denied claim. Do not mix the two.
- Raw payer payloads are PHI. Never put them in a log line, a span attribute, an API response
  or a committed fixture.
- Precision is more important than recall. If no rule applies, give no recommendation. Never
  guess.
- Fixtures are synthetic (`PAYER-A`, `CLM-0001`, `LASTA`/`FIRSTA`, no DOB).
  `TestNoPHIInTestdata` enforces these patterns.
- Never put secrets in git, a log or a transcript. API keys are in the environment or in files
  that git ignores. Never `cat` a file that can hold a key.

## Writing

All documents, READMEs and skills use the Strict mode of simple-english, based on ASD-STE100. Before you write or
change a Markdown file, read the
[simple-english skill](../.claude/skills/simple-english/SKILL.md). Write with its rules for the
document, in Strict mode, and do its self-check before you give the change to the owner. Do not change code, ids, paths
or headings that other files link to.

## Adding things

- A spec area: add `spec/<area>.md`, and add it to `spec/INDEX.md`.
- A decision: add `docs/adr/NNNN-title.md`, and add it to `docs/adr/README.md`.
- An open question: take the next `Q-NNN` in `docs/platform/open-questions.md`. Add a table row
  and a section. The section gives the owner, what the question blocks, the options, what can
  settle it, and what we assume until then. Ids are stable. Close a duplicate, but never delete
  it. Add the question to "Blocking now" only if it stops work today.
- An improvement: take the next `CI-NNN` in `docs/continuous-improvement.md`. Add a table row
  and a section with the source, owner, experiment, measure and review sprint. At most three
  items are Active. The `continuous-improvement` skill (`.claude/skills/`) adds, reviews and
  closes items.
- Put each thing that is specific to one client in a client pack, not here.

## Commit and PR conventions

- The repository owner commits. Assistants leave their changes in the working tree for review.
- Write the commit subject in the imperative mood. In the body, say what changed and why. Give
  the spec rule ids and the roadmap slice ids.
- Jira issue keys use the `HCA` prefix (`HCA-123`). Each open roadmap story has one Task, under
  the epic of its station in the operating model. The key is in the Jira column of the story
  (`PROJECT_ROADMAP.md#jira`).
  - Name the branch `HCA-123-s6-03-short-name`. Put both ids in the PR title
    (`… (S6-03, HCA-123)`).
  - Give the key in the commit body and in the PR description, with the spec rule ids and the
    slice ids.
  - Never put the key in `cmd/`, `pkg/`, `spec/`, `docs/` or `frontend/`, because
    `TestNoClientIdentifiersInCore` operates there.
  - Change a story in the roadmap, never in Jira. After the roadmap changes merge, the lead
    mirrors the roadmap into Jira.
- Use these headings in the PR body: `## What?` / `## Why?` / `## Details`.
