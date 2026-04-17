---
name: async-pr-review
description: Start or inspect a background PR review run. Use when the user wants PR checks to run in the background, wants to come back later for a summary, or needs a structured async review workflow.
---

<!-- Adapted from the public Gemini CLI `async-pr-review` skill and rewritten for Otto-native background review patterns and log-based status checks. -->

# Async PR Review

Use this workflow when the user wants a PR review process to continue in the background and return a status summary later.

## Core idea

The Otto-native version focuses on deterministic background work first:

- fetch PR metadata and diff
- run project-native checks such as preflight, lint, build, or tests when those commands are known
- capture all output to log files
- later synthesize the logs and diff into a concise review summary

Do not assume background LLM inference is available. If the runtime supports automations or background shells, use them. Otherwise, explain that async review is unavailable and offer a synchronous review instead.

## Determine action

Figure out whether the user wants to:

- start a new async review
- check the status of an existing async review

## Start review

1. Identify the PR number.
2. Create a dedicated log directory and, when needed, a temporary worktree or isolated checkout.
3. Capture baseline artifacts:
   - `gh pr diff <PR>` into a diff file
   - repo metadata and current command choices into a small status file
4. Start background jobs for the project-native checks that make sense for the repository.
   - Prefer documented commands such as `npm run preflight`, `bun run test`, `pytest`, or the repo's own validation scripts.
   - Write each check to its own log file.
5. Tell the user where the logs live and how to ask for status later.

## Check status

1. Inspect the log directory and any status files.
2. If checks are still running, report which jobs are incomplete.
3. If checks are complete, read the diff and the logs, then summarize:
   - whether build or lint checks passed
   - whether tests passed
   - the most important warnings or failures
   - whether the PR looks ready for deeper review or fixes

## Guardrails

- Use an isolated worktree or temp checkout instead of mutating the user's main workspace.
- Do not auto-fix code while the async run is still collecting evidence.
- Do not invent build or test commands. Use repo-native commands only.
- Keep log output on disk so the user can revisit it later.
- If background execution is unsupported in the current environment, say so clearly and offer the synchronous alternative.
