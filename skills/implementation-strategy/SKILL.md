---
name: implementation-strategy
description: Plan scoped, contract-safe implementation before editing code. Use when a task changes public APIs, runtime behavior, schemas, persisted state, CLI flags, environment variables, config, tests, docs, examples, agent/tool contracts, or larger multi-file behavior. Do not use for tiny obvious edits, pure formatting, or simple read-only questions.
---

# Implementation Strategy

## Overview

Use this skill before implementation to decide what boundary is changing, what must stay compatible, and how to slice the work into verifiable steps. The output should make the edit smaller, safer, and easier to verify.

## Workflow

1. Read local guidance first: `AGENTS.md`, README, nearby docs, existing tests, schemas, route definitions, package scripts, and files adjacent to the likely edit.
2. Identify the surface being changed:
   - released or documented public API
   - runtime behavior
   - persisted state, schema, cache, or serialized data
   - wire protocol, CLI flag, environment variable, config key, or workflow contract
   - tests, docs, examples, fixtures, or internal helper only
3. Decide the compatibility boundary:
   - Preserve released or documented external behavior unless the user explicitly wants a breaking change.
   - Update branch-local or unreleased interfaces directly instead of adding shims.
   - Treat durable state and cross-process contracts as compatibility-sensitive even when they are not formal public APIs.
4. Prefer the simplest implementation that satisfies the current task. Avoid feature flags, adapters, migrations, dual paths, base classes, and generic frameworks unless a current caller or compatibility boundary requires them.
5. Break the work into small steps with acceptance criteria and verification. For larger work, favor vertical slices that leave the repo runnable after each checkpoint.
6. Identify open questions only when they block correctness or safety. Otherwise proceed with the smallest defensible assumption and state it.

## Strategy Quality Bar

A useful implementation strategy should answer:

- What exact behavior or contract is changing?
- Which existing callers, workflows, persisted data, docs, or tests could be affected?
- What is the smallest implementation that satisfies the acceptance criteria?
- What must be preserved for compatibility?
- What could fail during rollout, verification, or rollback?
- What evidence will prove the final state?

If acceptance criteria are missing or subjective, use `requirements-acceptance-clarifier` before editing. If the change is tiny and the answers are obvious from the code, keep the strategy implicit and proceed.

## Risk Slicing

Treat these as higher-risk slices that deserve explicit sequencing:

- public APIs, schemas, CLIs, env/config keys, migrations, persisted state, or generated artifacts
- authentication, authorization, secrets handling, payments, billing, or external writes
- agent/tool contracts, prompts, evals, retries, background jobs, or scheduled workflows
- dependency, CI, Docker, deployment, release, or package-manager changes
- broad refactors across shared utilities or framework entry points

For high-risk slices, plan the reversible order: inspect, add/adjust focused guard, make the narrow change, verify locally, then expand checks. Do not mix unrelated cleanup with contract changes.

## Output Shape

For non-trivial tasks, produce a short plan before editing:

- Boundary: what is changing and whether it is compatibility-sensitive.
- Approach: the smallest implementation path.
- Files likely touched: only when useful for coordination.
- Verification: commands, tests, runtime checks, or manual checks expected to prove the change.
- Stop conditions: cases where user confirmation is required.

Keep the plan concise. Do not turn simple edits into ceremony.

## Stop And Confirm

Ask before editing when:

- The change would intentionally break documented external behavior.
- The task requires data migration, destructive cleanup, live writes, or production-affecting changes.
- Requirements are contradictory or missing a decision that cannot be discovered from the repo.
- The user asked for a plan/review only.
