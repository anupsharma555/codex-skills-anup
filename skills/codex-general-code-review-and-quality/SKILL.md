---
name: codex-general-code-review-and-quality
description: Review code for correctness, maintainability, simplicity, performance risk, security basics, and AI-specific failure modes. Use after implementation, before merge or handoff, when reviewing a diff, when simplifying or refactoring code, or when the user asks for a code review, cleanup, or safer implementation. Do not use for pure docs, test-only review, dependency-only review, or conceptual questions.
---

# Code Review And Quality

## Overview

Use this skill as the judgment layer around implementation code. It should catch real bugs, behavior drift, unnecessary complexity, inefficient paths, poor boundaries, dead code, and common agent-generated failure modes.

## Modes

- Guard pass: after writing code, inspect your diff before presenting it.
- Review mode: when the user asks for review, lead with findings and do not edit unless asked.
- Simplify mode: when cleaning or refactoring, preserve observable behavior exactly and separate bug fixes from refactors.

## Review Axes

Prioritize evidence-backed issues over style preferences:

1. Correctness: requirements match, edge cases handled, errors are not swallowed, state remains consistent.
2. Readability: names reveal intent, control flow is direct, comments explain why rather than what.
3. Architecture: follows local patterns, respects module boundaries, avoids circular dependencies and needless abstractions.
4. Simplicity: no speculative flags, factories, interfaces, compatibility shims, or helpers without a present caller.
5. Performance: no obvious N+1 patterns, unbounded loops, repeated expensive work, unnecessary rendering, or missing pagination.
6. Security basics: no secrets, injection risks, missing auth checks, unsafe external data handling, or unchecked file/network boundaries.
7. AI failure modes: no hallucinated APIs, broad catch-all success, hardcoded "ok" returns, fake fixtures in production, disabled tests, or dead code left behind.

## Guard Pass Checklist

- Read the edited file and at least one neighboring file before judging style.
- Verify external APIs or library methods against installed code, lockfiles, or official docs when uncertain.
- Confirm new abstractions have a current second use or a clear boundary reason.
- For refactors, compare observable behavior: inputs, outputs, exceptions, side effects, ordering, and persistence.
- Remove unused imports, unreachable branches, obsolete comments, and scaffolding left from earlier attempts.
- If you find a possible bug during a refactor, flag it separately before changing behavior.

## Severity And Evidence

Use severity based on impact, not taste:

- Critical: likely data loss, security/privacy breach, broken production path, corrupt state, or release-blocking regression.
- Important: correctness bug, contract drift, meaningful reliability/performance issue, or missing guard for changed behavior.
- Suggestion: maintainability, simplification, or coverage improvement with concrete future cost.
- Nit: local clarity or polish that should not block the work.

Every finding should include evidence: file/line or symbol, the failing scenario or affected caller, why the behavior is risky, and the smallest practical fix. Do not report broad rewrites, style preferences, or speculative architecture opinions as findings.

## Fix Or Backlog

In implementation mode, fix review issues immediately only when they are clearly inside the requested scope and the correction is low-risk. For real but out-of-scope issues, record them separately or use `codex-general-repo-diagnostic-backlog-review` when the user wants a repo-level backlog. Do not silently expand the task into unrelated cleanup.

## Review Output

In review mode, lead with findings:

- Severity: Critical, Important, Suggestion, or Nit.
- Location: file and line when available.
- Risk: what can break or degrade.
- Fix: the smallest practical correction.

If there are no findings, say that clearly and mention remaining verification gaps. Avoid "LGTM" without evidence.

In implementation mode, fix issues before final handoff when the fix is clearly in scope. Do not broaden the task into unrelated cleanup.
