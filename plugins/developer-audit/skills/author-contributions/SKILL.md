---
name: author-contributions
description: Identify which files a specific author contributed to on a branch compared with an upstream, including rename chains. Use when the user asks who changed what, what files an author touched, or to audit authorship before a merge.
---

# Author Contributions

Use this workflow when the user wants to know which files a specific author contributed to on a branch, even if files were renamed before the branch lands.

## When to use

- "Which files did Alice actually touch on this branch?"
- "What code from Bob will land if we merge this PR?"
- "Audit authorship before merge"
- "Show me the files this person contributed to, including renames"

## Recommended workflow

1. Resolve the exact git identity first.

```bash
git log --format="%an <%ae>" <upstream>..<branch> | sort -u
```

2. Match the requested person to the exact identity string that appears in git history.
3. Collect commits by that exact author in the branch range.
4. Collect the files touched by those commits.
5. Build a rename graph across all commits in the same range so later file names can be traced back to earlier paths.
6. Compare against the final merge diff and classify each landing file as:
   - `DIRECT`: the author touched the file under its current path
   - `VIA_RENAME`: the author touched an ancestor path that later became the current file
7. Present the result as a compact table and include line stats where possible.

## Use the helper script

Run the helper script from the repository root you want to audit:

```bash
python3 plugins/developer-audit/skills/author-contributions/scripts/audit_author_contributions.py \
  --author "Full Name" \
  --upstream main \
  --branch HEAD
```

Useful options:

- `--format markdown` for a ready-to-share table
- `--format json` for machine-readable output
- `--repo /path/to/repo` to audit another checkout
- `--author-match exact` when the input should only match one exact git identity

## Guardrails

- Do not guess the author identity if multiple close matches exist.
- Build the rename graph from all commits in the branch range, not only the target author's commits.
- Only report files that still appear in the merge diff versus the upstream.
- If the result set is large, summarize the totals first and then show the table.
