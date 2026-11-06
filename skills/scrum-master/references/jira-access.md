# Jira access, modes and approval gates

## Which route to use

Pick the first that works and say which one you are using:

1. **Atlassian MCP connected** (tools such as search, get issue, create issue, edit issue): use it
   for reads and writes. It handles login, and accepts Markdown descriptions.
2. **REST credentials present** (`JIRA_EMAIL`, `JIRA_API_TOKEN` and `JIRA_SITE`, or
   `tools/jira-dashboard/jira_config.json`): use the scripts in `tools/jira-dashboard/` for reads.
   They are read-only today. For writes, prepare the change and ask the user to apply it, or to
   connect the Atlassian MCP.
3. **Neither:** offer demo mode (`JIRA_DEMO=1`) on fictional data, or suggest connecting the
   Atlassian connector.

Never print, echo or log a token. Check that a credential is set without showing it
(`printenv JIRA_API_TOKEN | cut -c1-4`).

## Source-of-truth modes

| Mode | Who writes stories where | What the skill does |
|---|---|---|
| **jira-first** (default) | The PO works in Jira. | Drafts and rates stories, then writes them to Jira after approval. |
| **repo-first** | Stories are written in `PROJECT_ROADMAP.md` first and mirrored to Jira (the CDD method in `example-project/`). | Drafts a roadmap change for a pull request instead of writing to Jira, then mirrors approved stories to Jira. |

Ask which mode the team uses the first time, if it isn't clear from the repository, and remember
it for the session.

## Approval gate before any write

Nothing is created or changed in Jira without the user's explicit yes, given after they have seen
the change. For every batch of writes:

1. **Preview** a table: issue key (or "new"), type, summary, the fields that change (old → new),
   parent epic, labels, sprint.
2. **Ask** once for the whole batch. Accept edits to the batch before approval.
3. **Write** only what was approved, then report each issue's key and link.
4. **Check for duplicates** before creating: search for an open issue with the same summary in the
   same project, and ask instead of creating a second one.

The skill never changes story points, rank or sprint membership on its own. Points belong to the
team (planning poker), rank to the PO, and sprint membership to Engineering's agreement at sprint
planning. It may propose them in the preview.

## Fields to look up, not assume

- **Story points:** the field id differs per site. Look it up by name ("Story point estimate",
  "Story Points") through the field list, and set it in `tools/jira-dashboard/pull_jira.py`
  (`SP_FIELD`) for the scripts.
- **Epic link:** current Jira Cloud uses the `parent` field. Older company-managed projects may use
  an "Epic Link" custom field.
- **Board id:** needed for sprints; find it from the project's boards.
