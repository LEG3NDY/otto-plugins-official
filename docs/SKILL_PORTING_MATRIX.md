# Skill Porting Matrix

This document summarizes source skill inventories evaluated for Otto/LEG3NDY marketplace inclusion and classifies them for the plugin format used in this repository.

## Status legend

- `ported`: already available in `otto-plugins-official`
- `port-now`: low-friction candidate that can be adapted directly to Otto/LEG3NDY
- `port-with-rewrite`: useful idea, but the source is tightly coupled to another product, runtime, or schema
- `reference-only`: useful as inspiration, but too product-specific or environment-specific to ship here
- `blocked-license`: do not port into this repository without a clean Otto-native reimplementation

## Current additions

The marketplace currently includes these additions beyond the original starting set:

- `algorithmic-art` added under `creative-studio`
- `doc-coauthoring` added under `doc-workflows`
- `plugin-creator` added under `plugin-builder`
- `plugin-installer` added under `marketplace-tools`
- `create-pull-request` added under `git-workflows`
- `babysit-pr` reimplemented Otto-native under `git-workflows`
- `author-contributions` reimplemented Otto-native under `developer-audit`
- `update-screenshots` reimplemented Otto-native under `frontend-qa`

## Source: `anthropics/skills`

| Skill | Status | Target plugin | Notes |
| --- | --- | --- | --- |
| `canvas-design` | `ported` | `creative-studio` | Available in the current marketplace. |
| `slack-gif-creator` | `ported` | `creative-studio` | Available in the current marketplace. |
| `theme-factory` | `ported` | `creative-studio` | Available in the current marketplace. |
| `algorithmic-art` | `ported` | `creative-studio` | Apache-licensed source; required Otto branding cleanup. |
| `frontend-design` | `ported` | `frontend-design` | Available in the current marketplace. |
| `web-artifacts-builder` | `ported` | `frontend-design` | Available in the current marketplace. |
| `internal-comms` | `ported` | `internal-comms` | Available in the current marketplace. |
| `mcp-builder` | `ported` | `mcp-builder` | Available in the current marketplace. |
| `webapp-testing` | `ported` | `playwright` | Available in the current marketplace. |
| `skill-creator` | `ported` | `skill-creator` | Available in the current marketplace. |
| `doc-coauthoring` | `ported` | `doc-workflows` | Generic workflow; needed Otto terminology and web/runtime cleanup. |
| `brand-guidelines` | `port-with-rewrite` | `leg3ndy-brand` | Source is explicitly Anthropic-branded. Rebuild around Otto/LEG3NDY brand assets instead of search/replace. |
| `claude-api` | `port-with-rewrite` | `leg3ndy-api` | High-value, but deeply coupled to Anthropic/Claude SDKs and model naming. Needs a real Otto/LEG3NDY API surface first. |
| `docx` | `blocked-license` | n/a | Source-available Anthropic document skill. Reimplement Otto-native version instead of porting. |
| `pdf` | `blocked-license` | n/a | Same constraint as `docx`. |
| `pptx` | `blocked-license` | n/a | Same constraint as `docx`. |
| `xlsx` | `blocked-license` | n/a | Same constraint as `docx`. |

## Source: `openai/codex` sample skills

| Skill | Status | Target plugin | Notes |
| --- | --- | --- | --- |
| `plugin-creator` | `ported` | `plugin-builder` | Rewritten to the `.otto-plugin` schema and marketplace format used here. |
| `skill-installer` | `ported` | `marketplace-tools` | Rewritten around Otto plugin marketplaces, `known_marketplaces.json`, and `installed_plugins.json`. |
| `imagegen` | `port-with-rewrite` | `creative-studio` or `image-tools` | Useful, but depends on Codex built-in tool semantics and OpenAI fallback docs. |
| `openai-docs` | `reference-only` | n/a | Valuable for provider-specific integrations, but not Otto/LEG3NDY-native marketplace content. |
| `skill-creator` | `ported` | `skill-creator` | Available in the current marketplace. |

## Source: Codex skills

| Skill | Status | Target plugin | Notes |
| --- | --- | --- | --- |
| `babysit-pr` | `ported` | `git-workflows` | Reimplemented Otto-native with `gh`-based snapshot/watch state and delta tracking. |
| `remote-tests` | `reference-only` | n/a | Tied to Codex remote executor concepts. |
| `test-tui` | `reference-only` | n/a | Codex TUI-specific. |

## Source: Copilot skills

| Skill | Status | Target plugin | Notes |
| --- | --- | --- | --- |
| `author-contributions` | `ported` | `developer-audit` | Reimplemented Otto-native from scratch. No source text was copied because no clear redistribution license was identified. |
| `update-screenshots` | `ported` | `frontend-qa` | Reimplemented Otto-native from scratch. No source text was copied because no clear redistribution license was identified. |
| `accessibility` | `blocked-license` | n/a | No clear redistribution license was identified. |
| `add-policy` | `blocked-license` | n/a | No clear redistribution license was identified. |
| `agent-sessions-layout` | `blocked-license` | n/a | No clear redistribution license was identified. |
| `azure-pipelines` | `blocked-license` | n/a | No clear redistribution license was identified. |
| `component-fixtures` | `blocked-license` | n/a | No clear redistribution license was identified. |
| `fix-errors` | `blocked-license` | n/a | No clear redistribution license was identified. |
| `hygiene` | `blocked-license` | n/a | No clear redistribution license was identified. |
| `memory-leak-audit` | `blocked-license` | n/a | No clear redistribution license was identified. |
| `sessions` | `blocked-license` | n/a | No clear redistribution license was identified. |
| `tool-rename-deprecation` | `blocked-license` | n/a | No clear redistribution license was identified. |

## Source: Gemini CLI skills

| Skill | Status | Target plugin | Notes |
| --- | --- | --- | --- |
| `async-pr-review` | `ported` | `git-workflows` | Rewritten around Otto-native background checks, log files, and later synthesis instead of Gemini headless inference. |
| `pr-address-comments` | `ported` | `git-workflows` | Rewritten as a generic Otto workflow for triaging GitHub PR comments before editing code. |
| `pr-creator` | `ported` | `git-workflows` | Consolidated into `create-pull-request` with stronger template and preflight guidance. |
| `docs-changelog` | `port-with-rewrite` | `doc-workflows` | Requires deeper review of Gemini-specific assumptions before inclusion. |
| `docs-writer` | `port-with-rewrite` | `doc-workflows` | Same as `docs-changelog`. |
| `github-issue-creator` | `port-with-rewrite` | `git-workflows` | Likely tied to Gemini repository process and requires Otto-native rewrite before inclusion. |
| `code-reviewer` | `reference-only` | n/a | Not currently suitable for marketplace inclusion without deeper review. |
| `string-reviewer` | `reference-only` | n/a | Repo/process-specific without adaptation. |

## Source: Cline skills

| Skill | Status | Target plugin | Notes |
| --- | --- | --- | --- |
| `create-pull-request` | `ported` | `git-workflows` | Rewritten for Otto conventions, then consolidated with Gemini `pr-creator` guidance. |

## Public inclusion constraints

- Do not port Anthropic-restricted document skills directly.
- Do not ship Anthropic branding or Claude API product guidance under Otto naming.
- Do not import content without a clear redistribution license into the public marketplace.
- Do not import highly product-specific VS Code, Gemini CLI, or Codex maintainer workflows without a deliberate Otto-native rewrite.
