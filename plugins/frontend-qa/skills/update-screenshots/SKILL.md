---
name: update-screenshots
description: Refresh screenshot baselines from CI artifacts instead of local captures. Use when screenshot tests fail in CI, when the user wants to accept new visual baselines, or when a PR produced a baseline artifact that should become the new source of truth.
---

# Update Screenshots

Use this workflow when screenshot baselines should come from CI rather than the developer machine.

## Goal

Find the most relevant Actions run for a branch or PR, download the artifact that contains screenshot outputs or diff assets, and use that material to update the repository baseline in a controlled way.

## Why this workflow exists

Visual baselines often differ across environments because of fonts, rendering, operating system behavior, or DPI. If the project treats CI as the visual source of truth, accept the CI artifact instead of trusting local screenshots.

## Recommended workflow

1. Identify the relevant workflow, artifact name, and branch or PR.
2. Find the latest run that actually produced the artifact:

```bash
python3 plugins/frontend-qa/skills/update-screenshots/scripts/download_screenshot_artifact.py --pr 123
```

3. If the result looks right, download it:

```bash
python3 plugins/frontend-qa/skills/update-screenshots/scripts/download_screenshot_artifact.py \
  --pr 123 \
  --download \
  --dir .tmp/screenshot-artifact
```

4. Inspect any diff report or generated images in the artifact.
5. Copy only the CI-generated baseline files into the project baseline location.
6. Review the resulting git diff before committing.
7. Commit with a clear message such as `test: refresh screenshot baselines from CI`.

## Common inputs

- `--pr <number>`: infer the branch from a PR
- `--branch <name>`: use a specific branch directly
- `--workflow <file-or-name>`: override the workflow selector
- `--artifact-name <name>`: override the artifact name
- `--run-id <id>`: skip lookup and use a specific run directly

## Guardrails

- Do not blindly replace unrelated baseline directories.
- Review the artifact contents before copying them into the repository.
- If no artifact is present, report that clearly instead of pretending the run is usable.
- If the repo uses Git LFS or special storage rules for screenshots, follow that repo's documented push flow before pushing the branch.
- Keep this plugin complementary to `playwright`: `playwright` is for browser execution and testing flows, while `frontend-qa` is for artifact-driven visual QA maintenance.
