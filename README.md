# Otto Plugins Official

Official plugin marketplace for Otto.

This repository contains curated plugins that extend Otto with reusable skills, automation workflows, and future MCP or agent integrations.

## What Lives Here

Each plugin in this marketplace is a self-contained package that Otto can install and expose to the user.

Current official plugins:

- `frontend-design`
  Design and frontend workflow skills for stronger UI direction, hierarchy, responsiveness, polish, and richer web artifacts.
- `creative-studio`
  Visual composition, theme, and animated media skills for posters, static artwork, themed outputs, and Slack-ready GIFs.
- `playwright`
  Browser QA and E2E workflow skills for smoke tests, visual verification, and reproducible web bug reports.
- `mcp-builder`
  MCP server planning and implementation guidance for Node/TypeScript and Python.
- `internal-comms`
  Internal writing workflows for updates, newsletters, FAQs, and structured status communication.
- `skill-creator`
  Skill authoring workflows for creating, refining, and standardizing Otto skills.

## How Users Benefit

The goal of this marketplace is to give Otto a clean official surface for high-value workflows that should be installable, reusable, and versioned independently from the host.

That includes capabilities such as:

- design guidance
- creative production
- browser QA
- MCP implementation workflows
- internal communications
- reusable development workflows
- future MCP integrations
- future agent packs

## Repository Layout

```text
otto-plugins-official/
├── .otto-plugin/
│   └── marketplace.json
└── plugins/
    ├── creative-studio/
    ├── frontend-design/
    ├── internal-comms/
    ├── mcp-builder/
    ├── playwright/
    └── skill-creator/
```

## Status

This repository is intended to become the canonical official marketplace consumed by `otto-code`.

Most plugin content here is Otto-native or adapted from Apache-licensed public skill examples, with Anthropic-restricted/source-available document skills intentionally excluded from this repository. See `THIRD_PARTY_NOTICES.md` for attribution and sourcing notes.

Maintainers working inside the OttoAI monorepo should use the internal maintenance guide in:

- `otto-code/docs/official-marketplace.md`
