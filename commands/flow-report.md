---
description: Make a draft value stream map, the six flow metrics and the CFD findings from Jira or Azure DevOps history
argument-hint: "[JQL, project keys or an export file] [--team NAME] [--segment label:NAME]"
---
Use the "Discover the value stream" and "Explain a CFD" workflows of the scrum-master skill for $ARGUMENTS. Get six months of status history, keep the raw export in `flow-data/`, and anonymize it with `scripts/flow/flow_prepare.py`. Show me the list of statuses and a draft status map, and ask me for the commitment point before you use the map. Then start `scripts/flow/flow_report.py` with `--workdays`, and `scripts/flow/cfd.py` with `--svg`. Give me the summary, the Mermaid map, the largest wait, the likely constraint, the CFD findings and the data quality section. Write each cause as a hypothesis with its evidence. Count items, not story points. Change nothing in Jira.
