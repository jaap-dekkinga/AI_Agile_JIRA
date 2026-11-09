# Jira access, modes and approval gates

## Which route to use

Use the first route that works, and tell the user which route you use:

1. The Atlassian MCP is connected (tools such as search, get issue, create issue and edit
   issue): use it to read and to write. It manages the login, and accepts Markdown descriptions.
2. REST credentials are available (`JIRA_EMAIL`, `JIRA_API_TOKEN` and `JIRA_SITE`, or
   `tools/jira-dashboard/jira_config.json`): use the scripts in `tools/jira-dashboard/` to read.
   At this time, they only read. For a write, prepare the change and ask the user to make it, or
   to connect the Atlassian MCP.
3. Neither route is available: offer demo mode (`JIRA_DEMO=1`) on fictional data, or tell the
   user to connect the Atlassian connector.

Never print, echo or log a token. To make sure that a credential is set, do not show it
(`printenv JIRA_API_TOKEN | cut -c1-4`).

## Modes: where the stories are written first

| Mode | Where stories are written first | What the skill does |
|---|---|---|
| roadmap-first | In `PROJECT_ROADMAP.md`, with the CDD method of `example-project/`. The roadmap leads, and Jira follows. | Writes a roadmap change for a pull request. After the merge, the lead mirrors the stories into Jira. |
| jira-first | In Jira. The Product Owner writes the stories there. | Writes drafts and scores, then writes them to Jira after approval. |

To find the mode, examine the repository. If it has a `PROJECT_ROADMAP.md` with stories, use
roadmap-first. If not, use jira-first. If the repository does not make it clear, ask once, and
use the answer for the full session.

## Approval gate before each write

The skill makes and changes nothing in Jira without an explicit yes from the user, after the
user saw the change. For each batch of writes:

1. Preview: show a table with the issue key (or "new"), the type, the summary, the fields that
   change (old → new), the parent epic, the labels and the sprint.
2. Ask: ask once for the full batch. The user can change the batch before the approval.
3. Write: write only what the user approved. Then give the key and the link of each issue.
4. Duplicates: before you make an issue, search for an open issue with the same summary in the
   same project. If you find one, ask before you make a second one.

The skill never changes the rank or the sprint of an item alone. The rank belongs to the
Product Owner, and the sprint belongs to the agreement of Engineering at sprint planning. The
skill can propose these changes in the preview. The team uses #NoEstimates, so the skill never
writes story points.

## Fields to look up

- Epic link: Jira Cloud uses the `parent` field. Older company-managed projects can use an
  "Epic Link" custom field.
- Board id: necessary for sprints. Find it from the boards of the project.
- Story points: not used. If a board has a story point field, leave it empty.
