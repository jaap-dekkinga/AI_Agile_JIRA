---
name: "simple-english"
description: "Write or rewrite text in plain, layman-readable English based on ASD-STE100 Simplified Technical English, for docs, runbooks, error messages, and plain-English or no-jargon requests."
---

# Simple English

Source: github.com/AminBlg/SimpleEnglish (MIT), version 2.1.1, with its reference files merged into this one file as appendices.

Write plain English that a smart reader outside your field understands on one read. The rules come from ASD-STE100, the controlled language that aerospace uses for maintenance manuals. Two registers exist: the document you write or rewrite, and the reply you type in chat. Each has its own short rule set below.

## The Document

When asked to write or rewrite documentation, apply these rules to the prose:

1. Classify each passage. Procedural text tells the reader what to do: imperative mood, 20 words per sentence, one instruction per sentence. Descriptive text explains: simple tenses, 25 words per sentence, one topic per paragraph, six sentences per paragraph at most.
2. Never touch code, identifiers, commands, flags, file paths, quoted errors, product names, or facts. When the source gives no number or cause, keep the general statement.
3. Condition before command, with a comma: "If the build fails, read the log."
4. Use simple tenses and active voice. No present perfect ("has completed" → "completed"). No "-ing" verb after a comma (", making it easy" → new sentence). Name the actor: "You run the migration."
5. Modals: can, will, must. Never should, would, may, might, could. A required "should" becomes "must". An optional one is deleted.
6. Use complete grammar. No contractions, keep articles, keep "that". Write short sentences, not telegraph style.
7. No semicolons and no em-dashes. Write two sentences, or name the relation.
8. One word, one meaning, for the whole document. Use `make sure that` for check, verify, confirm, validate, ensure. Use `configuration` for config, settings, options. Break noun chains over three words with a preposition ("the timeout value for the connection pool").
9. Give the reader each term and each fact before the step that needs it. Define a concept term at its first use, under ten words, one per sentence. Do not define product names, standard names (Postgres, S3, HTTP), or the tool the document is about. Also name the host, the flag, or the prior step that a command depends on. "Restart the service" becomes "Restart the `sync` service on the host that runs the job."
10. State the fact, not its importance. Delete words that carry no fact: simply, seamlessly, robust, powerful, comprehensive, leverage, crucial, "in order to", "it is worth noting". No "not just X, it is Y". No decorative triplets. No "in conclusion".
11. Use formatting only where it carries structure. No bold lead-ins, no bold as emphasis, no emoji, no heading over two sentences. A vertical list is for three or more parallel items or steps: colon on the lead-in, uppercase start, one instruction per item.
12. Warnings: command or condition first, then the risk. "Do not run this against production. The command deletes rows."

Use American spelling. Appendix A (Word swaps) maps the overused words to plain ones. For an error message, a runbook, an incident report, release notes, a commit message, or UI copy, read Appendix B (Use cases) first. It names the mode and the pattern for each.

Before (AI output):

> **Connection timeouts.** If sqlpipe hangs or fails with `dial tcp: i/o timeout`, check that the host running sqlpipe can reach the Postgres port (usually 5432) — this is often a security group or firewall rule blocking the connection. If you're connecting to a managed database (RDS, Cloud SQL, etc.), confirm the instance allows connections from sqlpipe's IP.

After (procedural, headed, numbered):

> ## Connection timeouts
>
> sqlpipe stops with `dial tcp: i/o timeout` when it cannot connect to the Postgres port (5432 by default).
>
> 1. Make sure that the host that runs sqlpipe can connect to the Postgres port. A firewall or security group usually blocks it.
> 2. If the database is managed (RDS, Cloud SQL), make sure that the instance accepts connections from the IP of sqlpipe.

## The Reply

Every chat reply, in every mode, follows these rules:

1. Answer in prose. No headers, no bullet lists, no bold, no tables. A code block is legal when the reader must copy it.
2. The first sentence gives the answer or the result. Do not restate the question.
3. No em-dashes. Name the relation ("because", "but", "for example") or write two sentences.
4. Define a concept term in a few words the first time you use it: "idempotent (safe to run twice)". Do not define product names.
5. No contractions. No openers ("Certainly", "Great question") and no closers ("I hope this helps", "Let me know").
6. Do not shorten quoted error text, security warnings, or confirmations before a destructive action.

Before: The failure stems from control-plane leader election during pod churn — nothing to worry about!
After: The pods restarted and the queue lost its leader for a short time. It recovered without help. You do not have to do anything.

## Self-Check Before You Deliver

1. Reply: search for `—`, `**`, `#`, and a line that starts with `-`. Remove each one.
2. Document: count the words in your three longest sentences. Over 20 or 25, split. Search for `'`, `has been`, `should`, `may`, `;`, `—`, `, making`, `**`, `check`, `verify`, `config`, and any heading that covers fewer than three sentences. Fix each hit. Read each step: does it name a host, a flag, or a prior step the reader must already have? If not, add it or point to it.

## Modes

Plain is the default and is all of the above. Strict applies when the user names STE, ASD-STE100, or compliance: read Appendix D (Strict vocabulary) before you draft the document, and say once that no tool guarantees compliance. The reply stays Plain in every mode.

When asked to CHECK text instead of writing it, first open Appendix C (Rule catalog). Then report each violation as: rule number quoted from that appendix, the offending text, a compliant rewrite. Never cite a rule number from memory. When the user asked for compliance, end with one sentence: no tool can guarantee ASD-STE100 compliance, and the standard is a free download at asd-ste100.org.

## Limits

These rules are for facts and instructions, not marketing copy or brand writing, because they delete persuasion. Say so, and offer them for the docs instead.

## Appendix A: Word swaps

This table is ours, not the ASD dictionary. It maps the words AI-generated docs overuse to plain replacements. If the word carries no fact, delete it instead of replacing it.

| Slop | Write instead |
|---|---|
| leverage, utilize | use |
| in order to | to |
| prior to | before |
| ensure | make sure that |
| it is worth noting that | (delete) |
| it's important to | (delete, then state the fact) |
| simply, just, easily, seamless, seamlessly, effortlessly | (delete) |
| robust, powerful, comprehensive, performant | (delete, or give the measurable property) |
| functionality | function, feature |
| enables you to, allows you to | you can |
| is designed to, aims to | (delete, then say what it does) |
| facilitate | help, make possible |
| dive into, delve into | read, examine |
| when it comes to | for |
| in the event that | if |
| due to the fact that | because |
| as needed, as necessary | (state the condition) |
| and/or | Pick one, or write "X, or Y, or both" |
| e.g. / i.e. / etc. | for example / that is / (name the items) |
| gracefully handles | (say what it does: "retries three times, then stops") |
| out of the box | by default |
| under the hood | internally |
| blazingly fast | fast (give the number) / (delete) |
| streamline | make simpler, make faster |
| plethora, myriad | many |
| addresses the issue, tackles | corrects the fault, removes the error |
| pivotal, crucial, crucially, paramount | important |
| tapestry, testament, synergy | (delete) |
| interplay | interaction (or delete) |
| intricate | complex |
| vibrant, nuanced, multifaceted | (delete, or name the parts) |
| realm, landscape (metaphorical) | area |
| groundbreaking, cutting-edge, state-of-the-art, innovative, unprecedented | new (or delete) |
| transformative, game-changer | (delete, then say what changes) |
| revolutionize | change |
| showcase, underscore, emphasize | show |
| foster, empower, bolster | help, support, let |
| harness | use |
| enhance | improve |
| elevate | increase |
| furthermore, moreover | also |
| in conclusion, in summary, at the end of the day | (delete) |
| embark, endeavor | start, try |
| meticulous, meticulously | careful, carefully |
| holistic | full |
| paradigm | model |
| navigate (metaphorical) | go to |
| boasts | has |
| nestled, in the heart of | (delete, then give the location or the fact) |
| bustling | busy |
| that being said, notwithstanding | but |
| I hope this helps, let's dive in | (delete) |

## Appendix B: Use cases

STE was built for aircraft maintenance manuals. The same properties transfer to any text where a misreading has a cost: one meaning per word, short sentences, condition-first commands. Each case below names the mode and the adaptations.

### Error messages and CLI output

Mode: procedural. An error message is an instruction to a reader who is in the middle of a failure.

Pattern: state what happened (simple past), state the cause if known, give the command or condition that fixes it.

> Before: Oops! Something went wrong while attempting to establish a connection. Please ensure your credentials are properly configured and try again.
> After: Connection to the database failed. The password for user `app` was not correct. Set `DB_PASSWORD` and connect again.

### Runbooks and standard operating procedures

Mode: procedural. An on-call runbook is a maintenance manual, which is the text type that STE was written for.

- Every step is imperative, one instruction per step, condition first.
- A warning comes before its step: command first, risk second.
- No sentence has more than 20 words.

### Incident reports and postmortems

Mode: descriptive, simple past only. A timeline in present perfect ("we have identified") hides when things happened.

> Before: We have identified an issue that may have impacted some users' ability to access the service.
> After: Between 14:02 and 14:31 UTC, 12% of requests failed. A deploy at 14:00 removed the cache warmup step.

STE bans hedges such as "may have impacted". The report states what is known and says "unknown" for the rest.

### Commit messages and PR descriptions

Mode: imperative subject line, descriptive body. The convention already matches STE. Apply the word swaps and the 25-word limit to the body. Delete "this PR aims to".

### API changelogs and release notes

Mode: descriptive. One entry, one change, one sentence where possible. A "Breaking:" entry follows the warning pattern, command first: "Update your calls to `v2/users`. The `name` field split into `first_name` and `last_name`."

### Instructions for AI agents (prompts, AGENTS.md, skills)

Mode: procedural. A system prompt is a procedure for a reader that cannot ask questions.

- One instruction per sentence keeps each rule quotable and hard to half-follow.
- One word, one meaning stops the model from treating "check", "verify", and "validate" as three operations.
- A condition first ("If the build fails, stop") beats a trailing condition, which models drop.
- No "should". A model reads "should" as optional. Write "must" or delete the rule.

### Support macros and status-page updates

Mode: descriptive, 25-word limit. Many readers of these messages are non-native speakers.

> Before: We sincerely apologize for any inconvenience this may have caused.
> After: The API was down for 18 minutes. Uploads made during this time were saved and will process today.

### Translation and localization prep

Mode: strict. STE was written so that non-native maintenance crews can read English manuals. The same rules prepare text for machine translation. One meaning per word and complete grammar (articles, "that") remove many ambiguities that a translator must otherwise guess at.

### UI copy and empty states

Mode: procedural, hard length limits. Buttons and labels are technical names and are exempt. Body copy follows the rules: "No projects yet. Create a project to start."

### Where STE does not fit

Do not use STE for marketing pages, launch posts, blog posts, or brand writing. STE removes persuasion. Write those texts in your own voice, and use STE for the docs that they link to.

## Appendix C: Rule catalog

Read this appendix for CHECK mode, for Strict mode, or when a rule number is in question. The core skill above names the rules that move output the most. This appendix holds the whole catalog.

53 rules in 9 sections, paraphrased from ASD-STE100 Issue 9 with software examples. Rules marked (S) are Strict mode only (see Appendix D). The official wording is in the free standard at asd-ste100.org.

#### Section 1: Words (Rules 1.1-1.14)

| Rule | Instruction |
|---|---|
| 1.1-1.4, 1.6 (S) | Use only approved words, as their listed part of speech, meaning, and form. |
| 1.5 | You can use domain words as technical nouns ("webhook", "commit", "endpoint"). |
| 1.7 | Do not use technical nouns as verbs. |
| 1.8 | Use the technical nouns of your project or industry. |
| 1.9 | When you pick a technical noun, pick a short and clear one. |
| 1.10 | No regional, slang, or jargon words as technical nouns. |
| 1.11 | One item, one name. Do not call it "config" here and "settings" there. |
| 1.12 | You can use domain verbs as technical verbs ("deploy", "compile", "merge"). The standard names computer verbs as legal: click, type, copy, paste, delete, save, install, download, update, and more. When a common verb does the same job, prefer it: "find" instead of "detect". |
| 1.13 | Do not use technical verbs as nouns. |
| 1.14 | Use American English spelling. |

In Plain mode, rules 1.5, 1.8, and 1.12 make your domain vocabulary legal.

Before: You can webhook the event, then do a deploy.
After: Send the event to the webhook. Then deploy the service.

#### Section 2: Multi-word nouns (Rules 2.1-2.2)

| Rule | Instruction |
|---|---|
| 2.1 | Write multi-word nouns of three words or fewer. |
| 2.2 | When a technical noun needs more than three words, write it in full once, then give a short form or hyphenate the units. |

Break long noun chains with prepositions (of, on, in, for):

Before: the connection pool timeout configuration value
After: the timeout value for the connection pool

#### Section 3: Verbs (Rules 3.1-3.7)

| Rule | Instruction |
|---|---|
| 3.1 (S) | Use only the verb forms that the dictionary gives. |
| 3.2 | Use only: infinitive, imperative, simple present, simple past, simple future, past participle as adjective. |
| 3.3 | Use the past participle only as an adjective ("the cached response"). |
| 3.4 | No auxiliary verbs for complex constructions. No present perfect, no "is to be installed". |
| 3.5 | Use an "-ing" form only as a technical noun or inside one ("logging", "the mounting bracket"), never as a verb. |
| 3.6 | Active voice. In descriptive text, passive is legal only when the agent is unknown. To repair an agentless passive, use "you" (the reader) or "we" (your company): "Indexes are not used on this table" → "We do not use indexes on this table." |
| 3.7 | Describe an action with a verb, not a noun ("compress the file", not "perform compression of the file"). |

Approved modals: can, will, must. Banned: should, would, may, might, could. The modal ladder at the end of this appendix gives the replacement for each banned modal.

#### Section 4: Sentences (Rules 4.1-4.5)

| Rule | Instruction |
|---|---|
| 4.1 | Write short and clear sentences. |
| 4.2 | Do not omit words or use contractions to shorten sentences. Keep articles, keep "that". |
| 4.3 | Use a vertical list for complex text: colon on the lead-in, uppercase start, a period only on full-sentence items, no mixed instructions and facts, no nesting. |
| 4.4 | Use connecting words between sentences on related topics ("Then", "As a result"). |
| 4.5 | Put an article (the, a, an) or a demonstrative adjective (this, these) before nouns where applicable. Exception: no article before a noun when an identifier follows it: "Restart pod web-7f9b2". |

Rule 4.2 is the anti-terseness rule. Plain English is short sentences with complete grammar, not telegraph style:

Wrong shortening: Ensure file exists before running.
Plain: Make sure that the file exists before you run the command.

#### Section 5: Procedural writing (Rules 5.1-5.5)

| Rule | Instruction |
|---|---|
| 5.1 | Maximum 20 words per sentence. Warnings and cautions included. |
| 5.2 | One instruction per sentence, unless two actions happen at the same time. A step can add one sentence for an immediate result or limit. |
| 5.3 | Write instructions in the imperative: "Run the migration." |
| 5.4 | Put a required condition before the command, divided by a comma: "If the build fails, read the log." |
| 5.5 | Notes give information, never instructions or limits. A limit belongs with its action. Notes test: the procedure must still work for a reader who deletes all notes. |

Before: You'll want to grab the API key from the dashboard before configuring the client, which you can do under Settings.
After: Get the API key from the dashboard, under Settings. Then configure the client with this key.

#### Section 6: Descriptive writing (Rules 6.1-6.6)

| Rule | Instruction |
|---|---|
| 6.1 | Give information gradually: one new fact per sentence. |
| 6.2 | Use key words and phrases to give the text a logical structure. |
| 6.3 | Maximum 25 words per sentence. |
| 6.4 | Group related information in paragraphs. |
| 6.5 | One topic per paragraph. |
| 6.6 | Maximum six sentences per paragraph. |

#### Section 7: Safety instructions (Rules 7.1-7.3)

| Rule | Instruction |
|---|---|
| 7.1 | Use a word that shows the risk level ("WARNING" = injury, "CAUTION" = damage). If the two risks occur together, use "WARNING". |
| 7.2 | Start with a clear command or condition. |
| 7.3 | Then give the risk or the possible result. |

Put the instruction before the explanation. Use the same pattern for destructive CLI flags and migrations that you cannot undo.

Before: Note that data loss may occur in some circumstances if the destructive flag happens to be enabled when running against production.
After: CAUTION: Do not use the `--force` flag against production. The flag deletes rows that do not match the source.

#### Section 8: Punctuation and word count (Rules 8.1-8.7)

| Rule | Instruction |
|---|---|
| 8.1 | All standard punctuation is legal except the semicolon. Write two sentences instead. |
| 8.2 | Use hyphens to connect words that act as one unit. |
| 8.3 | Parentheses are legal for references, item numbers, abbreviations, plural forms, explanations, alternatives. |
| 8.4 | In a vertical list, the lead-in colon ends a sentence for word count. Each item after the colon counts as a new sentence and gets its own 20/25-word budget. |
| 8.5-8.7 | Count as one word each: text in parentheses, a hyphenated word, numbers, numbers with units, abbreviations, identifiers, quoted text, titles, labels, proper nouns. |

Rule 8.6 matters for software text: `sqlpipe run --config sqlpipe.yaml` in backticks counts as one word.

Dashes (a rule of this skill, not of the standard): an em-dash (`—`) splices two statements and hides the logic between them. Name the relation ("because", "but", "for example") or write two sentences. A spaced or double hyphen between statements is the same dash. A range (`5–10`), a list marker, and a flag (`--force`) are not.

#### Section 9: Writing practices (Rules 9.1-9.4, GR-1 to GR-8)

| Rule | Instruction |
|---|---|
| 9.1 | When a word-for-word replacement does not work, restructure the sentence. |
| 9.2 (S) | Use each approved word correctly: approved meaning, approved part of speech. |
| 9.3 | Prefer the one-word verb over the phrasal verb ("decrease", not "go down"; "install", not "set up"). Strict mode: the phrasal verb is a violation. |
| 9.4 | Keep one consistent style and terminology through the whole document. |

General recommendations: keep "that" (GR-1), primary verb first and the tool after "with" (GR-2: "Fetch the URL with curl"), clear pronoun referents (GR-3), "this + noun" (GR-4), inclusive language (GR-7). GR-6: "e.g." → "for example", "i.e." → "that is", delete "etc." and name the items.

#### The modal ladder

| You wrote | Write instead |
|---|---|
| should (requirement) | must |
| should (recommendation) | Delete it, or state it as fact: "X is better because Y." |
| should (inverted conditional: "should a failure occur") | if: "If a failure occurs" |
| may / might / could (possibility) | can |
| may (permission) | can |
| would (hypothetical) | can, or restructure: "If X occurs, Y occurs." |

### Signs of AI Writing

AI text drifts in known directions (Wikipedia "Signs of AI writing"). The rules above remove some already. Guard against the rest by direction, in documents and replies alike:

- Inflated significance: no "vital", "crucial", "a testament". State the fact.
- Negative parallelism: no "not just X, it is Y".
- Rule of three: no decorative triplets.
- Vague attribution: no "studies show". Name the source, or drop the claim.
- False ranges: no "ranging from X to Y" without real limits.
- Restating summaries: no "in conclusion" paragraphs.
- Editorializing asides: no "it is important to note".
- Collaborative leftovers: no "I hope this helps", no "Let me know".
- Formatting habits: no bold as decoration, no bold lead-ins, no emoji as structure, no heading for two sentences.

For the specific overused words, Appendix A maps each one to a plain replacement. If a word carries no fact, delete it instead.

### Word Choice

One word, one meaning, one part of speech, for the whole document (Rules 1.11, 9.4).

- The settings file is `configuration`, never config, settings, or options in the same document.
- The verify concept is `make sure that`, never check, verify, confirm, validate, or ensure as verbs. Strict mode routes the rest with Appendix D.
- Common swaps: however → but, therefore → as a result, since (= because) → because, perform → do, avoid → prevent, repeat → do again, acceptable → permitted, now → delete it.

## Appendix D: Strict vocabulary

Read this appendix when the user names STE, ASD-STE100, or compliance. Strict mode adds the dictionary rules to the document. It does not change the reply to the user, which stays in Plain mode.

The official dictionary (about 900 approved words and 1,200 rejected words with their alternatives) is copyrighted by ASD and is not reproduced here. This appendix gives the rules that depend on it, the rulings that software writers meet most, and the words the standard names as recurring errors. Tell the user, one time per conversation and in one sentence, that this index is lossy and that full compliance needs the official dictionary (free at asd-ste100.org).

### Rules that exist only with the dictionary

| Rule | Instruction |
|---|---|
| 1.1 | Use only approved words, technical nouns, or technical verbs. |
| 1.2 | Use an approved word only as its listed part of speech. |
| 1.3 | Use an approved word only with its approved meaning. |
| 1.4 | Use only the approved forms of verbs and adjectives. |
| 1.6 | Use an unapproved word only when it is a technical noun or part of one. |
| 3.1 | Use only the verb forms that the dictionary gives. |
| 9.2 | Use each approved word correctly: approved meaning, approved part of speech. |
| GR-5 | Avoid false friends: words that look like a word in the reader's language but mean something else. |
| GR-8 | Use the possessive apostrophe only when you are sure that it is correct. If unsure, write "the file of the user". |

Issue 9 adds a quick-reference list of approved verbs in the dictionary introduction. Check your verbs against it.

### Part-of-speech rulings

| Word | Ruling |
|---|---|
| test, check, work | Noun only. "Do a test", not "test the pump". "Check that X" becomes "make sure that X". |
| oil | Technical noun only. For the verb, the dictionary gives "lubricate": "Lubricate the linkage with oil." |
| help | Verb only. For the noun, the dictionary gives "aid": "with the aid of". |
| fall (noun) | Rejected. Use "decrease" for a reduction in value. Use "fall" (verb) only for movement downward by gravity: "Make sure that the tools do not fall into the engine." |
| follow | "To come after" only, never "obey". Write "obey the instructions". |
| above, below | Physical positions only. For limits write "more than", "less than". |

### Dictionary rulings on common software verbs

The standard has already chosen. Use the approved word.

| You wrote | Dictionary status | Use instead |
|---|---|---|
| check (verb), verify, confirm, ensure | All rejected as verbs | Route by intent: `make sure that` (a state), `examine` (look for faults: "examine the log"), `measure` (get a value), or the noun: "do a check of". |
| validate | Not in the dictionary | Legal as a technical verb (Rule 1.12), or replace with `make sure that`. |
| delete, drop (verb), destroy | All rejected as dictionary verbs | `erase` (data), `remove` (physical). In computer contexts `delete` is also a legal technical verb (Rule 1.12). Do not use `drop` or `destroy`. |
| remove | Approved verb | Keep it. |
| run, execute | Both rejected | `operate` for run, `do` for execute. |
| invoke, launch | Not in the dictionary | Legal as technical verbs (Rule 1.12). |
| display (verb), render, present (verb) | All rejected | `show` covers most software cases. Official alternatives: display → `show`, render → `make`, present → `give` or `show`. |
| issue | Not in the dictionary | Use as a technical noun, or replace with `problem` (approved). |
| failure | Rejected in general use; approved as a technical noun for performance loss | Use only for a performance error: "a failure of the pump". |
| error, problem | Approved nouns | Keep them. |

### Recurring errors the standard names

The dictionary introduction lists the words that writers get wrong most often. This is the software-relevant set, as rulings only.

| You wrote | STE writes |
|---|---|
| however | but |
| therefore | thus, as a result |
| since (= because) | because |
| any | Delete it, or restructure: "if you have any questions" → "if you have questions" |
| now | at this time. Better, delete it: "now start the service" → "start the service" |
| need to, have to | Imperative in procedures ("install"); "it is necessary to" in descriptive text |
| perform | do |
| insert | put (but SQL `INSERT` stays: it is quoted text) |
| reach | get, get to |
| avoid | prevent |
| repeat | do … again |
| acceptable | permitted. Better, give the limit: "a latency of less than 200 ms" |
| complete (adjective) | completed |
| the example below, the section above | Name the target, or put the reference after it: "the example that follows" |

### Strict self-check

Add these two steps to the self-check above:

1. Search the draft for every verb in the two tables above. Replace each hit with the approved word.
2. Search for the phrasal verbs you built ("set up", "go down"). Replace each with the one-word verb (Rule 9.3: "install", "decrease").