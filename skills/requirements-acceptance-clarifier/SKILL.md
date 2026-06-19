---
name: requirements-acceptance-clarifier
description: Convert broad, vague, or risky requests into objective requirements, explicit non-goals, acceptance criteria, and practical verification standards before implementation. Use when the user asks for feature work, refactors, repo improvements, agent/workflow changes, audits that may become implementation, or any task where "do this work" is not enough to prove done. Do not use for tiny mechanical edits, pure Q&A, or tasks with already explicit acceptance criteria.
---

# Requirements Acceptance Clarifier

## Overview

Use this skill before planning or implementation when the request needs clearer done criteria. The goal is to make success observable: what should change, what should not change, what evidence proves it, and where judgment or user confirmation is still required.

## Clarify The Objective

Build a concise requirements packet:

- Objective: the concrete outcome the user wants.
- Users or callers affected: human user, API caller, CLI user, background job, agent workflow, docs reader, maintainer, or downstream system.
- Current state: what exists now, based on repo evidence when possible.
- Desired state: what must be true after the work.
- Non-goals: what should intentionally stay out of scope.
- Constraints: compatibility, performance, cost, security, privacy, data migration, timeline, or repo conventions.
- Unknowns: only the questions that block correctness or safety.

If requirements are discoverable from local code/docs, inspect those first. Ask the user only for decisions that cannot be safely inferred.

## Acceptance Criteria

Write criteria that are specific, observable, and testable. Prefer:

- "Given/when/then" behavior statements for user or workflow behavior.
- Input/output examples for APIs, parsers, CLIs, and data transforms.
- State transition expectations for workflows, jobs, agents, or persistence.
- Error and edge-case expectations, not only happy paths.
- Explicit compatibility expectations when public behavior, schemas, configs, or persisted state are touched.

Avoid acceptance criteria such as:

- "works correctly"
- "improve quality"
- "make it robust"
- "clean up the code"
- "better testing"

Translate those into concrete standards: which behavior, what quality dimension, which failure mode, what test, what measurable output.

## Quality Bar

A requirements packet is strong enough to hand to implementation when it defines:

- Behavior: what users, callers, jobs, agents, or maintainers can observe.
- Boundaries: which APIs, files, workflows, data, or docs are in and out of scope.
- Failure modes: at least the important error, empty, missing-data, permission, retry, or cancellation paths when relevant.
- Compatibility: what existing behavior, schema, config, CLI, persisted state, or docs must keep working.
- Evidence: the practical check that would make each important criterion believable.

If one of these is unknowable from the repo and materially affects the implementation, ask a targeted question instead of guessing.

## Practical Verification Standards

For each acceptance criterion, name the lowest-cost evidence that proves it:

- code inspection for narrow mechanical changes
- focused unit or integration test
- existing regression test
- CLI command or smoke test
- runtime probe, browser check, log/trace check, or API call
- docs grep or generated artifact comparison
- manual review only when behavior cannot be automated reasonably

Tie verification to the repo's actual tools: README, package scripts, Makefile, pyproject, CI, existing test commands, local runbooks, and nearby tests. Do not invent commands.

Use an evidence ladder:

1. Repo evidence: existing tests, code paths, docs, schemas, scripts, logs, fixtures, or CI config.
2. Focused proof: a small test, command, dry run, trace, or fixture check tied to the changed behavior.
3. Broader proof: suites, integration flows, browser/runtime checks, or live/API probes only when the blast radius requires them.
4. Manual judgment: acceptable only when automation would not reasonably prove the criterion.

## Stop Conditions

Stop and ask before implementation when:

- acceptance depends on a product decision
- the change would break documented behavior
- verification would require live writes, expensive API calls, production access, or destructive commands
- user intent conflicts with repo contracts or safety requirements
- there are multiple plausible interpretations with different implementations

## Handoff Shape

Before proceeding to implementation, summarize:

- Objective
- Acceptance criteria
- Non-goals
- Verification plan
- Assumptions or questions

Keep this short. The output should guide implementation, not become a specification document unless the user asks for one.
