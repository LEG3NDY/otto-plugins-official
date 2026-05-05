# Otto Plugins Official

Official plugin marketplace for Otto.

This repository contains curated plugins that extend Otto with reusable skills, automation workflows, and future MCP or agent integrations.

The marketplace now has two catalog layers:

- Otto-native official plugins stored under `./plugins/*`
- curated third-party upstream plugins referenced remotely from `marketplace.json`

## What Lives Here

Each plugin in this marketplace is a self-contained package that Otto can install and expose to the user.

Official plugins:

- `frontend-design`
  Design and frontend workflow skills for stronger UI direction, hierarchy, responsiveness, polish, and richer web artifacts.
- `frontend-qa`
  Visual regression, screenshot baseline refresh, and frontend QA artifact workflows for Otto repositories.
- `creative-studio`
  Visual composition, generative art, theme, and animated media skills for posters, static artwork, themed outputs, interactive art, and Slack-ready GIFs.
- `doc-workflows`
  Structured documentation co-authoring workflows for specs, proposals, RFCs, and decision documents.
- `developer-audit`
  Git authorship and contribution audit workflows for branch, merge, and PR analysis.
- `git-workflows`
  Pull-request creation, review, async review, babysitting, and feedback-handling workflows for Otto repositories.
- `playwright`
  Browser QA and E2E workflow skills for smoke tests, visual verification, and reproducible web bug reports.
- `mcp-builder`
  MCP server planning and implementation guidance for Node/TypeScript and Python.
- `internal-comms`
  Internal writing workflows for updates, newsletters, FAQs, and structured status communication.
- `marketplace-tools`
  Plugin installation, marketplace configuration, and local plugin-state inspection workflows for Otto users and maintainers.
- `plugin-builder`
  Plugin scaffolding and marketplace maintenance workflows for Otto/LEG3NDY plugin authors.
- `skill-creator`
  Skill authoring workflows for creating, refining, and standardizing Otto skills.
- LSP plugins
  Code intelligence adapters for TypeScript/JavaScript, HTML, CSS, JSON, Markdown, TOML, YAML, Python, Rust, Go, and C/C++.

Curated third-party catalog:

- indexed from public plugin directories only when the entry already points to an explicit upstream repository or package source
- installed from their upstream repositories instead of being copied into this repo
- tagged with `third-party`, `upstream-managed`, and `indexed-from-public-plugin-directory`
- kept separate from Otto-authored plugins even though they are discoverable from the same marketplace
- does not install from vendored `external_plugins/*` copies inside Anthropic's public marketplace repo
- includes a small set of Otto-maintained compatibility wrappers for vendor/community MCP servers where the useful integration is the MCP config itself rather than third-party plugin code

## How Users Benefit

The goal of this marketplace is to give Otto a clean official surface for reusable workflows that should be installable and versioned independently from the host.

That includes capabilities such as:

- design guidance
- creative production
- documentation co-authoring
- browser QA
- frontend QA
- MCP implementation workflows
- internal communications
- developer audit
- marketplace operations
- plugin authoring
- git workflows
- reusable development workflows
- LSP code intelligence
- future MCP integrations
- future agent packs

## Repository Layout

```text
otto-plugins-official/
├── .otto-plugin/
│   └── marketplace.json
└── plugins/
    ├── creative-studio/
    ├── doc-workflows/
    ├── developer-audit/
    ├── frontend-design/
    ├── frontend-qa/
    ├── git-workflows/
    ├── internal-comms/
    ├── marketplace-tools/
    ├── mcp-builder/
    ├── playwright/
    ├── plugin-builder/
    ├── skill-creator/
    ├── typescript-lsp/
    ├── html-lsp/
    ├── css-lsp/
    ├── json-lsp/
    ├── markdown-lsp/
    ├── toml-lsp/
    ├── yaml-lsp/
    ├── pyright-lsp/
    ├── rust-analyzer-lsp/
    ├── gopls-lsp/
    └── clangd-lsp/
```

## Sourcing

This repository publishes the official Otto plugin marketplace.

Most plugin content here is Otto-native or adapted from Apache-licensed public skill examples, with plugin-level `NOTICE` files and modified-file attribution notices where content was rewritten. Anthropic-restricted/source-available document skills and content without clear redistribution terms are intentionally excluded from this repository. See `THIRD_PARTY_NOTICES.md` for attribution and sourcing notes.

Third-party mirrored entries are not redistributed here. The marketplace only points Otto to their upstream sources using supported remote plugin source types such as `url`, `github`, and `git-subdir`.

For a source-by-source inclusion summary, see [docs/SKILL_PORTING_MATRIX.md](./docs/SKILL_PORTING_MATRIX.md).
