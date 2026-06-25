---
name: codex-general-storage-diagnostics
description: Diagnose repository storage footprint, file counts, folder counts, large directories, large files, generated artifacts, dependency caches, build outputs, logs, reports, and other possible storage bloat without changing files. Use when Codex is asked to inspect repo size, count files or folders, find storage hotspots, identify cleanup candidates, understand why a checkout is large, compare source versus generated/cache areas, or produce a read-only bloat/storage audit. Do not use to delete, trim, archive, rewrite history, or remove files unless the user separately asks for an implementation step after the diagnostic report.
---

# Storage Diagnostics

## Overview

Use this skill for read-only repository storage diagnostics. The goal is to map the footprint, identify likely bloat areas, and separate evidence from cleanup decisions.

This skill must not delete, move, rewrite, archive, or ignore files. Treat every cleanup candidate as a review item until repo-specific ownership, generated-file rules, and validation gates are checked.

## Workflow

1. Confirm the target path. Default to the current repo root when the user says "this repo."
2. Read local guidance first when available: `AGENTS.md`, README, cleanup docs, generated-file notes, `.gitignore`, package manifests, and existing backlog files.
3. Run a read-only size/count audit:
   - total bytes
   - file count
   - directory count
   - top directories by size
   - top directories by file count
   - top files by size
   - longest file and folder paths
   - extension/type footprint
   - likely generated, dependency, cache, build, log, report, or artifact areas
4. Interpret results conservatively:
   - distinguish source code from dependencies, build outputs, caches, generated assets, local reports, and user-facing artifacts
   - call out evidence and uncertainty
   - do not claim a path is safe to delete from size alone
5. If the user asks for follow-up cleanup, switch to an implementation plan with explicit candidates, risk, validation, and rollback.

## Script

Use `scripts/storage_diagnostics.py` for deterministic scans:

```bash
python3 scripts/storage_diagnostics.py .
python3 scripts/storage_diagnostics.py /path/to/repo --top 25 --max-depth 4
python3 scripts/storage_diagnostics.py . --json
python3 scripts/storage_diagnostics.py . --exclude node_modules --exclude .venv
```

The script is read-only. It does not follow directory symlinks. It excludes `.git` by default because Git object storage is a different diagnostic surface; ask before inspecting `.git` size or history bloat.

## Report Shape

Prefer a compact report:

```markdown
## Storage Diagnostics

- Total: <human size>, <files> files, <dirs> folders
- Largest folders: <top 5 with size and share>
- File-count hotspots: <top 5 with files and folders>
- Largest files: <top 5 with size>
- Longest paths: <top 5 paths by character length/depth>
- Likely bloat candidates: <paths with category and why>
- Unneeded-code leads: <large or high-file-count source areas that need reference/test proof>
- Keep/verify before cleanup: <source-of-truth, generated, fixture, artifact, or deliverable uncertainty>
- Suggested next step: <read-only follow-up or explicit cleanup plan>
```

Separate evidence types in the report:

- storage pressure: large byte footprint
- navigation/indexing pressure: many files or folders
- generated/artifact pressure: outputs that may be reproducible
- source-maintenance pressure: large or sprawling source/test/docs areas that may contain dead code but require reference analysis
- path-complexity pressure: deeply nested or long paths that make navigation, tooling, packaging, or cross-platform compatibility harder

## Candidate Categories

Use these labels as diagnostic hints, not deletion approval:

- dependency: package/vendor directories such as `node_modules`, `.venv`, `vendor`, or package caches
- build: `dist`, `build`, `target`, `.next`, `out`, coverage bundles, or compiled outputs
- cache: `.cache`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.turbo`, or tool caches
- artifact: `artifacts`, `output`, `outputs`, `reports`, screenshots, traces, generated PDFs, archives, or large run products
- media/data: large images, videos, audio, datasets, model files, or binary assets
- logs: `.log`, log directories, runtime traces, or local debug dumps
- source-heavy: many small source/test/docs files; usually a structure issue, not a deletion target

## Safety Rules

- Do not delete or mutate files during this skill.
- Do not recommend deleting dependencies or generated outputs until the repo's install/build/rebuild path is known.
- Do not recommend removing reports, artifacts, datasets, or media without checking whether they are deliverables, fixtures, or source-of-truth assets.
- Do not call code unneeded from size or file count alone. Treat dead-code cleanup as a separate proof step using imports, references, tests, entry points, and runtime behavior.
- Do not inspect secrets by opening large env/config/data files just because they are large; report path, size, and risk instead.
- For Git history bloat, inspect `.git` only when the user asks for history diagnostics or repository clone-size analysis.
