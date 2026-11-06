# Exec Briefing — Automation & Margin Dashboard
**Reporting week ending 06 Nov 2026** · generated 06 Nov 2026 15:38 · ~10 min + Q&A

> Auto-generated from tracker.db. `[SHOW: …]` cues = where to be in the dashboard. Numbers are live; lines marked **(REVIEW)** are judgment calls to confirm before presenting.

## 1 · Portfolio at a glance
`[SHOW: Portfolio Overview]`
- **4 On Track · 4 At Risk · 0 Off Track** across 8 projects.
- **5 live from Jira**, averaging **68.7% complete** (story-point-weighted).

## 2 · This week's movers
`[SHOW: trajectory chart]`
- 📈 **Operator Workbench** +10.7 pts → 46.2%.
- 📈 **Intake Document Classification** +6.0 pts → 59.4%.

## 3 · Where each initiative stands
`[SHOW: project table]`

| Project | Source | % | WoW | Status | vs Plan | Top open risk |
|---|---|---|---|---|---|---|
| Claims Follow-Up Automation | CFU | 95.7% | +2.7 | 🟢 On Track | +15.7 | Second clearinghouse contract not yet sign |
| Intake Document Classification | IDC | 59.4% | +6.0 | 🟢 On Track | -0.6 | Labelled training set below 2,000 document |
| Prior-Auth Assistant | mock | 29.8% | +0.0 | 🟡 At Risk | -5.2 | — |
| Payer Policy Search | PPS | 92.8% | +1.3 | 🟢 On Track | +7.8 | Policy source licence renewal pending |
| Operator Workbench | OWB | 46.2% | +10.7 | 🟡 At Risk | -8.8 | Two engineers reassigned to incident work |
| Long-Term Care Onboarding | mock | 42.5% | +0.0 | 🟡 At Risk | -7.5 | — |
| Data Platform Foundation | DPF | 49.3% | +2.1 | 🟢 On Track | +4.3 | Data retention policy awaiting compliance  |
| Practice System Integrations | mock | 25.5% | +0.0 | 🟡 At Risk | -4.5 | — |

## 4 · Spotlight (talking points)
- 🟢 **Claims Follow-Up Automation — 95.7%, On Track** (+15.7 vs plan). Onboarding tracked separately at **99.1%**.
- 🟢 **Payer Policy Search — 92.8%, On Track** (+7.8 vs plan).
- 🟡 **Operator Workbench — 46.2%, At Risk.** Top blocker: “Two engineers reassigned to incident work” (High). *(REVIEW: mitigation + owner.)*

## 5 · Risks & mitigations
`[SHOW: a project's Barrier log]`

| Project | Risk | Severity | Owner | Status |
|---|---|---|---|---|
| Claims Follow-Up Automation | Second clearinghouse contract not yet signed | High | Morgan Lee | Open |
| Intake Document Classification | Labelled training set below 2,000 documents | High | Priya Nair | Open |
| Operator Workbench | Two engineers reassigned to incident work | High | Morgan Lee | Open |
| Payer Policy Search | Policy source licence renewal pending | Med | Dana Brooks | Open |
| Operator Workbench | Design system components not yet accessible | Med | Chris Tan | Open |
| Data Platform Foundation | Data retention policy awaiting compliance review | Med | Riley Chen | Open |

*(REVIEW: confirm each mitigation and the specific help needed.)*

## 6 · Asks (REVIEW — tailor to the room)
1. **Claims Follow-Up Automation:** assign an owner to unblock “Second clearinghouse contract not yet signed” (High).
2. **Intake Document Classification:** assign an owner to unblock “Labelled training set below 2,000 documents” (High).
3. **Operator Workbench:** assign an owner to unblock “Two engineers reassigned to incident work” (High).
4. **Operator Workbench:** At Risk at 46.2% (-8.8 vs plan) — agree resourcing/priority to get it back on track.
- **Standing ask:** every team points its Jira stories — that's what keeps these numbers honest.

## 7 · How we run this (build trust)
> Generated straight from Jira, **locked each week** so history can't drift, stamped with a generation date, with a built-in glossary for every metric and date.
`[SHOW: KPI Glossary → Dates & reporting weeks]`

### Appendix — Q&A
- **Why can a number be lower than a past story?** Unpointed Jira stories are invisible to the %; as teams point their backlog the % reflects *all* the work (truer, sometimes lower).
- **Why is WoW flat?** See movers above.
- **Is it live?** A weekly locked **snapshot**, not a live feed — stable and auditable. Footer shows the build time.
