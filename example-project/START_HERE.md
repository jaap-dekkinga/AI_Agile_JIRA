# Start here

This page is the start point into the project for all readers: leadership, product,
architecture and engineering. It tells you what the project is, how we do our work, and where to find
each document. It takes about five minutes to read.

> Example content. Harbor Claims Assistant is a fictional product. It shows a full Context
> Driven Development setup: roadmap, Jira mirroring, open questions, decisions, glossary, spec
> rules and conventions for AI assistants.

## What this is

Harbor Claims Assistant helps healthcare billing teams to decide the next action on a claim. It
gets the status of a claim from the insurer and interprets it. Then it recommends the next
action, with the evidence for the recommendation.

- It is a product, not a single build for one client. One codebase gets a configuration for
  each client through a client pack. Nobody forks the codebase.
- It is deterministic. The same facts always give the same recommendation. Each
  recommendation tells you which rule made it.
- It recommends, and people act. No action that cannot be undone happens without a decision
  by a person.

## How we do our work

We use Context Driven Development (CDD). Its main idea is that the spec is the context. Before
we build something, we write down what we know in this repository. We review it like code. The
context includes these items:

- The direction.
- The open questions, and who owns each one.
- The decisions, and the reasons for them.
- The meaning of our words.
- The rules that the system must obey.

Tests cite the rules that they prove. We write the code after the tests. Anyone can make the
context better with a pull request. Most useful changes do not include code.

[docs/context-driven-development.md](docs/context-driven-development.md) gives the full
process, the roles, and how the roles overlap.

We plan and deliver in two-week sprints. Each sprint has a daily standup, backlog refinement,
sprint planning, a sprint demo and a retrospective. PMs keep the backlog refined and remove
blockers. Engineering decides what each sprint includes.
[docs/agile-practices.md](docs/agile-practices.md) describes the meetings, and when a story is
ready to build.

## Find your role

Roles overlap, and one person often has more than one role. Start with the row that fits you
today.

| If you are… | You mostly read | You mostly write | Start with |
|---|---|---|---|
| Leadership: product direction and goals | Roadmap, blocking questions, decisions | Direction, and answers to questions across teams | [Roadmap](PROJECT_ROADMAP.md) · [Blocking now](docs/platform/open-questions.md#blocking-now) |
| Product Management: requirements, priorities, timeline, domain answers, the backlog | Roadmap, open questions, glossary, rules | Clear questions, slices, refined stories, the domain meaning of terms and rules | [Roadmap](PROJECT_ROADMAP.md) · [Open questions](docs/platform/open-questions.md) · [Glossary](spec/glossary.md) · [Agile practices](docs/agile-practices.md) |
| Lead Architect: stack, architecture, standards | Decisions, architecture rules | ADRs, technical terms, conventions | [Decisions](docs/adr/README.md) · [Conventions](CLAUDE.md) |
| Software Developer: you build features | The spec area for your slice, conventions | Rules, tests, code, and findings on open questions | [Spec index](spec/INDEX.md) · [Conventions](CLAUDE.md) |

## The map

This table gives each kind of context, the question that it answers, and where it is.

| You want to know… | The answer is in | Where |
|---|---|---|
| What do we build next, and what is done? | The roadmap, in slices (`S6`) | [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) |
| How does the roadmap get to Jira? | The Jira section of the roadmap | [PROJECT_ROADMAP.md#jira](PROJECT_ROADMAP.md#jira) |
| When does the work happen, and what is each meeting for? | Two-week sprints, their meetings, and the Definitions of Ready and Done | [docs/agile-practices.md](docs/agile-practices.md) |
| What does this word mean? | The glossary, and the X12 and billing reference | [spec/glossary.md](spec/glossary.md) · [CDD vocabulary](docs/context-driven-development.md#cdd-vocabulary) |
| What is not decided yet, and who decides? | Open questions (`Q-NNN`) | [docs/platform/open-questions.md](docs/platform/open-questions.md), starting with [Blocking now](docs/platform/open-questions.md#blocking-now) |
| Why is it built this way? | Decisions (ADRs) | [docs/adr/README.md](docs/adr/README.md) |
| What exactly must the system do? | Rules (`eligibility-006`) | [spec/INDEX.md](spec/INDEX.md) |
| What do we try in how we do our work, and what did we learn? | Improvement items (`CI-NNN`) and working agreements, in the local register of the PM | Format: [docs/continuous-improvement.md](docs/continuous-improvement.md) |
| What are the coding conventions? | Conventions (AI assistants read them too) | [CLAUDE.md](CLAUDE.md) |

## Your first hour

1. Read this page.
2. Read [How we do our work](docs/context-driven-development.md): the idea, the lifecycle diagram, and
   your role.
3. Read the [Defined Terms](spec/glossary.md#defined-terms) in the glossary. Words that have
   an exact meaning here cause most confusion.
4. Read [Blocking now](docs/platform/open-questions.md#blocking-now): the questions that stop
   work today, and who owns them.
5. Open the [roadmap](PROJECT_ROADMAP.md). Find a slice with the mark 🟡 (in progress) and read
   its goal.

Then choose one thing that you know about: an open question, a term or a rule. Open a pull
request that makes it clearer. This is the method of CDD.
