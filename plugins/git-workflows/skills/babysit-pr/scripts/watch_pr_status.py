#!/usr/bin/env python3
"""Snapshot or watch GitHub pull-request state with delta tracking."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


class WatchError(Exception):
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
        raise WatchError(result.stderr.strip() or "Command failed.")
    return result.stdout


def gh_json(args: list[str], cwd: Path | None = None) -> Any:
    output = run_cmd(["gh", *args], cwd=cwd)
    return json.loads(output)


def git_root(cwd: Path) -> Path:
    output = run_cmd(["git", "rev-parse", "--show-toplevel"], cwd=cwd)
    return Path(output.strip())


def current_repo_name(cwd: Path) -> str:
    payload = gh_json(["repo", "view", "--json", "nameWithOwner"], cwd=cwd)
    name = payload.get("nameWithOwner")
    if not isinstance(name, str) or not name:
        raise WatchError("Unable to resolve GitHub repository name.")
    return name


def normalize_pr_selector(selector: str) -> str | int | None:
    if selector == "auto":
        return None
    if selector.isdigit():
        return int(selector)
    parsed = urlparse(selector)
    if parsed.scheme and parsed.netloc and parsed.path:
        return selector
    return selector


def pr_view(cwd: Path, selector: str) -> dict[str, Any]:
    fields = [
        "number",
        "url",
        "title",
        "state",
        "isDraft",
        "mergeStateStatus",
        "reviewDecision",
        "headRefName",
        "headRefOid",
        "author",
        "statusCheckRollup",
    ]
    base_args = ["pr", "view"]
    normalized = normalize_pr_selector(selector)
    if normalized is not None:
        base_args.append(str(normalized))
    base_args.extend(["--json", ",".join(fields)])
    payload = gh_json(base_args, cwd=cwd)
    if not isinstance(payload, dict):
        raise WatchError("Unexpected PR view response.")
    return payload


def issue_comments(cwd: Path, repo: str, pr_number: int) -> list[dict[str, Any]]:
    payload = gh_json(
        ["api", f"repos/{repo}/issues/{pr_number}/comments?per_page=100"],
        cwd=cwd,
    )
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def review_comments(cwd: Path, repo: str, pr_number: int) -> list[dict[str, Any]]:
    payload = gh_json(
        ["api", f"repos/{repo}/pulls/{pr_number}/comments?per_page=100"],
        cwd=cwd,
    )
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def reviews(cwd: Path, repo: str, pr_number: int) -> list[dict[str, Any]]:
    payload = gh_json(
        ["api", f"repos/{repo}/pulls/{pr_number}/reviews?per_page=100"],
        cwd=cwd,
    )
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def comment_summary(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in items:
        item_id = item.get("id")
        if item_id is None:
            continue
        user = item.get("user") or {}
        body = (item.get("body") or "").strip()
        rows.append(
            {
                "id": item_id,
                "author": user.get("login"),
                "createdAt": item.get("created_at"),
                "updatedAt": item.get("updated_at"),
                "bodyPreview": body[:160],
            }
        )
    return rows


def review_summary(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in items:
        item_id = item.get("id")
        if item_id is None:
            continue
        user = item.get("user") or {}
        body = (item.get("body") or "").strip()
        rows.append(
            {
                "id": item_id,
                "author": user.get("login"),
                "state": item.get("state"),
                "submittedAt": item.get("submitted_at"),
                "bodyPreview": body[:160],
            }
        )
    return rows


def check_summary(status_rollup: Any) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for item in status_rollup or []:
        if not isinstance(item, dict):
            continue
        name = item.get("name") or item.get("context") or item.get("workflowName") or "unknown"
        status = item.get("status") or item.get("state") or "UNKNOWN"
        conclusion = item.get("conclusion")
        url = item.get("detailsUrl") or item.get("targetUrl") or item.get("url")
        rows.append(
            {
                "name": name,
                "status": status,
                "conclusion": conclusion,
                "url": url,
            }
        )

    passed = 0
    failed = 0
    pending = 0

    for row in rows:
        status = str(row.get("status") or "").upper()
        conclusion = str(row.get("conclusion") or "").upper()
        if conclusion in {"SUCCESS", "NEUTRAL", "SKIPPED"}:
            passed += 1
        elif conclusion in {"FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE"}:
            failed += 1
        elif status in {"QUEUED", "IN_PROGRESS", "PENDING", "REQUESTED", "WAITING"} or not conclusion:
            pending += 1
        else:
            pending += 1

    return {
        "total": len(rows),
        "passed": passed,
        "failed": failed,
        "pending": pending,
        "checks": rows,
    }


def default_state_file(repo_root: Path, pr_number: int) -> Path:
    return repo_root / ".git" / ".otto-pr-watch" / f"pr-{pr_number}.json"


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def save_state(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def summarize_delta(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    prev_issue = set(previous.get("issueCommentIds", []))
    prev_review_comment = set(previous.get("reviewCommentIds", []))
    prev_reviews = set(previous.get("reviewIds", []))

    current_issue = {row["id"] for row in current["issueComments"]}
    current_review_comment = {row["id"] for row in current["reviewComments"]}
    current_reviews = {row["id"] for row in current["reviews"]}

    return {
        "newIssueComments": [row for row in current["issueComments"] if row["id"] not in prev_issue],
        "newReviewComments": [
            row for row in current["reviewComments"] if row["id"] not in prev_review_comment
        ],
        "newReviews": [row for row in current["reviews"] if row["id"] not in prev_reviews],
        "headChanged": previous.get("headRefOid") != current["pr"]["headRefOid"],
        "mergeStateChanged": previous.get("mergeStateStatus") != current["pr"]["mergeStateStatus"],
        "reviewDecisionChanged": previous.get("reviewDecision") != current["pr"]["reviewDecision"],
        "stateChanged": previous.get("state") != current["pr"]["state"],
        "checkSummaryChanged": previous.get("checks") != current["checks"],
    }


def compute_actions(snapshot: dict[str, Any], delta: dict[str, Any]) -> list[str]:
    pr = snapshot["pr"]
    checks = snapshot["checks"]
    actions: list[str] = []

    if pr.get("state") != "OPEN":
        actions.append("stop_pr_closed")
        return actions

    if delta["newIssueComments"] or delta["newReviewComments"] or delta["newReviews"]:
        actions.append("review_new_feedback")

    if checks["failed"] > 0:
        actions.append("diagnose_failed_checks")
    elif checks["pending"] > 0:
        actions.append("wait_for_pending_checks")

    review_decision = pr.get("reviewDecision")
    merge_state = pr.get("mergeStateStatus")
    if checks["failed"] == 0 and checks["pending"] == 0 and review_decision not in {"CHANGES_REQUESTED"}:
        if merge_state not in {"DIRTY", "UNKNOWN", "BEHIND"}:
            actions.append("ready_for_handoff")

    actions.append("continue_watch")
    return actions


def build_snapshot(cwd: Path, selector: str) -> tuple[dict[str, Any], Path]:
    repo_root = git_root(cwd)
    repo = current_repo_name(repo_root)
    pr = pr_view(repo_root, selector)
    pr_number = pr.get("number")
    if not isinstance(pr_number, int):
        raise WatchError("Unable to resolve PR number.")

    issue = comment_summary(issue_comments(repo_root, repo, pr_number))
    review_comment = comment_summary(review_comments(repo_root, repo, pr_number))
    review_items = review_summary(reviews(repo_root, repo, pr_number))
    checks = check_summary(pr.get("statusCheckRollup"))

    snapshot = {
        "pr": {
            "number": pr_number,
            "url": pr.get("url"),
            "title": pr.get("title"),
            "state": pr.get("state"),
            "isDraft": pr.get("isDraft"),
            "mergeStateStatus": pr.get("mergeStateStatus"),
            "reviewDecision": pr.get("reviewDecision"),
            "headRefName": pr.get("headRefName"),
            "headRefOid": pr.get("headRefOid"),
            "author": (pr.get("author") or {}).get("login"),
        },
        "checks": checks,
        "issueComments": issue,
        "reviewComments": review_comment,
        "reviews": review_items,
    }
    return snapshot, repo_root


def state_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "state": snapshot["pr"]["state"],
        "mergeStateStatus": snapshot["pr"]["mergeStateStatus"],
        "reviewDecision": snapshot["pr"]["reviewDecision"],
        "headRefOid": snapshot["pr"]["headRefOid"],
        "issueCommentIds": [row["id"] for row in snapshot["issueComments"]],
        "reviewCommentIds": [row["id"] for row in snapshot["reviewComments"]],
        "reviewIds": [row["id"] for row in snapshot["reviews"]],
        "checks": snapshot["checks"],
    }


def render_once(snapshot: dict[str, Any], delta: dict[str, Any], actions: list[str]) -> dict[str, Any]:
    return {
        "pr": snapshot["pr"],
        "checks": snapshot["checks"],
        "delta": delta,
        "actions": actions,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Snapshot or watch GitHub PR state.")
    parser.add_argument("--pr", default="auto", help="PR number, URL, or 'auto'")
    parser.add_argument("--once", action="store_true", help="Print one JSON snapshot")
    parser.add_argument("--watch", action="store_true", help="Poll and emit JSONL snapshots")
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Polling interval in seconds for --watch",
    )
    parser.add_argument(
        "--state-file",
        help="Optional explicit state file path. Defaults to .git/.otto-pr-watch/pr-<n>.json",
    )
    parser.add_argument(
        "--cwd",
        default=".",
        help="Repository working directory (defaults to current directory)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.once and not args.watch:
        args.once = True

    cwd = Path(args.cwd).expanduser().resolve()

    try:
        while True:
            snapshot, repo_root = build_snapshot(cwd, args.pr)
            pr_number = snapshot["pr"]["number"]
            state_file = (
                Path(args.state_file).expanduser().resolve()
                if args.state_file
                else default_state_file(repo_root, pr_number)
            )
            previous_state = load_state(state_file)
            delta = summarize_delta(previous_state, snapshot)
            actions = compute_actions(snapshot, delta)
            payload = render_once(snapshot, delta, actions)

            print(json.dumps(payload, indent=None if args.watch else 2))
            sys.stdout.flush()

            save_state(state_file, state_payload(snapshot))

            if not args.watch:
                return 0

            if "stop_pr_closed" in actions:
                return 0

            time.sleep(max(args.interval, 5))
    except WatchError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
