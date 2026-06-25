#!/usr/bin/env python3
"""Read-only repository storage diagnostics."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_EXCLUDES = {".git"}
DEPENDENCY_DIRS = {"node_modules", ".venv", "venv", "vendor", ".pnpm-store", ".yarn"}
BUILD_DIRS = {"dist", "build", "target", ".next", "out", "coverage", "site", "public"}
CACHE_DIRS = {
    ".cache",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".turbo",
    ".parcel-cache",
    ".gradle",
}
ARTIFACT_DIRS = {"artifacts", "artifact", "outputs", "output", "reports", "report", "screenshots", "traces"}
LOG_NAMES = {"logs", "log"}
MEDIA_EXTS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".mp4",
    ".mov",
    ".mp3",
    ".wav",
    ".pdf",
    ".zip",
    ".gz",
    ".tar",
    ".tgz",
    ".parquet",
    ".sqlite",
    ".db",
    ".pkl",
    ".pt",
    ".onnx",
}
LOG_EXTS = {".log", ".trace"}
SOURCE_EXTS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".swift",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".rb",
    ".php",
    ".cs",
}


@dataclass
class Node:
    path: str
    size: int = 0
    files: int = 0
    dirs: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only repository storage diagnostics.")
    parser.add_argument("path", nargs="?", default=".", help="Repository or directory to scan.")
    parser.add_argument("--top", type=int, default=15, help="Number of top paths to report.")
    parser.add_argument("--max-depth", type=int, default=3, help="Directory depth to aggregate for top folders.")
    parser.add_argument("--exclude", action="append", default=[], help="Additional directory/file names to exclude.")
    parser.add_argument("--include-git", action="store_true", help="Include .git in the scan.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    return parser.parse_args()


def human_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(value)} B"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def rel_path(path: Path, root: Path) -> str:
    if path == root:
        return "."
    return path.relative_to(root).as_posix()


def should_exclude(path: Path, excludes: set[str]) -> bool:
    return path.name in excludes


def classify(path: str, is_dir: bool) -> str | None:
    parts = set(Path(path).parts)
    name = Path(path).name
    suffix = Path(path).suffix.lower()
    if is_dir:
        if name in DEPENDENCY_DIRS or parts & DEPENDENCY_DIRS:
            return "dependency"
        if name in BUILD_DIRS or parts & BUILD_DIRS:
            return "build"
        if name in CACHE_DIRS or parts & CACHE_DIRS:
            return "cache"
        if name in ARTIFACT_DIRS or parts & ARTIFACT_DIRS:
            return "artifact"
        if name in LOG_NAMES or parts & LOG_NAMES:
            return "logs"
    if suffix in MEDIA_EXTS:
        return "media/data"
    if suffix in LOG_EXTS:
        return "logs"
    return None


def ancestor_keys(path: Path, root: Path, max_depth: int) -> list[str]:
    rel = path.relative_to(root)
    parts = rel.parts
    keys = ["."]
    for depth in range(1, min(len(parts), max_depth) + 1):
        keys.append(Path(*parts[:depth]).as_posix())
    return keys


def scan(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    root = root.resolve()
    excludes = set(args.exclude)
    if not args.include_git:
        excludes |= DEFAULT_EXCLUDES

    dirs: dict[str, Node] = defaultdict(lambda: Node(path=""))
    source_counts: Counter[str] = Counter()
    path_lengths: list[dict[str, Any]] = []
    files: list[Node] = []
    ext_sizes: Counter[str] = Counter()
    ext_counts: Counter[str] = Counter()
    candidates: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    total_files = 0
    total_dirs = 0

    dirs["."] = Node(path=".")
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    path = Path(entry.path)
                    if should_exclude(path, excludes):
                        continue
                    try:
                        is_dir = entry.is_dir(follow_symlinks=False)
                        is_file = entry.is_file(follow_symlinks=False)
                    except OSError as exc:
                        errors.append(f"{rel_path(path, root)}: {exc}")
                        continue
                    if is_dir:
                        total_dirs += 1
                        rel = rel_path(path, root)
                        path_lengths.append({"path": rel, "kind": "directory", "length": len(rel), "depth": len(Path(rel).parts)})
                        dirs[rel].path = rel
                        for key in ancestor_keys(path, root, args.max_depth):
                            dirs[key].dirs += 1
                        category = classify(rel, True)
                        if category:
                            candidates.setdefault(
                                rel,
                                {"path": rel, "category": category, "kind": "directory", "size": 0, "files": 0, "dirs": 0},
                            )
                        stack.append(path)
                    elif is_file or entry.is_symlink():
                        try:
                            size = entry.stat(follow_symlinks=False).st_size
                        except OSError as exc:
                            errors.append(f"{rel_path(path, root)}: {exc}")
                            continue
                        total_files += 1
                        rel = rel_path(path, root)
                        path_lengths.append({"path": rel, "kind": "file", "length": len(rel), "depth": len(Path(rel).parts), "size": size})
                        files.append(Node(path=rel, size=size, files=1))
                        suffix = path.suffix.lower() or "[no extension]"
                        ext_sizes[suffix] += size
                        ext_counts[suffix] += 1
                        for key in ancestor_keys(path, root, args.max_depth):
                            dirs[key].path = key
                            dirs[key].size += size
                            dirs[key].files += 1
                            if suffix in SOURCE_EXTS:
                                source_counts[key] += 1
                        category = classify(rel, False)
                        if category:
                            candidates.setdefault(
                                rel,
                                {"path": rel, "category": category, "kind": "file", "size": size, "files": 1, "dirs": 0},
                            )
        except OSError as exc:
            errors.append(f"{rel_path(current, root)}: {exc}")

    for path, candidate in list(candidates.items()):
        if candidate["kind"] == "directory" and path in dirs:
            candidate["size"] = dirs[path].size
            candidate["files"] = dirs[path].files
            candidate["dirs"] = dirs[path].dirs

    total_size = dirs["."].size
    top_dirs = sorted((node for key, node in dirs.items() if key != "."), key=lambda n: n.size, reverse=True)[: args.top]
    top_file_count_dirs = sorted((node for key, node in dirs.items() if key != "."), key=lambda n: n.files, reverse=True)[: args.top]
    top_files = sorted(files, key=lambda n: n.size, reverse=True)[: args.top]
    longest_paths = sorted(path_lengths, key=lambda item: (item["length"], item["depth"]), reverse=True)[: args.top]
    top_exts = [
        {"extension": ext, "size": size, "files": ext_counts[ext]}
        for ext, size in ext_sizes.most_common(args.top)
    ]
    top_candidates = sorted(candidates.values(), key=lambda item: item["size"], reverse=True)[: args.top]
    source_heavy = [
        {
            "path": path,
            "source_files": count,
            "total_files": dirs[path].files,
            "size": dirs[path].size,
            "category": "source-heavy",
        }
        for path, count in source_counts.most_common(args.top)
        if path != "." and count >= 25
    ]
    return {
        "root": str(root),
        "total_size": total_size,
        "total_files": total_files,
        "total_dirs": total_dirs,
        "top_dirs": [node.__dict__ for node in top_dirs],
        "top_file_count_dirs": [node.__dict__ for node in top_file_count_dirs],
        "top_files": [node.__dict__ for node in top_files],
        "longest_paths": longest_paths,
        "top_extensions": top_exts,
        "candidates": top_candidates,
        "source_heavy": source_heavy,
        "excluded_names": sorted(excludes),
        "errors": errors,
    }


def pct(size: int, total: int) -> str:
    if total <= 0:
        return "0.0%"
    return f"{(size / total) * 100:.1f}%"


def print_table(title: str, rows: list[dict[str, Any]], total: int, kind: str) -> None:
    print(title)
    for row in rows:
        size = row["size"]
        detail = f"{human_size(size):>10} {pct(size, total):>6}  {row['path']}"
        if kind == "dir":
            detail += f"  ({row['files']} files, {row['dirs']} dirs)"
        print(detail)
    if not rows:
        print("  none")


def print_text(result: dict[str, Any]) -> None:
    total = result["total_size"]
    print("Storage Diagnostics")
    print(f"root={result['root']}")
    print(f"total={human_size(total)} files={result['total_files']} dirs={result['total_dirs']}")
    print_table("largest directories:", result["top_dirs"], total, "dir")
    print_table("file-count hotspots:", result["top_file_count_dirs"], total, "dir")
    print_table("largest files:", result["top_files"], total, "file")
    print("longest paths:")
    for row in result["longest_paths"]:
        size = f" {human_size(row['size'])}" if "size" in row else ""
        print(f"{row['length']:>5} chars depth={row['depth']:<2} {row['kind']:<9}{size:>10}  {row['path']}")
    if not result["longest_paths"]:
        print("  none")
    print("largest extensions:")
    for row in result["top_extensions"]:
        print(f"{human_size(row['size']):>10} {pct(row['size'], total):>6}  {row['extension']}  ({row['files']} files)")
    if not result["top_extensions"]:
        print("  none")
    print("candidate review areas:")
    for row in result["candidates"]:
        print(
            f"{human_size(row['size']):>10} {pct(row['size'], total):>6}  "
            f"{row['category']:<10} {row['kind']:<9} {row['path']}"
        )
    if not result["candidates"]:
        print("  none")
    print("source-maintenance leads:")
    for row in result["source_heavy"]:
        print(
            f"{human_size(row['size']):>10} {pct(row['size'], total):>6}  "
            f"{row['source_files']} source files / {row['total_files']} total  {row['path']}"
        )
    if not result["source_heavy"]:
        print("  none")
    if result["errors"]:
        print("scan warnings:")
        for warning in result["errors"][:10]:
            print(f"  {warning}")


def main() -> int:
    args = parse_args()
    root = Path(args.path)
    if not root.exists():
        print(f"path does not exist: {root}", file=sys.stderr)
        return 2
    result = scan(root, args)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_text(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
