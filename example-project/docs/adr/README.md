# Decision log

This page lists the Architecture Decision Records (ADRs) of the fictional Harbor Claims
Assistant. Each ADR records one decision, the options that we thought about, and the results.
Nobody writes an accepted ADR again. When a newer ADR replaces it, only its *Status* line
changes.

This example includes only the index. A full ADR is a short file, `docs/adr/NNNN-title.md`. It
has the sections *Status*, *Context*, *Decision* and *Consequences*.

| ADR | Decision | Status |
|---|---|---|
| 0001 | Product, not solution: one Core plus client packs, never a fork | Accepted |
| 0002 | Deterministic Core: Capabilities are pure functions | Accepted |
| 0003 | Recommend, never act: an action that cannot be undone needs an Operator | Accepted |
| 0004 | Service shape, with PostgreSQL only | Accepted |
| 0005 | Every database object `dm_`-prefixed in a shared database | Accepted |
| 0006 | The Core can name product vendors, but not client vendors | Accepted |
| 0007 | The canonical claim status model is X12-277-shaped | Accepted |
| 0008 | Raw payer payloads are retained under a TTL | Accepted |
| 0013 | The Reference UI is a demonstration surface, not the product UI | Accepted |
| 0014 | Queued inquiries hold patient identity only as long as a send can use it | Proposed (S7-01) |
| 0015 | The agent tool surface carries no PHI | Proposed (S9-01) |
| 0017 | The canonical eligibility (271) model | Accepted |
