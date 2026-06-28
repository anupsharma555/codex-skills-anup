# Codex Skills Anup

Author: Anup Sharma, MD PhD (Keystone Neuroinformatics)

This repository contains clean, general-purpose Codex skills for improving software projects across different repositories. The skills are intentionally repo-agnostic and do not depend on any project-specific codebase.

The goal is to give Codex reusable operating procedures for planning, implementation quality, testing, verification, runtime diagnostics, safe handoffs, and incremental repo refinement.

See [docs/lifecycle.md](docs/lifecycle.md) for the compact lifecycle view.

## Menu Prefix

In Codex, type `$codex-general` to find these general skills in the skill menu.

## Included Skills

### `codex-general-requirements-acceptance-clarifier`

Use before implementation when a request is broad, vague, risky, or hard to verify. It turns intent into objective requirements, non-goals, acceptance criteria, and practical verification standards.

### `codex-general-implementation-strategy`

Use before non-trivial code changes. It identifies the compatibility boundary, affected contracts, implementation approach, risk slicing, and verification plan before editing.

### `codex-general-mature-repo-refinement`

Use for small, behavior-preserving improvements in mature repositories. It helps Codex make code slightly cleaner, more efficient, better organized, or easier to maintain without hidden behavior changes.

### `codex-general-code-review-and-quality`

Use during or after implementation to review code for correctness, simplicity, maintainability, performance risk, security basics, and common AI-generated failure modes.

### `codex-general-test-quality-and-coverage`

Use when adding, improving, or reviewing tests. It emphasizes tests that prove behavior, avoid fake confidence, reduce flakiness, and catch real regressions.

### `codex-general-runtime-observability-diagnostics`

Use when runtime behavior must be diagnosable from logs, tracebacks, traces, metrics, health checks, receipts, or runtime probes. It includes real-time traceback triage guidance.

### `codex-general-storage-diagnostics`

Use when diagnosing repository storage footprint, file/folder counts, large paths, file-count hotspots, generated artifacts, dependency caches, build outputs, logs, reports, and other possible bloat without changing files.

### `codex-general-window-placement`

Use when opening, placing, inspecting, or verifying visible macOS app and browser windows across the laptop display and external monitors. It supports Magnet-style regions, live monitor geometry, and dimension-first placement verification.

### `codex-general-api-cost-aware-agent-testing`

Use when testing API-backed or agentic workflows where live calls may cost money. It requires offline diagnostics first, one-agent-at-a-time testing, explicit budgets, and billing/usage checks where available.

### `codex-general-openai-cost-monitor`

Use when monitoring OpenAI API spend or usage drift during live workflows. It supports Admin Costs snapshots, Admin Usage completion buckets, two-minute watch mode, and approval stop-gaps for unexpected spend movement.

### `codex-general-repo-change-verification`

Use after changes to prove the current repo state before handoff. It helps Codex discover the right local checks, run focused validation, debug failures, and report what remains unverified.

### `codex-general-supply-docs-release-guard`

Use for high-blast-radius surfaces: dependencies, lockfiles, package scripts, CI, Dockerfiles, docs claims, config docs, changelogs, releases, and PR summaries.

### `codex-general-subagent-task-orchestration`

Use when the user explicitly asks for Codex subagents or broad parallel work. It defines safe delegation, worker boundaries, read-only investigation modes, disjoint implementation slices, and main-agent integration.

### `codex-general-repo-diagnostic-backlog-review`

Use for diagnostic-only repo audits. It creates numbered, evidence-backed backlog tickets that future Codex sessions can pick up and fix.

### `codex-general-explain-changes`

Use when the user asks what Codex changed and why. It explains current working-tree, staged, session, or artifact changes from local evidence, with concise code excerpts and next verification steps.

## Lifecycle Fit

These skills are designed to compose without making Codex dependent on a single workflow:

1. Clarify requirements with `codex-general-requirements-acceptance-clarifier`.
2. Plan the implementation boundary with `codex-general-implementation-strategy`.
3. Make careful improvements with `codex-general-mature-repo-refinement` or normal implementation.
4. Review code with `codex-general-code-review-and-quality`.
5. Strengthen tests with `codex-general-test-quality-and-coverage`.
6. Improve runtime diagnosis with `codex-general-runtime-observability-diagnostics` when logs, traces, agents, jobs, APIs, or CLIs are involved.
7. Use `codex-general-storage-diagnostics` when a repo needs a read-only size, file-count, path-length, or bloat-candidate audit.
8. Use `codex-general-window-placement` when visible macOS app/browser windows need repeatable placement across the laptop and external monitors.
9. Use `codex-general-api-cost-aware-agent-testing` before live model/API testing.
10. Use `codex-general-openai-cost-monitor` when a live workflow needs OpenAI spend or usage polling.
11. Verify the final state with `codex-general-repo-change-verification`.
12. Use `codex-general-supply-docs-release-guard` whenever docs, dependencies, CI, release, or PR surfaces are touched.
13. Use `codex-general-subagent-task-orchestration` only for explicitly delegated or broad parallel work.
14. Use `codex-general-repo-diagnostic-backlog-review` when issues should be recorded for later rather than fixed immediately.
15. Use `codex-general-explain-changes` when the user wants a grounded walkthrough of what changed, why it matters, and what should be verified next.

## Installation

Copy the desired skill folders into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R skills/* ~/.codex/skills/
```

Each skill folder contains a `SKILL.md` file and optional `agents/openai.yaml` metadata. After copying, restart Codex or start a new session so the skills are discovered.

## Design Notes

- Skills are intentionally general and repo-agnostic.
- Each skill has explicit trigger and non-trigger language in frontmatter.
- Detailed workflow guidance lives in `SKILL.md`, not in the README.
- Repo-specific skills should live in their own repositories or local skill folders, not in this general collection.
