---
name: repo-diagnostic-backlog-review
description: Run a diagnostic-only repo review and write numbered backlog tickets for future Codex sessions to fix. Use when the user asks to audit, inspect, walk through, triage, or diagnose a repo for issues; create a repo-level backlog; generate tickets; find future fixes; or record technical debt without changing production code. Do not use when the user asks to immediately fix issues, review only a small diff, or make implementation changes in the same pass.
---

# Repo Diagnostic Backlog Review

## Overview

Use this skill to inspect a repository, identify concrete issues, and record them as actionable repo-level backlog tickets for later Codex sessions. This skill is diagnostic-only: do not apply code fixes, do not refactor, and do not stage or commit changes.

## Scope And Safety

Before reviewing:

1. Read local instructions: `AGENTS.md`, README, contribution docs, architecture docs, CI config, and existing backlog files.
2. Determine the requested scope:
   - whole repo
   - subsystem
   - tests
   - docs
   - dependency/tooling surface
   - runtime/API/agent workflows
3. Prefer evidence-backed findings. Do not create tickets for vague style preferences or speculative rewrites.
4. Keep the pass read-only except for writing the backlog file.

If the user asks to fix items during the audit, separate the work: first write backlog tickets, then ask which ticket to fix or hand off to another session.

## Backlog Quality Bar

Create a ticket only when a future Codex session could act on it without rediscovering the whole repo:

- The issue is tied to concrete repo evidence.
- The impact is clear enough to justify work.
- The suggested fix is bounded and practical.
- The validation path is named.
- The ticket does not depend on an unavailable product decision unless that decision is the ticket.

Prefer fewer high-signal tickets over a long list of speculative cleanup.

## Backlog File Selection

Use an existing repo backlog when clear:

1. `docs/BACKLOG.md`
2. `BACKLOG.md`
3. `TODO.md`
4. `.codex/BACKLOG.md`
5. `.agents/BACKLOG.md`

If none exists, create `.codex/BACKLOG.md` unless local instructions prefer another path. If creating `.codex/BACKLOG.md`, create only the minimal parent directory and file needed.

Do not write backlog items into source files, README prose, issue trackers, or external systems unless the user explicitly asks.

## Ticket ID Rules

Use stable, grep-friendly IDs:

- Prefix: infer from repo name when obvious, otherwise use `CODX`.
- Format: `<PREFIX>-DIAG-###`, for example `KBA-DIAG-001` or `CODX-DIAG-001`.
- Continue the next number from existing matching IDs in the backlog.
- If the backlog already has a different ticket convention, follow the existing convention.
- Never reuse an ID for a different issue.

Before adding a new ticket, scan the existing backlog for duplicates, superseded items, closed items, and related IDs. Add new evidence to an existing open ticket when it is the same underlying issue.

## Diagnostic Categories

Look for issues that a future Codex session can realistically fix:

- Correctness bugs or edge-case failures.
- Test gaps, brittle tests, fake confidence, or missing regression coverage.
- Runtime, CLI, API, schema, state, or config drift.
- Dependency, CI, package script, Docker, or release-surface risks.
- Docs that claim behavior not supported by code.
- Performance, reliability, cleanup, retry, or resource-leak risks.
- Security, privacy, secrets, permission, or untrusted-input issues.
- Maintainability problems with concrete impact, such as duplication, dead code, confusing ownership, or unnecessary abstraction.

Skip:

- personal taste, formatting-only comments, and broad rewrites without evidence
- issues already tracked unless adding materially new evidence
- fixes that require product decisions not available in the repo
- low-value churn that would not improve correctness, reliability, cost, maintainability, or developer efficiency

## Ticket Format

Add tickets under a dated heading such as:

```markdown
## Diagnostic Backlog - YYYY-MM-DD
```

Use this format for each item:

```markdown
### PREFIX-DIAG-001 - Short imperative title

- Status: open
- Severity: high | medium | low
- Area: module, subsystem, tests, docs, tooling, runtime, security, or performance
- Evidence: file paths, symbols, commands, logs, tests, or observed behavior
- Why it matters: concrete user, developer, runtime, cost, or maintenance impact
- Suggested fix: smallest practical fix path
- Validation: focused command, test, probe, or review needed after fixing
- Notes: optional context, constraints, or related tickets
```

Keep each ticket self-contained enough that a fresh Codex session can start from it.

## Review Workflow

1. Build a repo map: major modules, tests, docs, package/config files, CI, and runtime entry points.
2. Select a bounded review slice if the repo is large.
3. Inspect source and tests together; a code concern without test context is often under-specified.
4. Run read-only or low-risk diagnostic commands when useful, such as `rg`, `git status`, `git diff`, `find`, existing list commands, or targeted test discovery. Do not run expensive, live, destructive, or external-write commands without approval.
5. Draft candidate findings.
6. Deduplicate against existing backlog entries.
7. Write only the strongest actionable tickets.
8. Summarize ticket IDs and next recommended fix order.

## Severity Guidance

- High: likely correctness, security, data-loss, broken runtime, major cost, release, or contract risk.
- Medium: important test gap, reliability problem, confusing ownership, docs drift, or maintainability issue with real future cost.
- Low: localized cleanup, minor coverage gap, or polish that is safe to defer.

Do not inflate severity to make the audit look useful.

## Final Handoff

Report:

- Backlog file path used.
- Ticket IDs created.
- Highest-priority ticket to tackle first and why.
- Any scope intentionally left unreviewed.
- Any diagnostic commands run, or state that the pass was file-inspection only.

Do not present backlog entries as fixed work.
