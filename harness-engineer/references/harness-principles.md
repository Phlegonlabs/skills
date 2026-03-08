# Harness Engineering Principles Reference

This document summarizes the core principles of Harness Engineering as practiced by
OpenAI's Codex team and others. It serves as background context for the harness-engineer skill.

## What is Harness Engineering?

Harness engineering is the discipline of designing constraints, feedback loops, documentation
structures, linting rules, and lifecycle management systems that allow AI coding agents to
operate reliably at scale. It is meta-engineering: engineering the environment in which
engineering happens.

The key insight: when an agent makes a mistake, you don't "try harder" — you ask
"what capability is missing?" and engineer a solution so the mistake never recurs.

## The Four Pillars

### 1. Context Architecture (Layered, Progressive Disclosure)

Agents should receive exactly the context they need for their current task — no more, no less.

- AGENTS.md is the table of contents (~100 lines), not the encyclopedia
- Deep knowledge lives in structured docs/ directories
- Design docs, architecture maps, execution plans, and quality grades are all versioned
- A background process should detect stale docs and flag them for cleanup

**Why one big file fails:**
- Context is scarce — a giant file crowds out the actual task
- When everything is "important," nothing is
- Monolithic docs rot instantly and can't be mechanically verified

**Repository knowledge layout:**
```
AGENTS.md              ← table of contents
ARCHITECTURE.md        ← domain map
docs/
├── design-docs/       ← indexed, verified architectural decisions
├── exec-plans/
│   ├── active/        ← current work
│   └── completed/     ← historical context
├── quality/           ← domain quality grades
└── tech-debt/         ← tracked debt
```

### 2. Mechanical Enforcement (Not Suggestions)

Telling agents "don't do X" in markdown is a suggestion. Making X trigger a build failure is a rule.

- Custom linters with remediation instructions baked into error messages
- Strict dependency layers validated by structural tests
- The error output itself becomes agent context
- Enforce boundaries centrally, allow autonomy locally

**Dependency layer example:**
Types → Config → Repo → Service → Runtime → UI

Each layer can only import from layers to its left. A linter enforces this mechanically.

### 3. Plans as First-Class Artifacts

Traditional engineering keeps planning state in Jira, Confluence, Slack threads.
For agent-first development, this is a fundamental flaw — knowledge the agent can't access
in-context is invisible to it.

- Execution plans are versioned repository artifacts
- Lightweight ephemeral plans for small changes
- Structured execution plans with progress and decision logs for complex work
- Active plans, completed plans, and tech debt are all version-controlled and co-located
- Agents working on later tasks can reason about decisions made in earlier tasks

### 4. Feedback Loops and Observability

The harness improves fastest when the agent can see what "good" looks like.

- Make quality metrics available to agents, not just humans
- CI results, test coverage, lint scores feed back into agent context
- Every failure is a signal: identify what's missing and encode it
- AGENTS.md is a living feedback loop, updated iteratively when agents encounter failures

## The Human Role Shift

The engineer's primary output shifts from code artifacts to environment artifacts:
- Documentation structure
- Linter rules
- Merge policies
- Feedback loops
- Architecture enforcement
- Review-system design

The code still gets written. The architecture still gets designed. But humans steer,
and agents execute.

## Practical Starting Point

Audit your repo with this question: can a new agent, with zero context beyond what's in
the repo, find what it needs, follow the architectural rules, and ship working code?

If not, that gap is your backlog.
