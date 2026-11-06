"""Shared reporting configuration.

ACTIVE_KEYS — the Jira boards pulled live each week. Every other project (no
jira_key, or a jira_key that is not listed here) carries its most recent locked
week forward unchanged and shows as 'stale' in the weekly summary.

Not every board listed here reaches the dashboard: the rendered project list is
whatever carries `projects.active=1`, and a retired board (active=0) is configured
but not pulled and not shown.

Retiring a project is done with `projects.active=0`, NOT by removing it here:
dropping a key from this set leaves the project on the dashboard showing stale
numbers, which is worse than either hiding it or pulling it. Keeping the key
listed is also what makes un-retiring a project a one-flag change.

A board listed here that has no epics yet is not an error: it simply does not
appear on the dashboard until its first epic lands, and it never blocks the other
boards' week. See pull_jira.EXIT_NO_EPICS.

The keys and project names below are EXAMPLES (see seed_demo_db.py). Replace them
with your own Jira project keys.
"""

ACTIVE_KEYS = {
    'AGP',   # Agent Platform (RETIRED - active=0)
    'SOC',   # SOC 2 Certification (RETIRED - active=0)
    'OWB',   # Operator Workbench
    'DPF',   # Data Platform Foundation (has milestones, below)
    'PPS',   # Payer Policy Search
    'PMO',   # Product Management Office (RETIRED - active=0; business project, see PARENT_TYPES)
    'CFU',   # Claims Follow-Up Automation
    'IDC',   # Intake Document Classification
}

# The issue type that plays the EPIC role on a board, where it is not 'Epic'.
# Jira business projects have no Epic type at all; their top level is a custom
# type (PMO uses 'Workstream'), with stories parented to it exactly as they would
# be to an epic. Everything downstream still calls these rows "epics".
PARENT_TYPES = {
    'PMO': 'Workstream',
}

# ---------------------------------------------------------------------------
# STATUS_CREDIT — partial credit toward "complete", per Jira status NAME.
#
# Progress is effort-weighted: Σ(story points × credit) ÷ Σ(story points). Without
# this table every issue is all-or-nothing, keyed on Jira's statusCategory, so a
# story sitting in review counts for exactly nothing until someone moves it.
#
# Keying on the status NAME is the whole point: 'In Progress' and 'In Review' are
# both statusCategory 'indeterminate', so the category cannot tell them apart.
#
# Any status NOT listed here falls back to its category — 'done' scores 1.0 and
# everything else 0.0. So this map only needs the statuses that deserve something
# other than 0 or 1.
#
# These fractions are a reporting convention, not a measurement: a story in review
# is not literally 75% delivered. Keep them coarse, and do not tune them to make a
# RAG status look better.
#
# NOTE: statuses such as "Won't Do" or "Ready for UAT" often sit in category 'done'
# and so score 1.0 — abandoned and not-yet-tested work is credited as delivered.
# Decide deliberately whether to list them here at 0.0.
STATUS_CREDIT = {
    'In Progress': 0.50,
    'In Review':   0.75,
}

# ---------------------------------------------------------------------------
# MILESTONES — the delivery milestones shown in the dashboard's "MS Progress"
# panel, per Jira board. Boards absent from this map get no panel at all.
#
# Each entry is (jira_label, deliverable). The LABEL IS THE JOIN KEY: progress is
# whatever carries that label in Jira. It is deliberately not rendered — the
# dashboard shows the deliverable text, because "MS2" means nothing to a reader
# outside the team.
#
# The order here is the display order, and it is the ONLY place milestones are
# declared. A milestone stays listed even when nothing in Jira carries its label
# yet: the panel then reports it as not-yet-labelled rather than 0%, because
# "nobody has tagged this work" and "this work has not started" are different
# claims and only one of them is supported by the data.
#
# Renaming a label here orphans the stored history for the old name (it is keyed
# by label), so prefer re-labelling in Jira over renaming here.
MILESTONES = {
    'DPF': [
        ('MS1', 'Source inventory signed off; schema finalized and frozen; '
                'data-quality baseline'),
        ('MS2', 'Core ingestion live — billing system, operator actions, '
                'payer-policy data'),
        ('MS3', 'Enrichment layer + data-quality monitoring, alerting and '
                'validation; outputs to the analytics workspace'),
        ('MS4', 'Legacy reporting migrated onto the platform; '
                'cutover and go-live'),
    ],
}
