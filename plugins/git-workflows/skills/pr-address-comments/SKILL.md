---
name: pr-address-comments
description: Review and triage GitHub PR comments before making fixes. Use when the user asks to address review comments, summarize PR feedback, or decide which comments to act on first.
---

<!-- Adapted from the public Gemini CLI `pr-address-comments` skill and rewritten for generic Otto GitHub workflows. -->

# PR Address Comments

Use this workflow when the user wants help understanding or responding to GitHub PR feedback.

## Objective

Summarize the current PR feedback, identify what still needs action, and let the user choose what to fix or defer before editing code.

## Workflow

1. Determine which PR to inspect.
   - If the current branch already has an open PR, use that PR.
   - If not, ask the user for the PR number or URL.
2. Gather the current state with `gh`.
   - `gh pr view <PR> --comments`
   - `gh pr view <PR> --json number,title,url,reviewDecision,reviews,comments`
   - `gh pr diff <PR> --stat`
3. Review the current branch diff and recent commits if the PR branch is checked out locally.
4. Separate the feedback into:
   - still-open actionable comments
   - already-addressed comments
   - non-blocking suggestions or discussion points
5. Present the summary first. Do not start fixing comments automatically.
6. Let the user decide which items to fix, skip, or answer.
7. After the user chooses a subset, make targeted edits, run relevant validation, and only then help draft replies or resolution summaries if asked.

## Guardrails

- Do not assume every comment should be implemented.
- Do not auto-resolve threads without user direction.
- Prefer a concise numbered summary of actionable comments so the user can prioritize quickly.
- If the current user already replied to a thread, take that context into account before proposing another answer.
- If the PR includes automated review comments and human comments, label them separately in the summary.
