#!/usr/bin/env python3
"""Locate and optionally download screenshot-related GitHub Actions artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


class ArtifactError(Exception):
    pass


def run_cmd(args: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ArtifactError(result.stderr.strip() or "Command failed.")
    return result.stdout


def gh_json(args: list[str], cwd: Path | None = None) -> Any:
    output = run_cmd(["gh", *args], cwd=cwd)
    return json.loads(output)


def current_branch(cwd: Path) -> str:
    output = run_cmd(["git", "branch", "--show-current"], cwd=cwd)
    branch = output.strip()
    if not branch:
        raise ArtifactError("Unable to determine current git branch.")
    return branch


def repo_name(cwd: Path) -> str:
    payload = gh_json(["repo", "view", "--json", "nameWithOwner"], cwd=cwd)
    name = payload.get("nameWithOwner")
    if not isinstance(name, str) or not name:
        raise ArtifactError("Unable to resolve GitHub repository name.")
    return name


def branch_for_pr(cwd: Path, pr: str) -> str:
    payload = gh_json(["pr", "view", pr, "--json", "headRefName"], cwd=cwd)
    head = payload.get("headRefName")
    if not isinstance(head, str) or not head:
        raise ArtifactError(f"Unable to resolve branch for PR {pr}.")
    return head


def run_list(cwd: Path, workflow: str, branch: str, limit: int) -> list[dict[str, Any]]:
    payload = gh_json(
        [
            "run",
            "list",
            "--workflow",
            workflow,
            "--branch",
            branch,
            "--limit",
            str(limit),
            "--json",
            "databaseId,workflowName,displayTitle,headBranch,status,conclusion,url,createdAt",
        ],
        cwd=cwd,
    )
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def run_artifacts(cwd: Path, repo: str, run_id: int) -> list[dict[str, Any]]:
    payload = gh_json(
        ["api", f"repos/{repo}/actions/runs/{run_id}/artifacts?per_page=100"],
        cwd=cwd,
    )
    artifacts = payload.get("artifacts") if isinstance(payload, dict) else None
    if not isinstance(artifacts, list):
        return []
    return [item for item in artifacts if isinstance(item, dict)]


def pick_run(
    cwd: Path,
    repo: str,
    workflow: str,
    branch: str,
    artifact_name: str,
    limit: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    runs = run_list(cwd, workflow, branch, limit)
    for run in runs:
        run_id = run.get("databaseId")
        if not isinstance(run_id, int):
            continue
        artifacts = run_artifacts(cwd, repo, run_id)
        for artifact in artifacts:
            if artifact.get("name") == artifact_name:
                return run, artifact
    raise ArtifactError(
        f"No run on branch '{branch}' produced artifact '{artifact_name}' for workflow '{workflow}'."
    )


def download_run_artifact(cwd: Path, run_id: int, artifact_name: str, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    run_cmd(
        ["gh", "run", "download", str(run_id), "--name", artifact_name, "--dir", str(dest)],
        cwd=cwd,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Locate and optionally download screenshot-related GitHub Actions artifacts."
    )
    parser.add_argument("--workflow", default="screenshot-test.yml", help="Workflow file or name")
    parser.add_argument(
        "--artifact-name",
        default="screenshot-diff",
        help="Artifact name to search for",
    )
    parser.add_argument("--branch", help="Branch to inspect")
    parser.add_argument("--pr", help="PR number to inspect")
    parser.add_argument("--run-id", type=int, help="Specific run ID to use")
    parser.add_argument("--download", action="store_true", help="Download the artifact")
    parser.add_argument(
        "--dir",
        default=".tmp/screenshot-artifact",
        help="Destination directory for --download",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="How many runs to inspect when searching",
    )
    parser.add_argument(
        "--cwd",
        default=".",
        help="Repository working directory (defaults to current directory)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cwd = Path(args.cwd).expanduser().resolve()

    try:
        repo = repo_name(cwd)
        branch = args.branch or (branch_for_pr(cwd, args.pr) if args.pr else current_branch(cwd))

        if args.run_id is not None:
            run = {"databaseId": args.run_id, "headBranch": branch}
            artifact = None
            for candidate in run_artifacts(cwd, repo, args.run_id):
                if candidate.get("name") == args.artifact_name:
                    artifact = candidate
                    break
            if artifact is None:
                raise ArtifactError(
                    f"Run {args.run_id} does not contain artifact '{args.artifact_name}'."
                )
        else:
            run, artifact = pick_run(
                cwd,
                repo,
                args.workflow,
                branch,
                args.artifact_name,
                args.limit,
            )

        run_id = run.get("databaseId")
        if not isinstance(run_id, int):
            raise ArtifactError("Resolved run is missing a numeric databaseId.")

        download_path = None
        if args.download:
            dest = Path(args.dir).expanduser().resolve()
            download_run_artifact(cwd, run_id, args.artifact_name, dest)
            download_path = str(dest)

        payload = {
            "repo": repo,
            "branch": branch,
            "workflow": args.workflow,
            "artifactName": args.artifact_name,
            "run": run,
            "artifact": artifact,
            "downloadPath": download_path,
        }

        if args.format == "json":
            print(json.dumps(payload, indent=2))
            return 0

        print(f"Repo: {repo}")
        print(f"Branch: {branch}")
        print(f"Run ID: {run_id}")
        print(f"Artifact: {artifact.get('name')}")
        if run.get("url"):
            print(f"Run URL: {run['url']}")
        if download_path:
            print(f"Downloaded to: {download_path}")
        return 0
    except ArtifactError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
