# General Codex Skills Lifecycle

This lifecycle describes how the general skills in this repository fit together. The skills are intentionally modular: use the smallest skill or combination of skills that matches the task instead of forcing every project through the full sequence.

## Core Flow

1. **Clarify the work**
   - Skill: `codex-requirements-acceptance-clarifier`
   - Use when the request is broad, risky, or hard to verify.
   - Output: objective, non-goals, acceptance criteria, assumptions, and practical verification standards.

2. **Plan the implementation boundary**
   - Skill: `codex-implementation-strategy`
   - Use before non-trivial changes to APIs, runtime behavior, schemas, config, tests, docs, agent/tool contracts, or multi-file behavior.
   - Output: compatibility boundary, implementation approach, risk slices, stop conditions, and verification plan.

3. **Refine mature code carefully**
   - Skill: `codex-mature-repo-refinement`
   - Use when a working repo should become slightly cleaner, more efficient, better organized, or easier to maintain without behavior changes.
   - Output: small behavior-preserving improvements with explicit preservation checks.

4. **Review code quality**
   - Skill: `codex-code-review-and-quality`
   - Use after implementation, during review, or before handoff.
   - Output: evidence-backed findings or scoped fixes for correctness, maintainability, simplicity, performance, security basics, and AI-generated failure modes.

5. **Improve tests**
   - Skill: `codex-test-quality-and-coverage`
   - Use when adding tests, fixing bugs, improving coverage, reviewing test diffs, or dealing with weak/flaky tests.
   - Output: behavior-focused tests that would fail for the bug or regression they claim to guard.

6. **Make runtime behavior diagnosable**
   - Skill: `codex-runtime-observability-diagnostics`
   - Use for logs, tracebacks, traces, metrics, health checks, receipts, agents, jobs, CLIs, APIs, and other runtime workflows.
   - Output: diagnostic evidence that answers what happened, where, for which run/input, why it failed or skipped, and what to inspect next.

7. **Test API-backed agents without overspending**
   - Skill: `codex-api-cost-aware-agent-testing`
   - Use for OpenAI/API-backed agents, tool-calling workflows, evals, or live SDK behavior where live calls can cost money.
   - Output: staged offline-first diagnostics, explicit budget gates, one-agent-at-a-time live tests, and usage/cost notes when available.

8. **Verify the final repo state**
   - Skill: `codex-repo-change-verification`
   - Use after code, tests, build config, package scripts, CLI/UI/runtime workflows, schemas, or docs-linked behavior changes.
   - Output: exact checks run, what they prove, what failed and was fixed, and what remains unverified.

9. **Guard high-blast-radius surfaces**
   - Skill: `codex-supply-docs-release-guard`
   - Use for dependencies, lockfiles, package scripts, CI, GitHub Actions, Dockerfiles, docs claims, config/env docs, changelogs, releases, and PR summaries.
   - Output: safer dependency/tooling/docs/release changes with evidence and explicit stop points.

10. **Use subagents only when useful and authorized**
    - Skill: `codex-subagent-task-orchestration`
    - Use when the user explicitly asks for subagents, parallel investigation, broad multi-issue work, or disjoint worker fixes.
    - Output: clear worker ownership, bounded delegation, main-agent synthesis, integrated validation, and final handoff.

11. **Record future work instead of fixing immediately**
    - Skill: `codex-repo-diagnostic-backlog-review`
    - Use for diagnostic-only repo audits that should create actionable backlog tickets for later sessions.
    - Output: numbered tickets with evidence, severity, suggested fix, and validation path.

12. **Explain current work clearly**
    - Skill: `codex-explain-changes`
    - Use when the user wants to understand what changed, why it matters, and what should be verified next.
    - Output: a grounded walkthrough from local git evidence, session context, or generated artifacts, with short excerpts when useful.

## Avoiding Overuse

These skills should improve judgment, not create ceremony. Skip a skill when the task is tiny, the answer is obvious from nearby code, or the user asked only for a direct answer. Combine skills when the task crosses boundaries, such as a runtime agent change that needs requirements, implementation planning, cost-aware live testing, observability, and final verification.

## Coverage Gaps To Watch

Even with this lifecycle, Codex should still check for gaps between skills:

- Product decisions that cannot be inferred from code.
- Live systems, credentials, billing, publishing, or destructive operations that need explicit approval.
- Missing tests or logs that make behavior hard to prove.
- Broad cleanup pressure that should become backlog tickets instead of uncontrolled edits.
- Repo-specific conventions that should override these general instructions.

When in doubt, reduce scope, collect stronger evidence, and state what remains unverified.
