---
name: codex-general-explain-changes
description: Explain active Codex implementation work from local repository state, current session context, or generated artifacts. Use when the user invokes /explain-changes, selects Explain Changes from the skill menu, asks what changed and why, wants a concise session summary, asks what changed since the last explanation or heartbeat, wants a guided walkthrough of working-tree or staged changes, requests script/function-level details, or wants follow-up Q&A grounded in available local evidence. Plain /explain-changes should default to session summary mode and use delta behavior when a same-thread baseline exists. Do not use for code review findings, implementation planning, or remote pull request review unless the user explicitly provides the relevant local evidence.
---

# Codex Explain Changes

## Overview

Use this skill to explain what Codex changed, why it matters, and what should be verified next. Plain `/explain-changes` defaults to Session Context Summary mode with delta-if-baseline behavior: explain implementation work across the current visible Codex thread/session context, keep it concise, and report only changes since the last visible explain-changes or heartbeat summary when such a baseline exists.

Prefer repo-backed git evidence when the user asks for a repo/diff scope, names a repo or file, or passes repo/diff options such as `--repo`, `--staged`, or `--since`. When no repo scope is requested, explain from visible session context, tool outputs, generated files, installed artifacts, and user-provided paths.

Treat available local evidence as authoritative. Separate verified facts from inferred rationale. Do not fetch remotes, inspect hosted pull requests, or depend on external review services unless the user explicitly asks and provides the necessary context.

## Command Contract

Support these forms as variants of the same skill:

- `/explain-changes` - default to `--session --summary` plus delta-if-baseline: summarize the current visible Codex thread/session context, and if a prior explain-changes output, heartbeat summary, or explicit baseline exists in this thread, report only meaningful changes since that baseline.
- `/explain-changes --staged` - explain staged changes from `git diff --staged`.
- `/explain-changes --since <ref>` - explain changes from `git diff <ref>..HEAD`.
- `/explain-changes --summary` - provide a concise explanation focused on implementation intent, behavior, plain-language definitions for non-obvious terms, and next verification.
- `/explain-changes --details` - include more file, function, script, data-flow, or validation detail.
- `/explain-changes --delta` - compare current scoped evidence to the last explanation, heartbeat, or user-provided baseline in the current thread; report only meaningful changes since then.
- `/explain-changes --code` - include short code excerpts and explanation anchors.
- `/explain-changes --repo <path>` - explain changes in a specific local repo.
- `/explain-changes --chat` - explain a chat/session implementation when no git repo is available.
- `/explain-changes --session` - explain visible implementation work across the current Codex session context.
- `/explain-changes --artifact <path>` - explain a specific generated file, skill, report, or artifact.

Do not create separate skill entries for these variants.

## Repo-Backed Workflow

1. Identify the repo and scope.
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

## Chat Context Mode

Use this mode by default for plain `/explain-changes`, when no repo diff is available, the user passes `--chat` or `--session`, or the work happened in an open/projectless Codex session. For plain `/explain-changes`, use the shorter summary shape and compare against the last same-thread baseline when available.

Evidence to use:

- visible conversation and user requirements
- tool calls and outputs
- files created or edited in the current workspace
- installed skill files or generated artifacts when the task changed them
- explicit artifact paths from the user

Scope rules:

- `--chat` means the current visible chat and directly referenced artifacts.
- `--session` means the current visible Codex session context.
- Plain `/explain-changes` means `--session --summary` unless the user asks for repo/diff scope.
- Do not claim to summarize unrelated threads, repos, or hidden work.
- If the requested scope is not inspectable from available evidence, ask for the missing path, artifact, or session context.
- If the user asks for "today" or "the whole day", state what evidence is available and ask for the missing session/repo scope when needed.

## Delta Mode

Use `--delta` when the user asks what changed since a prior update, asks for recurring updates, or an automation/heartbeat asks for only changes since the prior run. Plain `/explain-changes` should also behave like delta mode when a same-thread baseline exists.

1. Identify the baseline: prior explanation, heartbeat, user-provided summary, commit, or diff range.
2. Compare current status, diff stat, changed files, relevant hunks, generated artifacts, and validation output.
3. Report only material changes:
   - newly changed files or removed changes
   - changed behavior or data flow
   - changed validation status
   - new failure modes or resolved risks
   - new next steps
4. If nothing material changed, say that directly and avoid a full recap. For automations or heartbeats, return a quiet/no-notify status when the automation protocol supports it.
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
