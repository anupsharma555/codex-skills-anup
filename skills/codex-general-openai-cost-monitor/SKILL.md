---
name: codex-general-openai-cost-monitor
description: Monitor OpenAI API costs, usage, credit balance, billing drift, or unexpected API spend during live workflows. Use when Codex is asked to baseline, poll, watch, compare, or diagnose OpenAI API billing/usage; to monitor spend while work runs; to check whether API calls are unexpectedly decreasing credits; or to use the OpenAI billing platform, Admin Costs API, Admin Usage API, Chrome billing tab, OPENAI_ADMIN_KEY, or OPENAI_API_KEY for cost monitoring. Do not use for general agent testing unless the task is specifically about cost or usage monitoring.
---

# OpenAI Cost Monitor

## Overview

Use this repo-agnostic skill to baseline and monitor OpenAI API spend so workflows are not blindsided by unexpected calls. Prefer structured Admin API snapshots when `OPENAI_ADMIN_KEY` is available; use the billing website in Chrome only as a fallback or independent visual check.

Use it for any repo or workflow that can trigger OpenAI API calls, including linked repos where one workflow can indirectly start API usage in another service.

## Source Priority

Use sources in this order:

1. Admin Costs API: `GET https://api.openai.com/v1/organization/costs` with `OPENAI_ADMIN_KEY` for dollar-denominated daily spend.
2. Admin Usage API: use `GET https://api.openai.com/v1/organization/usage/completions` with `bucket_width=1m` when session-level request/token movement is needed.
3. Chrome billing overview: use `https://platform.openai.com/settings/organization/billing/overview` when Admin API access is unavailable, the user asks for visual confirmation, or the billing page is the only authenticated source.

Admin costs and usage endpoints are metadata reads, not model inference calls. There is no official indication in the API pricing surface that these reads are billed as model/token usage. Keep polling conservative anyway to avoid rate limits and noisy diagnostics.

## Default Workflow

1. Confirm monitoring scope: organization-wide unless the user asks for a project, key, line item, repo, or linked workflow slice.
2. Take a baseline cost snapshot before risky or live work.
3. During active work, poll after known live-call stages or every 2 minutes in watch mode, unless an API, browser, or user-imposed time gap requires a slower cadence.
4. Flag any unexpected nonzero delta.
5. Label cost interval deltas by default: early at `$0.25`, medium at `$0.50`, and late at `$1.00`.
6. End with baseline, final observed cost, delta, source used, grouping, and uncertainty.

These labels are spend stop-gaps, not failure states. When a poll emits `interval_flag`, pause before initiating additional OpenAI API calls and ask the user whether the observed spend or usage is acceptable. Continue only after the user explicitly okays the flagged spend. Treat `early`, `medium`, and `late` as escalating urgency levels; treat `nonzero` usage movement as a prompt to confirm whether expected API activity occurred.

When running watch mode, align user-facing Codex updates with actual poll returns. Report each completed poll with observed requests/tokens or cost delta and any flag. Avoid filler status updates between polls unless the monitor errors, stalls, or the user asks for status.

Do not run high-frequency polling. Do not parallelize live OpenAI spend checks with live model workflows unless the user explicitly asks for continuous monitoring.

## Script

Use `scripts/openai_cost_monitor.py` for structured snapshots:

```bash
OPENAI_ADMIN_KEY=... python3 scripts/openai_cost_monitor.py --days 1
OPENAI_ADMIN_KEY=... python3 scripts/openai_cost_monitor.py --watch --max-polls 10
OPENAI_ADMIN_KEY=... python3 scripts/openai_cost_monitor.py --source usage-completions --minutes 10
OPENAI_ADMIN_KEY=... python3 scripts/openai_cost_monitor.py --source usage-completions --watch --max-polls 10
OPENAI_ADMIN_KEY=... python3 scripts/openai_cost_monitor.py --group-by project_id --json
```

The script reads `OPENAI_ADMIN_KEY` from the environment. Never print, log, commit, or paste the key into repo files, skill files, docs, tests, examples, command output, or final responses.

In watch mode, a flagged interval exits with status `2` by default so the caller can pause and ask for user approval. Use `--continue-after-flag` only when the user explicitly wants passive monitoring without an approval gate.

## Interpreting Results

- Use total organization cost for spend drift detection, but remember costs may appear as daily buckets and can lag short sessions.
- Use `--source usage-completions --bucket-width 1m` for session-level request and token movement. One-shot usage snapshots default to the latest 10 minutes; watch mode anchors near watch start so deltas reflect new activity.
- Use `--group-by project_id`, `--group-by api_key_id`, or `--group-by line_item` to localize an unexpected delta.
- Treat zeros or unchanged totals as "no observed cost movement from this source," not proof that no usage occurred.
- If the Admin Costs API lags behind recent calls, cross-check Admin Usage API or the billing page before declaring the workflow quiet.
- For repo-specific workflows, check the repo's environment conventions before assuming which API key or project is active. Monitor direct OpenAI API spend separately from any non-OpenAI provider costs.

## Chrome Fallback

When using Chrome:

1. Use the Chrome browser skill and claim or open the billing overview page.
2. Record the visible balance, usage, credit, or billing total and timestamp.
3. Refresh only at the agreed cadence or at stage boundaries.
4. Report that the value is page-derived and may lag or omit API grouping details.

Do not inspect cookies, local storage, session stores, passwords, or browser secrets.
