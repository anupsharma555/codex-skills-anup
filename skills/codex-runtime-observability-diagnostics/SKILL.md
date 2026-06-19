---
name: codex-runtime-observability-diagnostics
description: Inspect, design, or improve logs, tracebacks, traces, metrics, health checks, receipts, and runtime diagnostic evidence so failures are explainable and verification is practical. Use when debugging runtime behavior, exceptions, stack traces, background jobs, services, CLIs, APIs, agents, tool calls, dashboards, scheduled tasks, or delivery workflows; when logs/traces are missing, noisy, misleading, or not actionable; or before adding observability around new runtime behavior. Do not use for pure static code review, test-only changes, or docs-only edits.
---

# Runtime Observability Diagnostics

## Overview

Use this skill when runtime behavior must be diagnosable from logs, traces, metrics, receipts, or health checks. Good observability should answer: what happened, where, for which input/run, how long it took, what failed, what was retried, what was skipped, and what the operator should inspect next.

## Diagnostic Questions

Start by identifying the questions the evidence must answer:

- Did the workflow start, skip, fail, retry, or complete?
- Which run, request, job, user action, file, record, or agent step does this evidence describe?
- Which dependency or tool was called, with what safe summary of input?
- What decision was made and why?
- What state changed, if any?
- What error occurred, with enough context to reproduce or localize it?
- What should the operator do next?

Do not add logs just because a code path is complex. Add evidence where it changes diagnosis.

## Observability Standards

Prefer structured, grep-friendly fields when the repo supports them:

- event name
- run/request/job id
- component or agent name
- operation
- status: started, skipped, succeeded, failed, retried
- duration
- safe input summary
- dependency/tool name
- error type and safe message
- next diagnostic hint

For traces, preserve parent/child relationships across agents, tools, background tasks, and external calls when available. For user-facing receipts, include enough status and source information to reconcile visible output with backend logs.

## Noise And Safety

Avoid:

- logging secrets, tokens, API keys, cookies, credentials, raw personal data, or full prompts unless explicitly safe
- logging huge payloads, full documents, or unbounded API responses
- duplicate logs at every wrapper layer
- success logs that omit the item or run they refer to
- catch-all error logs that discard stack traces or root cause
- misleading "success" messages before durable work actually succeeds

Use redaction, hashes, counts, ids, and short summaries when full values are unsafe or noisy.

## Traceback Evaluation

When a traceback, stack trace, exception chain, crash log, or async task failure appears, evaluate it before changing code:

1. Preserve the full traceback text and command or runtime context that produced it.
2. Identify the exception type, message, and top-level operation that failed.
3. Find the first repo-owned frame where behavior diverges. Do not stop at framework, SDK, runner, or wrapper frames unless they are the actual integration point.
4. Walk upward and downward through the stack to distinguish root cause from symptom.
5. Correlate the traceback with run id, request id, job id, agent/tool name, input fixture, environment, and recent code/config changes when available.
6. Check whether this is deterministic, data-dependent, race/order-dependent, retry-related, or environment-specific.
7. Prefer the smallest proof step: a focused test, minimal command, reduced fixture, or replay that reproduces the first repo-owned failure boundary.
8. Add or recommend missing diagnostic context only where it would shorten the next traceback diagnosis.

Avoid:

- rerunning repeatedly without a hypothesis or code/config change
- masking the traceback with broad exception handling
- logging secrets or full payloads while trying to add context
- treating the last line of the traceback as the root cause without inspecting caller state
- fixing only the crashing line when the stack shows a broken external contract

## Real-Time Traceback Triage

For an active failure, keep the loop short and evidence-driven:

1. Capture the failing command, timestamp, environment, branch/commit, and full traceback.
2. Summarize the failure in one line: operation, exception type, message, and first repo-owned frame.
3. State the current hypothesis and the single proof step that will confirm or reject it.
4. Make one targeted fix or instrumentation change at a time.
5. Rerun the smallest reproducer, then compare the new traceback/logs with the prior one.
6. If the error moves, record what boundary was cleared and continue from the new first failing repo-owned frame.
7. If the error stays the same after a targeted change, revisit the hypothesis before adding more changes.

Use this compact traceback handoff when another session or agent needs to continue:

- `failure`: command or workflow, status, exception type, and message
- `first_repo_frame`: file, function, line, and why it matters
- `correlation`: run/request/job id, agent/tool name, input fixture, and relevant environment
- `hypothesis`: likely root cause versus visible symptom
- `proof`: smallest reproducer or check already run
- `next_step`: one concrete diagnostic or fix action

## Debugging Workflow

When diagnosing an existing failure:

1. Find the entry point, run id, job id, request id, or visible receipt.
2. Trace the path across tracebacks, logs, state, tool calls, retries, and outputs.
3. Identify the first point where expected and actual behavior diverge.
4. Note missing evidence that would have made the diagnosis faster.
5. Add or recommend the smallest useful diagnostic signal.
6. Verify the new signal appears on success, failure, and skip paths as appropriate.

When adding observability for new behavior:

1. Define what operators will need to know after the feature runs.
2. Add diagnostics at boundaries, decisions, external calls, and state changes.
3. Keep log levels meaningful: debug for details, info for lifecycle, warning for recoverable anomalies, error for failed outcomes.
4. Ensure tests or smoke checks can assert important diagnostic output when practical.

## Handoff

Report:

- What diagnostic question was addressed.
- Which tracebacks/logs/traces/metrics/receipts were inspected or changed.
- What fields or correlation ids now make diagnosis possible.
- What sensitive data was intentionally not logged.
- What remains hard to diagnose and the next observability improvement.
