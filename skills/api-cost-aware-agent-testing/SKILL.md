---
name: api-cost-aware-agent-testing
description: Plan and run cost-aware API or agent testing by exhausting non-API diagnostics before live calls, testing one agent or workflow at a time, fixing between runs, monitoring OpenAI billing/usage, and escalating from fixtures to tightly bounded live tests only after max offline diagnosis is complete. Use when Codex is asked to test OpenAI/API-backed agents, LLM workflows, tool-calling agents, multi-agent systems, evals, smoke tests, or live SDK behavior with cost control. Do not use for purely local unit tests, UI-only testing, or non-API code review.
---

# API Cost-Aware Agent Testing

## Overview

Use this skill to reduce API spend while still getting high-quality diagnostic coverage for agent systems. The default posture is: diagnose offline first, test one agent at a time, fix between stages, check costs before and after live runs, and only broaden live testing when narrower evidence is clean.

## Required Testing Ladder

Do not jump straight to broad live API tests. Progress in this order:

1. Static and contract review, no API calls.
2. Local unit tests, parser tests, schema tests, fixture tests, replay tests, and mocked provider tests.
3. Single-agent local dry run with API calls disabled or stubbed.
4. Single-agent live smoke test with the smallest useful input and explicit budget.
5. Single-agent diagnostic expansion, still bounded by call count, tokens, model, and tool scope.
6. Multi-agent or end-to-end live test only after individual agents are understood and fixed.

Stop after each stage to inspect failures and fix broad root causes before spending on the next stage.

## Before Any Live API Call

Confirm all of the following:

- The user has asked for or approved live API testing.
- The repo has no obvious static, fixture, schema, config, or environment issues left to fix.
- The exact agent, workflow, prompt, model, input, tool set, and expected output surface are identified.
- A maximum spend, maximum call count, or maximum run count is set. If the user did not provide one, ask before live testing.
- The smallest useful model, input size, output limit, and tool scope have been selected.
- Logging is ready: command, timestamp, model, prompt/input source, run id or trace id when available, observed result, token/cost evidence when available.

If any item is missing, do not run live tests yet.

## Budget Gate

Use an explicit live-test budget before the first API call:

- hard stop: maximum dollars, calls, runs, or tokens
- scope: agent/workflow, model, tools, input fixture, and output limit
- reason: what offline evidence has already been exhausted
- expected diagnostic value: what one live run can prove that mocks or fixtures cannot
- stop condition: what result ends the stage or requires user approval to continue

If the user did not provide a budget and live calls are necessary, ask for one. When only a tiny smoke run is needed, propose the smallest bounded budget instead of choosing silently.

## Billing And Usage Checks

Use current billing/usage evidence, not memory. The preferred billing page is:

https://platform.openai.com/settings/organization/billing/overview

Before live testing:

- Check current billing/usage when browser or platform access is available.
- If platform access is unavailable, ask the user for the current usage/cost snapshot or proceed only with an explicit small budget.
- Record the starting observation in the work notes or final summary.

During testing:

- Keep live runs serial, not parallel.
- Check billing/usage after any unexpectedly expensive run, repeated failure, model/tool change, or expanded diagnostic stage.
- Stop immediately if costs move faster than expected or the platform indicates quota/budget pressure.

After live testing:

- Re-check billing/usage when possible.
- Report live call count, models used, test scope, observed cost/usage if available, and any uncertainty.

## Diagnostic Workflow

For each agent or workflow:

1. Map dependencies: prompts, tools, schemas, config, env vars, fixtures, state, persistence, and external services.
2. Run no-API checks first:
   - import/compile/type checks
   - schema validation
   - prompt/template rendering
   - tool contract tests
   - fixture/replay tests
   - dry-run commands
   - fake provider or mocked SDK tests
3. Fix broad failures before live calls. Examples: wrong env key, bad schema, malformed prompt, missing tool registration, invalid state transition, broken parser, or fixture drift.
4. Run one live agent smoke test.
5. Inspect full evidence from that run before moving on: response, tool calls, traces/logs, state writes, errors, retries, and cost signal.
6. Fix the broadest root cause that explains the failure.
7. Repeat on the same agent until it is clean or the budget/stop condition is reached.
8. Move to the next agent only after the previous agent has useful diagnostic evidence.

Keep a run ledger during live testing:

- agent/workflow and scenario
- command or script
- model and tool scope
- call/run count
- observed result, trace id, or log path
- cost/usage observation when available
- fix or decision made before the next run

## Live Test Cost Controls

Prefer:

- one agent at a time
- one scenario at a time
- one input fixture at a time
- low token limits for diagnostic runs
- disabled optional tools
- deterministic or narrow prompts
- mocked expensive tools
- replayed external search/data where acceptable
- saved traces/logs so failures are not rerun unnecessarily

Avoid:

- broad eval suites before single-agent checks pass
- parallel live runs
- repeated "try again" calls without a code/config change
- high-token prompts when a reduced fixture proves the issue
- live web/search/tool calls when fixture data can isolate the failure
- testing multiple agents after a shared root cause is already visible

## Final Handoff

Report:

- Offline checks run and what they proved.
- Live tests run, one agent/workflow at a time.
- Fixes made between test stages.
- Billing/usage checks performed, including the platform link or reason direct billing evidence was unavailable.
- Remaining risks, untested agents, stop conditions hit, and recommended next bounded test.
