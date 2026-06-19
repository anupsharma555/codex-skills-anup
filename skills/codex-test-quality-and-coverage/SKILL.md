---
name: codex-test-quality-and-coverage
description: Write, improve, and review tests so they prove behavior instead of implementation details. Use when adding tests, fixing bugs, changing behavior, improving coverage, reviewing test diffs, or working with weak, flaky, mock-heavy, or low-value tests. Also use for Playwright/Cypress quality review when E2E tests exist. Do not use for production-code-only review or docs-only work.
---

# Test Quality And Coverage

## Overview

Use this skill to make tests valuable, maintainable, and behavior-focused. It should prevent test bloat, fake confidence, brittle mocks, and coverage work that raises numbers without guarding real behavior.

## Workflow

1. Read the repo's test guidance first: `AGENTS.md`, README, test docs, fixtures, helpers, package scripts, CI, and nearby existing tests.
2. Identify the behavior under test and the bug or regression each test should catch.
3. For bug fixes, write or identify a reproduction test that fails before the fix when feasible.
4. Prefer the smallest test level that proves the behavior:
   - unit for pure logic
   - integration for boundaries, persistence, APIs, workflows, and file/network abstractions
   - E2E only for critical user flows that lower-level tests cannot prove
5. Use real value/state objects. Mock only true boundaries such as network, third-party SDKs, external files, time, randomness, databases when persistence is not the subject, or LLM/API calls.
6. Run the focused test first, then the appropriate broader suite or verification skill after edits.

## Test Quality Rules

- Test behavior from the caller's perspective, not internal helper calls.
- Every test should answer: "What bug would this catch that no other test catches?"
- Name tests as requirements or scenarios.
- Prefer DAMP, readable tests over over-DRY shared setup that hides intent.
- Parameterize near-duplicate variants.
- Do not test framework guarantees, constructors, constants, pass-throughs, or type-system guarantees unless project context makes them real behavior.
- Do not skip, weaken, or delete failing tests to make a suite pass.
- Regression tests for real bugs are valuable even when they look narrow.

## Failure Proof And Flake Control

For important tests, especially regression and E2E tests, check that the test would fail for the bug it claims to guard. Use one of these proofs when practical:

- run the test before the fix and observe failure
- reason from a minimal diff or disabled path that the assertion would catch the regression
- assert the externally visible output, state, event, error, or side effect rather than only implementation calls

Reduce flakiness before expanding coverage:

- control time, randomness, order, concurrency, network, and external services
- prefer deterministic fixtures and explicit waits/assertions over sleeps
- keep mocks faithful to provider contracts and failure shapes
- avoid snapshots that hide the behavior under review
- avoid over-broad setup that can make tests pass on the wrong state

## Coverage Work

When asked to improve coverage:

1. Run or inspect the repo's coverage command if available.
2. Prioritize public behavior, risky paths, recent changes, error handling, concurrency, retries, data transforms, and workflow transitions.
3. Propose a concise list of test additions before broad test-writing campaigns.
4. Avoid writing tests just to cover lines that do not encode project behavior.

## E2E Review

When Playwright or Cypress tests exist, check for false confidence:

- Missing `await` on actions or assertions.
- One-shot locator reads instead of framework assertions with retry.
- Hard sleeps, forced clicks, broad exception suppression, and test-only bypasses.
- Tests whose names promise behavior that assertions do not verify.
- Auth or setup gaps that make tests pass on the wrong page.
- Hardcoded credentials or environment-specific assumptions.
