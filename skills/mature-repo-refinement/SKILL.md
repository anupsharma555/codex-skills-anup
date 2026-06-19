---
name: mature-repo-refinement
description: Make small, behavior-preserving improvements to mature repositories so they become slightly more efficient, organized, clean, functional, and easier to maintain without destabilizing working systems. Use when the user asks to polish, tighten, simplify, organize, improve maintainability, reduce small inefficiencies, clean mature code, remove low-risk friction, or make incremental repo improvements without breaking behavior. Do not use for large rewrites, feature builds, speculative architecture redesigns, dependency upgrades, release work, or urgent bug fixes.
---

# Mature Repo Refinement

## Overview

Use this skill for controlled refinement of a repo that already works. The goal is not transformation; it is to make a mature codebase a little clearer, faster, safer, or easier to work in while preserving current behavior.

## Refinement Principles

- Preserve observable behavior unless the user explicitly asks for a behavior change.
- Prefer small, reviewable changes with obvious local benefit.
- Follow existing project patterns before introducing a new abstraction.
- Improve code that has evidence of friction: duplication, confusing ownership, wasteful work, brittle setup, noisy logs, weak names, stale comments, or minor ergonomics problems.
- Avoid churn. Do not rename, move, reformat, or reorganize code unless it directly improves the selected issue.
- Stop before changes become architectural, cross-cutting, or compatibility-sensitive.

## Candidate Selection

Start by reading local guidance, recent diffs, tests, package scripts, and the area the user cares about. Select candidates that satisfy all of these:

- The current behavior is understood from code, tests, docs, or runtime evidence.
- The improvement can be explained in one sentence.
- The affected surface is small enough to review.
- The expected benefit is practical: less duplication, less work per call, clearer flow, better organization, fewer footguns, more useful diagnostics, or easier future edits.
- Verification is available through existing focused tests, commands, compile checks, or inspection.

Good candidates:

- remove dead or unreachable code after confirming no references
- simplify a confusing branch without changing inputs, outputs, errors, ordering, or side effects
- replace repeated local logic with an existing nearby helper
- tighten an inefficient loop, repeated parse, repeated render, or repeated I/O in a hot-enough path
- clarify names or comments where current wording misleads maintainers
- organize small files or helpers to match established local conventions
- add small diagnostics where failures are currently opaque
- add a narrow regression or characterization test before a risky cleanup

Poor candidates:

- broad formatting or folder reshuffles
- new frameworks, dependency upgrades, or package-manager changes
- speculative base classes, adapters, service layers, or plugin systems
- compatibility shims without a current caller
- behavior changes hidden inside cleanup
- deleting code only because it looks unused without reference checks
- optimizing code without evidence that the path matters

## Workflow

1. Inspect first: read the target files, adjacent tests, callers, and local conventions.
2. Identify one to three refinement candidates and choose the smallest highest-confidence one.
3. State the preservation contract: inputs, outputs, errors, side effects, state, ordering, public API, docs, and performance expectations that must not regress.
4. Make one coherent refinement at a time.
5. Review the diff for accidental behavior change, hidden scope growth, and user-owned changes.
6. Verify with the smallest relevant check, then broaden only if the changed surface warrants it.
7. Stop when the repo is slightly better; do not keep hunting for extra cleanup unless asked.

## Behavior Preservation Checks

Before final handoff, compare old and new behavior for the touched path:

- public function signatures, CLI flags, route names, schemas, env/config keys, and documented examples
- return values, exceptions, logs, retries, persistence, file writes, network calls, and ordering
- tests and fixtures that encode current behavior
- user-facing UI text, layout, accessibility semantics, or generated artifacts when applicable
- concurrency, caching, cleanup, idempotency, and resource ownership when relevant

For refactors with meaningful risk, add or run a characterization test first. If the characterization reveals existing broken behavior, separate that bug from the cleanup and ask or create a backlog item before changing behavior.

## Stop Conditions

Stop and ask or switch skills when:

- the refinement requires a product decision or intended behavior change
- the change touches public contracts, migrations, dependency surfaces, release automation, or live systems
- tests are missing and behavior cannot be verified by inspection or a small probe
- the cleanup would span many modules or create merge-conflict risk
- an issue is real but too broad for this pass; use `repo-diagnostic-backlog-review` instead

Use `implementation-strategy` for compatibility-sensitive planning, `code-review-and-quality` for review findings, `test-quality-and-coverage` for meaningful test additions, and `repo-change-verification` before claiming completion.

## Handoff

Report:

- The refinement target and why it was worth changing.
- The behavior preservation contract.
- What changed in practical terms.
- What verification was run and what it proved.
- Any broader cleanup or risky issue intentionally left for a later ticket.
