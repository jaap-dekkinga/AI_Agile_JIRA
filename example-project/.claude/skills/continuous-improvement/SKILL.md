---
name: continuous-improvement
description: Keep the improvement register of the team (docs/continuous-improvement.md). Use it to add, review, close or list CI-NNN improvement items, for example before or after a retrospective.
---

# Continuous improvement

The register is `docs/continuous-improvement.md`. Read it before you change it. It holds
`CI-NNN` items. Each item has a row in the All items table and a section with its fields. While
an item is Trying, it also has a row in the Trying now table. The register also holds the
Working agreements table.

You keep the record, and people decide. Never adopt, drop or start an item on your own
judgment. Do it only when the person tells you that the team decided it.

## Rules for each task

- Ids are stable. To get a new id, take the highest `CI-NNN` in the file and add one. Never
  renumber, use again or delete an item. Drop a duplicate with the result "Duplicate of
  CI-NNN".
- Each item has one named owner. If the person names nobody, ask who owns it.
- A Trying item has an experiment, a measure and a Review by sprint. A measure is a number or a
  sign that anyone can examine. If the person gives a feeling ("standups feel better"), propose
  one measure that anyone can examine. Ask the person to agree to it.
- At most three items are Trying. If a fourth item is about to start, tell the person, and add
  the item as Proposed.
- Each sprint has the name of its start date (`sprint 2026-11-09`). A sprint is two weeks long.
- Do not put PHI, client names, secrets or Jira keys from other projects in the file.
- Leave your change in the working tree for the repository owner to review and commit. Never
  commit and never push.
- Write the text with the simple-english skill (`.claude/skills/simple-english/SKILL.md` at
  the root of the repository). Use the style of the rest of the file.
- Write a status as one word: Proposed, Trying, Adopted or Dropped. Add the date for Adopted
  and Dropped: `Adopted (2026-11-20)`.

## Add an item

Do this task when the person says "add an improvement" or "log this for the retro", or gives
you retrospective notes.

1. From the notes, take one item for each change that the team agreed to try. Ignore
   complaints without an agreed change. Give the items back to the person, one line each. If
   the notes are not clear, ask which items to add.
2. For each item, fill in these fields: the improvement (one line), the source, the owner, the
   experiment, the measure and the Review by sprint. The source is the retrospective, by the
   start date of its sprint, or the person and the date. If nobody gave you a field, write "not
   set yet" and keep the item as Proposed.
3. Add the row to the All items table. Add the section after the section of the last item. If
   the item is Trying, add a row to the Trying now table.
4. If the item needs build work, tell the person that it needs a roadmap story. If it needs a
   change to a Jira setting, tell the person that it needs a Jira Task in the CDD Framework
   epic. Do not make the story or the Task unless the person asks you to.

## Review before a retrospective

Do this task when the person says "review the register", "what is due at the retro" or "prep
the retro". Do not change the file. Give a report in this order:

1. Due at this retrospective: each Trying item whose Review by is the current sprint or an
   earlier sprint. Give its measure, and what the person told you about the result. Ask the
   person to bring the evidence.
2. Overdue: items whose Review by sprint is in the past. The team decides these items first.
3. No measure or no owner: Trying items that the team cannot judge in their current form.
4. Waiting: Proposed items, the oldest first. Also give the number of free Trying places (3
   minus the number of Trying items).

Keep the report short enough to read aloud at the start of the meeting.

## Close an item

Do this task when the person says that the team adopted, dropped or extended an item.

- Adopted: set the status to `Adopted (YYYY-MM-DD)` in the All items table. Remove the row
  from the Trying now table. Write the Result: what the measure showed. Then make the change
  that the item adopts, in the same working tree. This can be a line in
  `docs/agile-practices.md`, a row in the Working agreements table, or a line in `CLAUDE.md`.
  If the place is not clear, ask the person. The result of the item names the place of the
  change.
- Dropped: set the status to `Dropped (YYYY-MM-DD)`. Remove the row from the Trying now table.
  Write the result and the reason. A dropped item is a lesson, so write what the team learned.
- Extended: move the Review by sprint one sprint later and add ", extended once". The team can
  extend an item only once. A second extension is a decision to adopt or to drop, so ask the
  person for that decision.
- Started: a Proposed item becomes Trying only when it has an experiment, a measure and a
  Review by sprint. Fewer than three items must be Trying at that time.

## Show what the team tries

Do this task when the person asks "what are we trying" or "status of improvements". List the
Trying items: id, improvement, owner and Review by sprint. Give one line for each item. Do not
change the file.
