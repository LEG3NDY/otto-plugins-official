---
name: babysit-pr
description: Monitor an open GitHub pull request over time, surface new feedback or failing checks, and keep reporting deltas until the PR is stable or user help is required.
---

<!-- Otto-native reimplementation inspired by the public Codex `babysit-pr` workflow. -->

# Babysit PR

Use this workflow when the user wants Otto to keep an eye on an open PR instead of doing only a one-shot check.

## Objective

Track PR state over time and surface meaningful changes:

- new failing or recovered checks
- new review comments or review submissions
- mergeability changes
- draft/open/closed/merged transitions

The goal is to keep the user updated on what changed, not to spam them with identical snapshots.

## Inputs

Accept:

- no explicit PR target, meaning "use the PR for the current branch"
- a PR number
- a PR URL

## Recommended workflow

1. Start with a one-shot snapshot:

```bash
python3 plugins/git-workflows/skills/babysit-pr/scripts/watch_pr_status.py --pr auto --once
```

2. If the user wants ongoing monitoring, switch to watch mode:

```bash
python3 plugins/git-workflows/skills/babysit-pr/scripts/watch_pr_status.py --pr auto --watch
```

3. Read the structured output and focus on the `actions`, `delta`, and summary fields.
4. If checks fail, diagnose the failures before deciding whether the issue is flaky, branch-related, or needs user help.
5. If new review feedback appears, surface it quickly and decide with the user whether to fix it now.
6. If the PR reaches a stable green state, report that clearly, but keep watching while the PR remains open if the user asked for monitoring.

## Actions you may see

- `stop_pr_closed`: the PR is no longer open
- `review_new_feedback`: new comments or review submissions appeared since the last snapshot
- `diagnose_failed_checks`: at least one check is failing
- `wait_for_pending_checks`: checks are still running or queued
- `ready_for_handoff`: checks are green and no obvious blocking review decision is present
- `continue_watch`: the PR is still open and should continue being monitored

## State tracking

The helper script stores a compact state file so later snapshots can report deltas instead of re-reporting the entire PR every time.

Default state location:

```text
.git/.otto-pr-watch/pr-<number>.json
```

Override it with `--state-file` when needed.

## Guardrails

- Do not assume failing checks are flaky without reading their logs.
- Do not auto-fix review comments unless the user asked for that next step.
- Do not stop monitoring just because one snapshot is idle if the PR is still open and the user asked for ongoing watch.
- If `gh` is unavailable or unauthenticated, stop and explain the gap.
