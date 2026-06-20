---
name: codex-general-explain-changes
description: Explain active Codex implementation work from local repository state, source session context, side-chat/main-thread deltas, or generated artifacts. Use when the user invokes /explain-changes, selects Explain Changes, asks what changed and why, wants a concise session or delta summary, asks what changed since the last explanation/heartbeat/side chat, asks from a side chat for the main/origin implementation delta, wants working-tree/staged walkthroughs, requests code/function-level details, or wants Q&A grounded in local evidence. Do not use for code review findings, implementation planning, or remote pull request review unless the user provides local evidence.
---

# Codex Explain Changes

## Overview

Use this skill to explain what Codex changed, why it matters, and what should be verified next. Plain `/explain-changes` defaults to Session Context Summary mode with delta-if-baseline behavior: explain implementation work across the source implementation context, keep it concise, and report only changes since the last visible explain-changes or heartbeat summary when such a baseline exists. When invoked from a side chat, source implementation context means the main/origin task thread or repo evidence being explained, not the side-chat transcript itself unless the user explicitly passes `--chat` or asks to explain the side chat.

Prefer repo-backed git evidence when the user asks for a repo/diff scope, names a repo or file, or passes repo/diff options such as `--repo`, `--staged`, or `--since`. When no repo scope is requested, explain from visible source-session context, tool outputs, generated files, installed artifacts, and user-provided paths.

Treat available local evidence as authoritative. Separate verified facts from inferred rationale. Do not fetch remotes, inspect hosted pull requests, or depend on external review services unless the user explicitly asks and provides the necessary context.

## Command Contract

Support these forms as variants of the same skill:

- `/explain-changes` - default to `--session --summary` plus delta-if-baseline: summarize the source implementation context, and if a prior explain-changes output, heartbeat summary, side-chat summary, or explicit baseline exists for that source context, report only meaningful changes since that baseline. In a side chat, do not treat side-chat-only messages as the implementation session unless the user asks for `--chat`.
- `/explain-changes --staged` - explain staged changes from `git diff --staged`.
- `/explain-changes --since <ref>` - explain changes from `git diff <ref>..HEAD`.
- `/explain-changes --summary` - provide a concise explanation focused on implementation intent, behavior, plain-language definitions for non-obvious terms, and next verification.
- `/explain-changes --details` - include more file, function, script, data-flow, or validation detail.
- `/explain-changes --delta` - compare current scoped source evidence to the last explanation, heartbeat, side-chat summary, or user-provided baseline for the source implementation context. If only side-chat context is visible, say the main-session baseline is not available and use repo evidence or ask for a baseline instead of declaring no implementation delta.
- `/explain-changes --code` - include short code excerpts and explanation anchors.
- `/explain-changes --repo <path>` - explain changes in a specific local repo.
- `/explain-changes --chat` - explain a chat/session implementation when no git repo is available.
- `/explain-changes --session` - explain visible implementation work across the current Codex session context.
- `/explain-changes --artifact <path>` - explain a specific generated file, skill, report, or artifact.

Do not create separate skill entries for these variants.

## Repo-Backed Workflow

1. Identify the repo and scope.
   - First resolve the source context being explained. In a normal repo chat, this is the current workspace/repo plus visible thread. In a side chat launched from another task, this is the main/origin implementation thread, selected text, forwarded thread summary, timestamped side-chat baseline, or repo evidence tied to that task. The side-chat transcript alone is only the source when the user passes `--chat` or explicitly asks to explain the side chat.
   - If the user asks for a main-session/current-session delta from a side chat and the main/origin thread is not visible or readable, do not answer from side-chat-only context. Fall back to repo-backed evidence when a repo path or current workspace is available; otherwise ask for `--repo <path>`, the prior summary/heartbeat baseline, or the main-thread context.
   - Use repo-backed mode when the user passes `--repo`, `--staged`, or `--since`, names a repo/file path, or clearly asks for working-tree changes.
   - Start with the current working directory and run `git status --short`.
   - Use `git -C <repo> ...` when the user provides `--repo <path>`.
   - If the directory is not a git repo, use Chat Context Mode or ask for the target repo path.
   - Prefer `git diff HEAD` for active uncommitted changes only when repo-backed scope is requested.
   - Use `git diff --staged` only when staged changes are requested.
   - Use `git show <commit>` or `git diff <base>..<head>` only when the user names a commit or range.
   - Do not run `git fetch` as part of this workflow.

2. Build orientation before explaining.
   - Run `git diff --stat` for scope.
   - Inspect relevant hunks with the requested diff command.
   - Group changes into implementation concepts rather than file order.
   - Read post-change files when hunks alone do not explain behavior.
   - Compare against prior visible explanation output for `--delta`.

3. Explain the implementation.
   - Start with the user-visible goal and current state.
   - Explain what changed, why it matters, and what behavior or workflow is affected.
   - Include short code excerpts only when they clarify design, behavior, control flow, data shape, validation, error handling, or tests.
   - Expand non-obvious shorthand the first time it appears. For example, write `provider-mode provenance (the recorded evidence of whether a run was dry-run, live SDK, live search, and which model/search provider was invoked)` instead of only `provider-mode provenance`.
   - Prefer one short definition clause over a glossary unless the user asks for teaching mode, definitions, or educational detail.
   - State inferred rationale as inference, not fact.

4. Connect changes to verification.
   - Name commands already run and what they proved.
   - Name the next focused command or probe when verification is still needed.
   - Do not claim tests, builds, reviews, or deployments passed unless there is current evidence.

## Timestamped Delta Baselines

For `--delta`, recurring updates, heartbeat summaries, and side-chat invocations, create a compact timestamped baseline stamp before comparing changes. Use current local time in ISO 8601 format with timezone when available, such as `date -Iseconds`.

Capture these fields when inspectable:

- `current_time` - timestamp for this explanation run.
- `source_context` - main/origin thread, side chat via `--chat`, repo path, artifact path, or explicit user-provided context.
- `baseline_used` - timestamp and label of the prior visible explanation, heartbeat, side-chat summary, or explicit user-provided baseline. If the prior baseline has no timestamp, label it `untimestamped visible baseline`; do not invent a time.
- `repo_fingerprint` - repo path, branch, HEAD, changed-file list, and diff stat when repo evidence is available. Use `git status --short`, `git diff --stat`, and `git diff --name-status` as needed.
- `validation_state` - relevant tests, checks, or commands that ran since the baseline when visible.

Use side-chat timestamps to order prior and current explanations, but use git/file evidence to decide what code changed. A side-chat summary can be a baseline record; it is not itself proof of code changes unless it contains concrete file, command, or diff evidence.

Include one compact baseline sentence in `--summary`, `--delta`, and recurring outputs, for example: `Baseline: prior heartbeat at 2026-06-18T20:34:23Z; Current: 2026-06-18T20:39:23Z; Source: /path/to/repo; code delta from git diff.` If nothing material changed, say that the timestamp advanced but the repo fingerprint or inspected evidence did not materially change.

## Chat Context Mode

Use this mode by default for plain `/explain-changes`, when no repo diff is available, the user passes `--chat` or `--session`, or the work happened in an open/projectless Codex session. For side-chat invocations, resolve the source implementation context first; do not treat the side-chat transcript as the implementation session unless `--chat` was requested. For plain `/explain-changes`, use the shorter summary shape and compare against the last source-context baseline when available.

Evidence to use:

- visible conversation and user requirements
- tool calls and outputs
- files created or edited in the current workspace
- installed skill files or generated artifacts when the task changed them
- explicit artifact paths from the user

Scope rules:

- `--chat` means the current visible side chat and directly referenced artifacts. Use it only when explicitly requested.
- `--session` means the resolved source implementation session. In a side chat, prefer the main/origin task context, selected text, forwarded summary, readable thread context, timestamped side-chat baseline, or repo evidence over the side-chat wrapper transcript.
- Plain `/explain-changes` means `--session --summary` unless the user asks for repo/diff scope.
- Do not claim to summarize unrelated threads, repos, or hidden work.
- If the requested scope is not inspectable from available evidence, ask for the missing path, artifact, or session context.
- If the user asks for "today" or "the whole day", state what evidence is available and ask for the missing session/repo scope when needed.

## Delta Mode

Use `--delta` when the user asks what changed since a prior update, asks for recurring updates, or an automation/heartbeat asks for only changes since the prior run. Compare the source implementation context, not the side-chat wrapper, unless the user explicitly asks for side-chat context. Plain `/explain-changes` should also behave like delta mode when a source-context baseline exists.

1. Identify the baseline: prior explanation, heartbeat, user-provided summary, commit, or diff range.
2. Create a timestamped baseline stamp, then compare current status, diff stat, changed files, relevant hunks, generated artifacts, and validation output.
3. Report only material changes:
   - newly changed files or removed changes
   - changed behavior or data flow
   - changed validation status
   - new failure modes or resolved risks
   - new next steps
4. If nothing material changed, say that directly and avoid a full recap. Make clear whether only the timestamp advanced, or whether the repo fingerprint/file evidence changed. For automations or heartbeats, return a quiet/no-notify status when the automation protocol supports it.
5. If no baseline is available, say so, provide a normal concise summary, and let that summary establish the baseline for the next run.

## Output Shape

Use this shape for normal repo-backed explanations:

```markdown
## What Changed

<One paragraph summary of the implementation goal and current state.>

## Step 1: <Concept>

Files: `<path>`, `<path>`

Snippet A - `<file>:<function_or_region>`:

```<language>
<short excerpt>
```

Explanation:
<What changed, why it matters, and what behavior or risk it affects.>

## Watch Points

- <Risk, edge case, missing verification, or assumption.>

## Next Verification

- `<command>` - <what it proves>
```

For `--summary`, use fewer sections and fewer excerpts. For `--details`, add function/script-level details where they help. For `--code`, include more short excerpts with stable labels such as `Snippet A` or `Step 2` so the user can ask follow-up questions.

Use this shape for chat-context explanations:

```markdown
## What Codex Implemented In This Session

<One paragraph summary grounded in visible evidence.>

## Artifact: `<path>`

Purpose:
<What this artifact does.>

Key excerpt:

```<language>
<short excerpt>
```

Why it matters:
<How it supports the user request.>

## Verification

- `<command>` - <what it proved>

## Remaining Notes

- <Assumption, limitation, or next manual step>
```

## Safety And Accuracy

- Keep explanations grounded in current local evidence.
- Do not invent motivation, test results, or deployment state.
- Do not expose secrets, credentials, tokens, raw private data, or large sensitive payloads from diffs.
- Avoid pasting full files when a short excerpt and summary will do.
- Do not treat generated artifacts as correct without inspecting the relevant content.
- Do not run destructive commands or external writes while explaining changes.
- If the diff is large, summarize by concept and offer to drill into specific files.

## Handoff

End with:

- what changed
- why it matters
- what was verified
- what remains unverified
- the next best focused check or review step
