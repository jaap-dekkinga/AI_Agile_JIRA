# Executive briefing: Automation & Margin Dashboard
Reporting week ending 06 Nov 2026 · generated 06 Nov 2026 15:38 · about 10 minutes, then questions

> A script makes this file from tracker.db. A `[SHOW: …]` cue tells you which part of the dashboard to show. The numbers come from the data. Lines with the mark (REVIEW) are judgment calls. Make sure that they are correct before you give the briefing.

## 1 · Portfolio summary
`[SHOW: Portfolio Overview]`
- 4 On Track · 4 At Risk · 0 Off Track, across 8 projects.
- 5 projects get their data from Jira. Their average is 68.7% complete.

## 2 · Largest changes this week
`[SHOW: trajectory chart]`
- Operator Workbench: +10.7 percentage points, to 46.2%.
- Intake Document Classification: +6.0 percentage points, to 59.4%.

## 3 · Status of each initiative
`[SHOW: project table]`

| Project | Source | % | Change from last week | Status | Against plan | Largest open risk |
|---|---|---|---|---|---|---|
| Claims Follow-Up Automation | CFU | 95.7% | +2.7 | On Track | +15.7 | Second clearinghouse contract not yet sign |
| Intake Document Classification | IDC | 59.4% | +6.0 | On Track | -0.6 | Labelled training set below 2,000 document |
| Prior-Auth Assistant | mock | 29.8% | +0.0 | At Risk | -5.2 | — |
| Payer Policy Search | PPS | 92.8% | +1.3 | On Track | +7.8 | Policy source licence renewal pending |
| Operator Workbench | OWB | 46.2% | +10.7 | At Risk | -8.8 | Two engineers reassigned to incident work |
| Long-Term Care Onboarding | mock | 42.5% | +0.0 | At Risk | -7.5 | — |
| Data Platform Foundation | DPF | 49.3% | +2.1 | On Track | +4.3 | Data retention policy awaiting compliance  |
| Practice System Integrations | mock | 25.5% | +0.0 | At Risk | -4.5 | — |

## 4 · Points to talk about
- Claims Follow-Up Automation: 95.7%, On Track (+15.7 against the plan). The dashboard tracks onboarding separately, at 99.1%.
- Payer Policy Search: 92.8%, On Track (+7.8 against the plan).
- Operator Workbench: 46.2%, At Risk. Largest blocker: “Two engineers reassigned to incident work” (High). *(REVIEW: give the mitigation and its owner.)*

## 5 · Risks and mitigations
`[SHOW: a project's Barrier log]`

| Project | Risk | Severity | Owner | Status |
|---|---|---|---|---|
| Claims Follow-Up Automation | Second clearinghouse contract not yet signed | High | Morgan Lee | Open |
| Intake Document Classification | Labelled training set below 2,000 documents | High | Priya Nair | Open |
| Operator Workbench | Two engineers reassigned to incident work | High | Morgan Lee | Open |
| Payer Policy Search | Policy source licence renewal pending | Med | Dana Brooks | Open |
| Operator Workbench | Design system components not yet accessible | Med | Chris Tan | Open |
| Data Platform Foundation | Data retention policy awaiting compliance review | Med | Riley Chen | Open |

*(REVIEW: make sure that each mitigation is correct, and say what the team needs.)*

## 6 · Requests (REVIEW: change them for the audience)
1. Claims Follow-Up Automation: give an owner to the blocker “Second clearinghouse contract not yet signed” (High), so that the owner removes it.
2. Intake Document Classification: give an owner to the blocker “Labelled training set below 2,000 documents” (High), so that the owner removes it.
3. Operator Workbench: give an owner to the blocker “Two engineers reassigned to incident work” (High), so that the owner removes it.
4. Operator Workbench: At Risk at 46.2% (-8.8 against the plan). Agree on people and priority, so that it returns to On Track.
- Standing request: each team links each Jira story to its epic. These numbers do not include a story without an epic.

## 7 · How we make this report
> The data comes directly from Jira. We lock each week, so the history cannot change. Each file shows the date on which it was made, and has a glossary for each metric and date.
`[SHOW: KPI Glossary → Dates & reporting weeks]`

### Appendix: questions and answers
- Why can a number be lower than in an earlier week? The % includes only the Jira stories that are linked to an epic. When a team adds stories to an epic, the % includes more work. The number is more correct, and sometimes lower.
- Why do some projects show no change from last week? Their numbers did not change this week, or their teams report them by hand. Section 2 gives the largest changes.
- Is it live? No. It is a weekly locked snapshot, not a live feed. Thus it is stable, and you can audit it. The footer shows when the file was made.
