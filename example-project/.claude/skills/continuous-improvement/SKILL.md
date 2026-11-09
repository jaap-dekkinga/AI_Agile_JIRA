---
name: continuous-improvement
description: Keep the team's improvement register (docs/continuous-improvement.md). Use to add an improvement from a retrospective or a conversation, to review the register before a retrospective, to close an item as adopted or dropped, or to list what the team is trying now.
---

# Continuous improvement

The register is `docs/continuous-improvement.md`. Read it before you change it. It holds
`CI-NNN` items: a row in **All items**, a row in **Trying now** while the item is Trying, and a
section with the item's fields. It also holds the **Working agreements** table.

You keep the record. People decide. Never adopt, drop or start an item on your own judgment.
Do it only when the person says the team decided it.

## Rules that always apply

- Ids are stable. Take the highest `CI-NNN` in the file and add one. Never renumber, reuse or
  delete an item. A duplicate is dropped with "Duplicate of CI-NNN" as its result.
- Every item has one named owner. If nobody is named, ask who owns it.
- A Trying item has an experiment, a measure and a **Review by** sprint. A measure is a number
  or a sign anyone can check. If the person gives a feeling ("standups feel better"), offer one
  checkable measure and ask them to confirm it.
- At most three items are Trying. If a fourth would start, say so and add it as Proposed.
- Sprints are named by their start date (`sprint 2026-11-09`). Sprints are two weeks long.
- No PHI, client names, secrets or Jira keys from other projects in the file.
- Leave your change in the working tree for the repository owner to review and commit. Never
  commit or push.
- Write plain, short sentences, in the style of the rest of the file.

## Add an item

Use when the person says "add an improvement", "log this for the retro", or gives retro notes.

1. From the notes, take one item per change the team agreed to try. Skip complaints with no
   agreed change. List them back to the person in one line each, and ask which to add if the
   notes are unclear.
2. For each item, fill: improvement (one line), source (the retro, by sprint start date, or the
   person and date), owner, experiment, measure, review by. A field nobody gave you is "not set
   yet", and the item stays Proposed.
3. Add the row to **All items**, the section after the last item, and a row to **Trying now**
   if it is Trying.
4. If the item needs build work, say it needs a roadmap story. If it needs a Jira setting
   changed, say it needs a Jira Task in the CDD Framework epic. Do not create either unless
   asked.

## Review before a retrospective

Use when the person says "review the register", "what's due at the retro", or "prep the retro".
Change nothing. Report, in this order:

1. **Due this retrospective:** each Trying item whose Review by is the current sprint or
   earlier. Give its measure and anything the person told you about how it went. Ask them to
   bring the evidence.
2. **Overdue:** items past their Review by sprint. These should be decided first.
3. **Missing a measure or an owner:** Trying items that can't be judged as they stand.
4. **Waiting:** Proposed items, oldest first, and how many Trying slots are free (3 minus the
   number Trying).

Keep it short enough to read aloud at the start of the meeting.

## Close an item

Use when the person says an item is adopted, dropped or extended.

- **Adopted:** set the status to `✅ Adopted (YYYY-MM-DD)` in **All items**, remove it from
  **Trying now**, and write the **Result**: what the measure showed. Then make the change it
  adopts in the same working tree: a line in `docs/agile-practices.md`, a row in **Working
  agreements**, or a line in `CLAUDE.md`. Ask which, if it isn't clear. The item's result names
  where the change went.
- **Dropped:** set `✖ Dropped (YYYY-MM-DD)`, remove it from **Trying now**, and write the result
  and the reason. A dropped item is a lesson, so say what was learned.
- **Extended:** move **Review by** one sprint later and add ", extended once". An item may be
  extended only once. A second extension is a decision to adopt or drop, so ask for it.
- **Started:** a Proposed item moves to Trying only with an experiment, a measure and a review
  sprint, and only when fewer than three items are Trying.

## Show what we are trying

Use when the person asks "what are we trying", "status of improvements" or similar. List the
Trying items: id, improvement, owner, review sprint. One line each. Change nothing.
