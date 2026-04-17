#!/usr/bin/env python3
"""Audit which landing files a specific author contributed to on a branch."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


class AuditError(Exception):
    pass


def run_git(repo: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AuditError(result.stderr.strip() or "Git command failed.")
    return result.stdout


def list_author_identities(repo: Path, upstream: str, branch: str) -> list[str]:
    output = run_git(
        repo,
        ["log", "--format=%an <%ae>", f"{upstream}..{branch}"],
    )
    identities = sorted({line.strip() for line in output.splitlines() if line.strip()})
    return identities


def resolve_author_identity(
    requested: str,
    identities: list[str],
    author_match: str,
) -> str:
    if author_match == "exact":
        for identity in identities:
            if identity == requested:
                return identity
        raise AuditError(f"Author '{requested}' not found in the selected range.")

    requested_lower = requested.lower()
    matches = [identity for identity in identities if requested_lower in identity.lower()]
    if not matches:
        raise AuditError(f"Author '{requested}' not found in the selected range.")
    if len(matches) > 1:
        joined = "; ".join(matches)
        raise AuditError(
            f"Author '{requested}' matched multiple identities: {joined}. "
            "Use a more specific name or pass --author-match exact."
        )
    return matches[0]


def list_commits_for_author(
    repo: Path,
    exact_author: str,
    upstream: str,
    branch: str,
) -> list[str]:
    pattern = f"^{re.escape(exact_author)}$"
    output = run_git(
        repo,
        ["log", f"--author={pattern}", "--format=%H", f"{upstream}..{branch}"],
    )
    return [line.strip() for line in output.splitlines() if line.strip()]


def files_touched_by_commits(repo: Path, commits: list[str]) -> set[str]:
    files: set[str] = set()
    for commit in commits:
        output = run_git(
            repo,
            ["diff-tree", "--no-commit-id", "--name-only", "-r", commit],
        )
        files.update(line.strip() for line in output.splitlines() if line.strip())
    return files


def build_rename_map(repo: Path, upstream: str, branch: str) -> dict[str, set[str]]:
    output = run_git(repo, ["log", "--format=%H", f"{upstream}..{branch}"])
    commits = [line.strip() for line in output.splitlines() if line.strip()]
    rename_map: dict[str, set[str]] = {}

    for commit in commits:
        diff_output = run_git(
            repo,
            ["diff-tree", "--no-commit-id", "-r", "-M", "--name-status", commit],
        )
        for line in diff_output.splitlines():
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            status = parts[0]
            if not status.startswith("R"):
                continue
            old_path = parts[1].strip()
            new_path = parts[2].strip()
            if not old_path or not new_path:
                continue
            rename_map.setdefault(new_path, set()).add(old_path)

    return rename_map


def landing_files(repo: Path, upstream: str, branch: str) -> list[str]:
    output = run_git(repo, ["diff", "--name-only", f"{upstream}..{branch}"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def classify_file(
    current_path: str,
    direct_files: set[str],
    rename_map: dict[str, set[str]],
) -> tuple[str, set[str]] | None:
    if current_path in direct_files:
        return ("DIRECT", set())

    seen: set[str] = set()
    pending = [current_path]

    while pending:
        path = pending.pop()
        if path in seen:
            continue
        seen.add(path)
        for previous in rename_map.get(path, set()):
            if previous in direct_files:
                ancestors = seen | {previous}
                ancestors.discard(current_path)
                return ("VIA_RENAME", ancestors)
            pending.append(previous)

    return None


def diff_stats(repo: Path, upstream: str, branch: str, path: str) -> str:
    output = run_git(repo, ["diff", "--numstat", f"{upstream}..{branch}", "--", path])
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        added, removed, file_path = parts[:3]
        if file_path != path:
            continue
        if added == "-" or removed == "-":
            return "binary"
        return f"+{added}/-{removed}"
    return ""


def markdown_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Status | File | +/- | Source Paths |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        source_paths = ", ".join(sorted(row["sourcePaths"])) if row["sourcePaths"] else "-"
        lines.append(
            f"| {row['status']} | {row['file']} | {row['stats'] or '-'} | {source_paths} |"
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit which landing files a specific author contributed to on a branch."
    )
    parser.add_argument("--author", required=True, help="Author name or identity string")
    parser.add_argument("--upstream", default="main", help="Upstream branch or ref")
    parser.add_argument("--branch", default="HEAD", help="Branch or ref to inspect")
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository root to inspect (defaults to current directory)",
    )
    parser.add_argument(
        "--author-match",
        choices=("contains", "exact"),
        default="contains",
        help="How to resolve the provided author against git identities in range",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).expanduser().resolve()

    try:
        identities = list_author_identities(repo, args.upstream, args.branch)
        exact_author = resolve_author_identity(args.author, identities, args.author_match)
        commits = list_commits_for_author(repo, exact_author, args.upstream, args.branch)
        direct_files = files_touched_by_commits(repo, commits)
        rename_map = build_rename_map(repo, args.upstream, args.branch)
        files = landing_files(repo, args.upstream, args.branch)

        rows: list[dict[str, Any]] = []
        for path in files:
            classification = classify_file(path, direct_files, rename_map)
            if classification is None:
                continue
            status, source_paths = classification
            rows.append(
                {
                    "status": status,
                    "file": path,
                    "stats": diff_stats(repo, args.upstream, args.branch, path),
                    "sourcePaths": sorted(source_paths),
                }
            )

        rows.sort(key=lambda row: row["file"])

        if args.format == "json":
            payload = {
                "author": exact_author,
                "upstream": args.upstream,
                "branch": args.branch,
                "count": len(rows),
                "files": rows,
            }
            print(json.dumps(payload, indent=2))
            return 0

        print(f"Author: {exact_author}")
        print(f"Range: {args.upstream}..{args.branch}")
        print(f"Files: {len(rows)}")
        print("")
        print(markdown_table(rows))
        return 0
    except AuditError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
