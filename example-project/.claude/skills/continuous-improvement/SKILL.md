---
name: continuous-improvement
description: Keep the local improvement register of the Scrum Master (docs/continuous-improvement.local.md). Use it to add, review, close or list CI-NNN improvement items, for example before or after a retrospective.
---

# Continuous improvement

The register is the local file `docs/continuous-improvement.local.md` on the computer of the
Scrum Master. Git ignores it. If the file does not exist, tell the person. Offer to make it as a
copy of the template `docs/continuous-improvement.md`, without the example items. Read the
register before you change it. It holds
`CI-NNN` items. Each item has a row in the All items table and a section with its fields. While
an item is Active, it also has a row in the Active items table. The register also holds the
Working agreements table.

You keep the record, and people decide. Never adopt, stop or start an item on your own
judgment. Do it only when the person tells you that the team decided it.

## Rules for each task

- Ids are stable. To get a new id, take the highest `CI-NNN` in the file and add one. Never
  renumber, use again or delete an item. Stop a duplicate with the result "Duplicate of
  CI-NNN".
- Each item has one named owner. If the person names nobody, ask who owns it.
- A Active item has an experiment, a measure and a Review by sprint. A measure is a number or a
  sign that anyone can examine. If the person gives a feeling ("standups feel better"), propose
  one measure that anyone can examine. Ask the person to agree to it.
- At most three items are Active. If a fourth item is about to start, tell the person, and add
  the item as Proposed.
- Each sprint has the name of its start date (`sprint 2026-11-09`). A sprint is two weeks long.
- Do not put PHI, client names, secrets or Jira keys from other projects in the file.
- Change only the local register, unless an adopted item changes the method. Leave a change to
  a file in the repository in the working tree for the owner to review and commit. Never commit
  and never push. Never copy the local register into the repository.
- Write the text with the simple-english skill (`.claude/skills/simple-english/SKILL.md` at
  the root of the repository). Use the style of the rest of the file.
- Write a status as one word: Proposed, Active, Adopted or Stopped. Add the date for Adopted
  and Stopped: `Adopted (2026-11-20)`.

## Add an item

Do this task when the person says "add an improvement" or "log this for the retro", or gives
you retrospective notes.

1. From the notes, take one item for each change that the team agreed to try. Ignore
   complaints without an agreed change. Give the items back to the person, one line each. If
   the notes are not clear, ask which items to add.
2. For each item, write these fields: the improvement (one line), the source, the owner, the
   experiment, the measure and the Review by sprint. The source is the retrospective, by the
   start date of its sprint, or the person and the date. If nobody gave you a field, write "not
   set yet" and keep the item as Proposed.
3. Add the row to the All items table. Add the section after the section of the last item. If
   the item is Active, add a row to the Active items table.
4. If the item needs work, its action is to write that work as a user story on the backlog.
   Work in the repository is a roadmap story. Other work, for example a change to a Jira
   setting, is a Jira Task in the CDD Framework epic. Tell the person which one it is. Do not
   make the story or the Task unless the person asks you to.

## Review before a retrospective

Do this task when the person says "review the register", "what is due at the retro" or "prep
the retro". Do not change the file. Give a report in this order:

1. Due at this retrospective: each Active item whose Review by is the current sprint or an
   earlier sprint. Give its measure, and what the person told you about the result. Ask the
   person to bring the evidence.
2. Overdue: items whose Review by sprint is in the past. The team decides these items first.
3. No measure or no owner: Active items that the team cannot judge in their current form.
4. Waiting: Proposed items, the oldest first. Also give the number of free Active places (3
   minus the number of Active items).

Keep the report short enough to read aloud at the start of the meeting.

## Close an item

Do this task when the person says that the team adopted, stopped or extended an item.

- Adopted: set the status to `Adopted (YYYY-MM-DD)` in the All items table. Remove the row
  from the Active items table. Write the Result: what the measure showed. Then make the change
  that the item adopts, in the same working tree. This can be a line in
  `docs/agile-practices.md` or a line in `CLAUDE.md`, and a row in the Working agreements table
  of the register.
  If the place is not clear, ask the person. The result of the item names the place of the
  change.
- Stopped: set the status to `Stopped (YYYY-MM-DD)`. Remove the row from the Active items table.
  Write the result and the reason. A stopped item is a lesson, so write what the team learned.
- Extended: move the Review by sprint one sprint later and add ", extended once". The team can
  extend an item only once. A second extension is a decision to adopt or to stop, so ask the
  person for that decision.
- Started: a Proposed item becomes Active only when it has an experiment, a measure and a
  Review by sprint. Fewer than three items must be Active at that time.

## Show what the team tries

Do this task when the person asks "what are we trying" or "status of improvements". List the
Active items: id, improvement, owner and Review by sprint. Give one line for each item. Do not
change the file.
