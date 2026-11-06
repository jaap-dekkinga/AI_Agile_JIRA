# Start here

Welcome. This page is the way into the project for anyone: leadership, product,
architecture or engineering. It explains what the project is, how we work, and where
everything lives. It takes about five minutes.

> **Example content.** Harbor Claims Assistant is a fictional product, used here to show a
> complete Context Driven Development setup: roadmap, Jira mirroring, open questions,
> decisions, glossary, spec rules and AI-assistant conventions.

## What this is

**Harbor Claims Assistant** helps healthcare billing teams decide what to do next with a claim.
It finds out a claim's status from the insurer, interprets it, and recommends the next
action, with the evidence behind the recommendation.

- It is a **product**, not a one-off build for a single client. One codebase is configured
  for each client through a **client pack**, and never forked.
- It is **deterministic**: the same facts always produce the same recommendation, and
  every recommendation says which rule produced it.
- It **recommends; people act.** Nothing irreversible happens without a person's decision.

## How we work

We follow **Context Driven Development (CDD)**: *the spec is the context*. Before anything is
built, what we know is written down in this repository and reviewed like code:
- the direction;
- the open questions and who owns them;
- the decisions and their reasons;
- the meaning of our words;
- the rules the system must follow.

Tests cite the rules they prove, and code follows. Anyone can improve the context with a
pull request, and most useful contributions don't involve code at all.

The full process, with the roles and how they overlap, is in
**[docs/context-driven-development.md](docs/context-driven-development.md)**.

We plan and deliver in **two-week sprints**, with a daily standup, backlog grooming, sprint
planning, a sprint demo and a retrospective. PMs keep the backlog groomed and clear blockers,
and Engineering decides what goes into each sprint. The meetings, and when a story is ready to
build, are in **[docs/agile-practices.md](docs/agile-practices.md)**.

## Find your role

Roles overlap, and one person often holds more than one. Start with the row that fits you
today.

| If you are… | You'll mostly read | You'll mostly write | Start with |
|---|---|---|---|
| **Leadership**: product direction and goals | Roadmap, blocking questions, decisions | Direction; answers to cross-team questions | [Roadmap](PROJECT_ROADMAP.md) · [Blocking now](docs/platform/open-questions.md#blocking-now) |
| **Product Management**: requirements, priorities, timeline, domain answers, the backlog | Roadmap, open questions, glossary, rules | Clarified questions, slices, groomed stories, domain meaning of terms and rules | [Roadmap](PROJECT_ROADMAP.md) · [Open questions](docs/platform/open-questions.md) · [Glossary](spec/glossary.md) · [Agile practices](docs/agile-practices.md) |
| **Lead Architect**: stack, architecture, standards | Decisions, architecture rules | ADRs, technical terms, conventions | [Decisions](docs/adr/README.md) · [Conventions](CLAUDE.md) |
| **Software Developer**: building features | The spec area for your slice, conventions | Rules, tests, code; findings on open questions | [Spec index](spec/INDEX.md) · [Conventions](CLAUDE.md) |

## The map

Every kind of context, what it answers, and where it lives.

| Looking for… | It's answered by | Where |
|---|---|---|
| What are we building next, and what's done? | The roadmap, in slices (`S6`) | [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) |
| How does the roadmap reach Jira? | The roadmap's Jira section | [PROJECT_ROADMAP.md#jira](PROJECT_ROADMAP.md#jira) |
| When does the work happen, and what is each meeting for? | Two-week sprints, their meetings, and the Definitions of Ready and Done | [docs/agile-practices.md](docs/agile-practices.md) |
| What does this word mean? | The glossary, plus the X12 and billing reference | [spec/glossary.md](spec/glossary.md) · [CDD vocabulary](docs/context-driven-development.md#cdd-vocabulary) |
| What's still undecided, and who decides? | Open questions (`Q-NNN`) | [docs/platform/open-questions.md](docs/platform/open-questions.md), starting with [Blocking now](docs/platform/open-questions.md#blocking-now) |
| Why is it built this way? | Decisions (ADRs) | [docs/adr/README.md](docs/adr/README.md) |
| What exactly must the system do? | Rules (`eligibility-006`) | [spec/INDEX.md](spec/INDEX.md) |
| What are the coding conventions? | Conventions (also what AI assistants read) | [CLAUDE.md](CLAUDE.md) |

## Your first hour

1. This page.
2. [How we work](docs/context-driven-development.md): the idea, the lifecycle diagram, and
   your role.
3. The [Defined Terms](spec/glossary.md#defined-terms) in the glossary. Most confusion
   comes from words that mean something precise here.
4. [Blocking now](docs/platform/open-questions.md#blocking-now): the questions that are
   stopping work today, and who owns them.
5. The [roadmap](PROJECT_ROADMAP.md): find a slice marked 🟡 (in progress) and read its
   goal.

Then pick one thing you know something about, whether that's an open question, a term or a
rule, and open a pull request that makes it clearer. That's how CDD works.
