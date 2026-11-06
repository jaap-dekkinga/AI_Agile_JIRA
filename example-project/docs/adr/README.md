# Decision log

Architecture Decision Records for the fictional Harbor Claims Assistant. Each ADR records one
decision, the options considered and the consequences. An accepted ADR is never rewritten; when
it is replaced, only its *Status* line changes.

Only the index is included in this example. A full ADR is a short file,
`docs/adr/NNNN-title.md`, with the sections *Status*, *Context*, *Decision*, *Consequences*.

| ADR | Decision | Status |
|---|---|---|
| 0001 | Product, not solution: one Core plus client packs, never a fork | Accepted |
| 0002 | Deterministic Core: Capabilities are pure functions | Accepted |
| 0003 | Recommend, never act: irreversible actions need an Operator | Accepted |
| 0004 | Service shape; PostgreSQL only | Accepted |
| 0005 | Every database object `dm_`-prefixed in a shared database | Accepted |
| 0006 | Product vendors may be named in the Core; client vendors may not | Accepted |
| 0007 | The canonical claim status model is X12-277-shaped | Accepted |
| 0008 | Raw payer payloads are retained under a TTL | Accepted |
| 0013 | The Reference UI is a demonstration surface, not the product UI | Accepted |
| 0014 | Queued inquiries hold patient identity only as long as a send can use it | Proposed (S7-01) |
| 0015 | The agent tool surface carries no PHI | Proposed (S9-01) |
| 0017 | The canonical eligibility (271) model | Accepted |
