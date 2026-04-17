---
name: create-pull-request
description: Create a GitHub pull request following repository conventions. Use when the user asks to open a PR, submit a branch for review, or turn local changes into a GitHub pull request.
---

<!-- Adapted from the public `cline` `create-pull-request` skill and Gemini CLI `pr-creator` guidance, then rewritten for Otto conventions, non-interactive git guidance, and `gh`-based PR creation. -->

# Create Pull Request

Use this workflow when the user wants a real GitHub pull request created.

## Preflight

Verify the local environment before touching the branch:

```bash
gh --version
gh auth status
git status --short
git branch --show-current
git remote show origin
```

If `gh` is missing or unauthenticated, explain the gap and stop until the user has that fixed.

## Branch and diff review

1. Identify the current branch. If it is the default branch (`main` or `master`), create or switch to a feature branch before opening a PR.
2. Identify the base branch from `git remote show origin`.
3. Review whether the working tree is clean. If intended PR changes are still unstaged or uncommitted, decide with the user whether to commit them now before creating the PR.
4. Review the commits and diff relative to the base branch:

```bash
git log origin/<base>..HEAD --oneline --no-decorate
git diff origin/<base>..HEAD --stat
```

5. Use commit messages, branch name, changed files, and existing docs to infer:
   - PR title
   - summary of the change
   - related issue or ticket, if any
   - testing performed

If critical context is missing, ask the user directly instead of inventing it.

## Repository rules

- Read the most appropriate PR template and follow it exactly:
  - `.github/pull_request_template.md`
  - `.github/PULL_REQUEST_TEMPLATE.md`
  - a specific template under `.github/PULL_REQUEST_TEMPLATE/`
- Never commit or push directly to the default branch.
- Prefer non-interactive git commands. Do not use interactive rebase unless the user explicitly asks for history rewriting.
- Do not discard unrelated working tree changes.
- If the working tree is dirty, confirm whether the current changes belong in the PR before proceeding.
- If the branch is not pushed yet, push it before creating the PR.
- If the repository has a standard preflight command such as `npm run preflight`, `bun run preflight`, or a documented equivalent, run it before creating a ready-for-review PR unless the user explicitly wants to skip it.

## PR creation flow

1. Draft the PR title and body.
2. Write the PR body to a temporary file rather than passing large markdown inline.
3. Create the PR with `gh pr create`.

Example:

```bash
gh pr create --title "PR title" --body-file /tmp/pr-body.md --base <base>
```

For draft PRs:

```bash
gh pr create --title "PR title" --body-file /tmp/pr-body.md --base <base> --draft
```

Use a draft PR when the user signals the work is still in progress or the branch still needs follow-up.

If the repository uses Conventional Commits for PR titles, keep the title aligned with that convention.

## After creation

- Return the PR URL.
- Mention whether the PR was created as draft or ready for review.
- If helpful, suggest obvious follow-up actions such as reviewers, labels, or a final pass on CI failures.

## Common issues

- No commits ahead of base: confirm the user is on the right branch.
- Branch not pushed: run `git push -u origin HEAD`.
- Existing PR already open: use `gh pr view` and tell the user instead of creating a duplicate.
- Merge conflicts with base: explain that the branch needs rebasing or conflict resolution before opening or merging cleanly.
