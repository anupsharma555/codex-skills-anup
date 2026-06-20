---
name: codex-general-subagent-task-orchestration
description: Orchestrate Codex subagents for broad repo work, multiple identified issues, parallel review or investigation, and disjoint implementation slices that hand results back to the main agent. Use when the user explicitly asks for subagents, delegation, parallel agent work, a swarm, multiple workers, broad multi-issue fixing, or a main-agent handoff after delegated work. Do not use for small single-file edits, ordinary local review, or when the user has not authorized subagent/delegated work.
---

# Subagent Task Orchestration

## Overview

Use this skill when subagents can materially speed up or improve a broad task without losing main-agent control. The main agent remains responsible for scope, delegation design, integration, validation, and final user-facing handoff.

## Non-Negotiable Rules

- Spawn subagents only when the user explicitly asks for subagents, delegation, parallel agent work, a swarm, multiple workers, or broad multi-issue work.
- Do not delegate vague ownership. Every subagent needs a concrete, self-contained task.
- Do not duplicate work between subagents or between a subagent and the main agent.
- The main agent owns synthesis and final decisions.
- The main agent validates the integrated result before final response.
- For code-editing workers, assign disjoint files, modules, or responsibilities to avoid conflicts.
- Tell workers they are not alone in the codebase and must not revert or overwrite unrelated changes.
- Treat subagent output as input evidence, not as final truth.

## Delegation Quality Bar

Before spawning subagents, define:

- Objective: what the whole delegation should accomplish.
- Work partition: which files, modules, issues, hypotheses, or review axes each worker owns.
- Boundaries: what each worker must not edit or decide.
- Evidence expected: findings, proofs, commands, traces, changed paths, or validation output.
- Integration plan: how the main agent will merge, reject, or sequence results.
- Stop condition: when to stop delegation and return control to the main agent.

If these cannot be defined clearly, do the work in the main session first until the task can be sliced safely.

## Choose A Mode

### Mode 1: Parallel Read-Only Review

Use for large diffs, risky changes, regression review, broad quality review, security/privacy review, performance review, or contract/test coverage review.

Subagents should be read-only. They must not edit files, run `apply_patch`, stage, commit, push, or perform state-mutating actions.

Useful roles:

- Intent and regression: does the change match the intended behavior without extra drift?
- Security and privacy: are trust boundaries, secrets, permissions, or untrusted inputs mishandled?
- Performance and reliability: are hot paths, cleanup, retries, ordering, or resource usage risky?
- Contracts and coverage: are APIs, schemas, config, migrations, docs, or tests incomplete?

Expected subagent output:

- finding
- file and line or nearest symbol
- why it matters
- recommended fix
- confidence

### Mode 2: Parallel Root-Cause Investigation

Use for bugs, regressions, crashes, flaky behavior, unexplained failures, or unclear root causes.

Subagents should normally be read-only until the main agent has a ranked diagnosis. Give every investigator the same bug packet:

- symptom
- expected behavior
- actual behavior
- known reproduction steps
- relevant logs, traces, screenshots, failing tests, recent diffs, or environment details
- what evidence would prove the diagnosis

Useful roles:

- Reproduction and scope: narrow the exact trigger and impact.
- Code path and data flow: trace where behavior diverges.
- Recent change and contract drift: identify likely regressors.
- Proof plan and observability: find the smallest confirming test, command, log, or trace.

Expected subagent output:

- hypothesis
- supporting evidence
- missing or conflicting evidence
- smallest proof step
- confidence

### Mode 3: Disjoint Worker Fixes

Use when there are multiple known issues or broad implementation slices that can be fixed independently.

Before spawning workers:

1. List the issues or slices.
2. Group them by file/module ownership.
3. Identify dependencies between slices.
4. Delegate only independent slices in parallel.
5. Keep shared interfaces, schemas, public contracts, and cross-cutting decisions with the main agent unless a worker is assigned that exact ownership.

Worker prompt requirements:

- State the owned files, modules, or responsibility.
- State files or modules the worker must not edit.
- Tell the worker not to revert others' changes.
- Ask the worker to edit directly in its forked workspace when code changes are intended.
- Ask for a final report with changed paths, behavior changed, validation run, and remaining risks.

Do not ask two workers to edit the same files unless one is explicitly sequentially following the other.

## Main-Agent Integration

After subagents return:

1. Read all outputs before acting.
2. Merge duplicates and discard weak, speculative, or instruction-conflicting results.
3. Resolve conflicts using repo evidence, not voting.
4. Apply or integrate fixes in the main workspace when needed.
5. Inspect changed files yourself before validation.
6. Run the smallest relevant validation first, then broader checks if the blast radius requires it.
7. Summarize what came from subagents, what the main agent changed, and what remains open.

If a worker returns patches or file changes, review them like external contributions. Do not assume correctness because the worker completed.

Watch for integration hazards:

- duplicate or conflicting edits
- inconsistent assumptions across workers
- changes to shared contracts made without main-agent approval
- tests run in only a worker workspace but not against the integrated result
- speculative findings without file-level evidence
- workers fixing symptoms while another worker found a broader root cause

## Handoff Format

End with a compact handoff:

- Delegation: which subagents ran and what each owned.
- Integrated result: what was accepted, changed, or rejected.
- Validation: commands or checks run and what they prove.
- Remaining risk: unresolved questions, deferred issues, or next bounded task.

For review-only or investigation-only runs, do not present unimplemented fixes as completed work.

## When Not To Use Subagents

Do not spawn subagents when:

- The task is a small direct edit.
- The work has one obvious code path and little ambiguity.
- The task requires sensitive live credentials or production mutation without explicit approval.
- Parallel edits would likely conflict.
- You do not have enough scope to give self-contained assignments.
- Waiting for subagents would be slower than doing the work directly.
