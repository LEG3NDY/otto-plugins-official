# Skill Porting Matrix

This document audits the skill inventories found under `/Users/artth/Documents` and classifies them for the Otto/LEG3NDY marketplace format used in this repository.

## Status legend

- `ported`: already available in `otto-plugins-official`
- `port-now`: low-friction candidate that can be adapted directly to Otto/LEG3NDY
- `port-with-rewrite`: useful idea, but the source is tightly coupled to another product, runtime, or schema
- `reference-only`: useful as inspiration, but too product-specific or too local to ship here
- `blocked-license`: do not port into this repository without a clean Otto-native reimplementation

## Imported waves

This repository now includes these imported waves beyond the original starting set:

- `algorithmic-art` added under `creative-studio`
- `doc-coauthoring` added under `doc-workflows`
- `plugin-creator` added under `plugin-builder`
- `plugin-installer` added under `marketplace-tools`
- `create-pull-request` added under `git-workflows`
- `babysit-pr` reimplemented Otto-native under `git-workflows`
- `author-contributions` reimplemented Otto-native under `developer-audit`
- `update-screenshots` reimplemented Otto-native under `frontend-qa`

## Source: `/Users/artth/Documents/skills/skills`

| Skill | Status | Target plugin | Notes |
| --- | --- | --- | --- |
| `canvas-design` | `ported` | `creative-studio` | Already adapted. |
| `slack-gif-creator` | `ported` | `creative-studio` | Already adapted. |
| `theme-factory` | `ported` | `creative-studio` | Already adapted. |
| `algorithmic-art` | `ported` | `creative-studio` | Apache-licensed source; required Otto branding cleanup. |
| `frontend-design` | `ported` | `frontend-design` | Already adapted. |
| `web-artifacts-builder` | `ported` | `frontend-design` | Already adapted. |
| `internal-comms` | `ported` | `internal-comms` | Already adapted. |
| `mcp-builder` | `ported` | `mcp-builder` | Already adapted. |
| `webapp-testing` | `ported` | `playwright` | Already adapted. |
| `skill-creator` | `ported` | `skill-creator` | Already adapted. |
| `doc-coauthoring` | `ported` | `doc-workflows` | Generic workflow; needed Otto terminology and web/runtime cleanup. |
| `brand-guidelines` | `port-with-rewrite` | `leg3ndy-brand` | Source is explicitly Anthropic-branded. Rebuild around Otto/LEG3NDY brand assets instead of search/replace. |
| `claude-api` | `port-with-rewrite` | `leg3ndy-api` | High-value, but deeply coupled to Anthropic/Claude SDKs and model naming. Needs a real Otto/LEG3NDY API surface first. |
| `docx` | `blocked-license` | n/a | Source-available Anthropic document skill. Reimplement Otto-native version instead of porting. |
| `pdf` | `blocked-license` | n/a | Same constraint as `docx`. |
| `pptx` | `blocked-license` | n/a | Same constraint as `docx`. |
| `xlsx` | `blocked-license` | n/a | Same constraint as `docx`. |

## Source: `/Users/artth/Documents/codex/codex-rs/skills/src/assets/samples`

| Skill | Status | Target plugin | Notes |
| --- | --- | --- | --- |
| `plugin-creator` | `ported` | `plugin-builder` | Rewritten to the `.otto-plugin` schema and marketplace format used here. |
| `skill-installer` | `ported` | `marketplace-tools` | Rewritten around Otto plugin marketplaces, `known_marketplaces.json`, and `installed_plugins.json`. |
| `imagegen` | `port-with-rewrite` | `creative-studio` or `image-tools` | Useful, but depends on Codex built-in tool semantics and OpenAI fallback docs. |
| `openai-docs` | `reference-only` | n/a | Valuable for provider-specific integrations, but not Otto/LEG3NDY-native marketplace content. |
| `skill-creator` | `ported` | `skill-creator` | Otto already has an adapted skill-creator workflow. |

## Source: `/Users/artth/Documents/codex/.codex/skills`

| Skill | Status | Target plugin | Notes |
| --- | --- | --- | --- |
| `babysit-pr` | `ported` | `git-workflows` | Reimplemented Otto-native with `gh`-based snapshot/watch state and delta tracking. |
| `remote-tests` | `reference-only` | n/a | Tied to Codex remote executor concepts. |
| `test-tui` | `reference-only` | n/a | Codex TUI-specific. |

## Source: `/Users/artth/Documents/copilot skills/skills`

| Skill | Status | Target plugin | Notes |
| --- | --- | --- | --- |
| `author-contributions` | `ported` | `developer-audit` | Reimplemented Otto-native from scratch. No source text copied because the local checkout has no clear redistribution license. |
| `update-screenshots` | `ported` | `frontend-qa` | Reimplemented Otto-native from scratch. No source text copied because the local checkout has no clear redistribution license. |
| `accessibility` | `blocked-license` | n/a | No clear redistribution license found in the local checkout. |
| `add-policy` | `blocked-license` | n/a | No clear redistribution license found in the local checkout. |
| `agent-sessions-layout` | `blocked-license` | n/a | No clear redistribution license found in the local checkout. |
| `azure-pipelines` | `blocked-license` | n/a | No clear redistribution license found in the local checkout. |
| `component-fixtures` | `blocked-license` | n/a | No clear redistribution license found in the local checkout. |
| `fix-errors` | `blocked-license` | n/a | No clear redistribution license found in the local checkout. |
| `hygiene` | `blocked-license` | n/a | No clear redistribution license found in the local checkout. |
| `memory-leak-audit` | `blocked-license` | n/a | No clear redistribution license found in the local checkout. |
| `sessions` | `blocked-license` | n/a | No clear redistribution license found in the local checkout. |
| `tool-rename-deprecation` | `blocked-license` | n/a | No clear redistribution license found in the local checkout. |

## Source: `/Users/artth/Documents/gemini-cli/.gemini/skills`

| Skill | Status | Target plugin | Notes |
| --- | --- | --- | --- |
| `async-pr-review` | `ported` | `git-workflows` | Rewritten around Otto-native background checks, log files, and later synthesis instead of Gemini headless inference. |
| `pr-address-comments` | `ported` | `git-workflows` | Rewritten as a generic Otto workflow for triaging GitHub PR comments before editing code. |
| `pr-creator` | `ported` | `git-workflows` | Consolidated into `create-pull-request` with stronger template and preflight guidance. |
| `docs-changelog` | `port-with-rewrite` | `doc-workflows` | Likely adaptable, but needs inspection of Gemini-specific assumptions. |
| `docs-writer` | `port-with-rewrite` | `doc-workflows` | Same as `docs-changelog`. |
| `github-issue-creator` | `port-with-rewrite` | `git-workflows` | Good idea, but likely tied to Gemini repo process. |
| `code-reviewer` | `reference-only` | n/a | Worth reading later; needs deeper inspection before marketplace inclusion. |
| `string-reviewer` | `reference-only` | n/a | Likely too repo/process-specific without adaptation. |

## Source: `/Users/artth/Documents/cline/.agents/skills`

| Skill | Status | Target plugin | Notes |
| --- | --- | --- | --- |
| `create-pull-request` | `ported` | `git-workflows` | Rewritten for Otto conventions, then consolidated with Gemini `pr-creator` guidance. |

## Suggested next waves

1. Add heartbeat or automation-assisted monitoring to `git-workflows` on top of `babysit-pr`
2. Extend `frontend-qa` with report summarization or selective baseline acceptance workflows
3. `brand-guidelines` -> reauthor as `leg3ndy-brand`
4. `claude-api` -> only after a real `leg3ndy-api` SDK/docs surface exists
5. `imagegen` -> adapt only after deciding how much Otto should depend on built-in image tooling versus plugin content

## Explicit non-goals for this repository

- Do not port Anthropic-restricted document skills directly.
- Do not ship Anthropic branding or Claude API product guidance under Otto naming.
- Do not import content without a clear redistribution license into the public marketplace.
- Do not import highly product-specific VS Code, Gemini CLI, or Codex-local maintainer workflows without a deliberate Otto-native rewrite.
