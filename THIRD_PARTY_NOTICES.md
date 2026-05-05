# Third-Party Notices

This repository includes Otto-native plugins and adapted content derived from public Apache-licensed skill examples originally published in:

- the public `anthropics/skills` repository
- the public `openai/codex` sample skills tree
- the public `cline` repository
- the public `gemini-cli` repository

Adapted content has been cleaned for Otto naming, `.otto` paths, Otto-host workflows, and explicit modified-file notices before inclusion here.

This marketplace also catalogs third-party upstream plugins via remote `marketplace.json` entries. Those entries are referenced by source and are not copied into this repository. Otto only indexes public directory entries when they already point to an explicit upstream repository or package source, and those entries are tagged with `indexed-from-public-plugin-directory`.

Included as adapted Apache-licensed source:

- `frontend-design`
- `web-artifacts-builder`
- `webapp-testing`
- `skill-creator`
- `mcp-builder`
- `internal-comms`
- `canvas-design`
- `algorithmic-art`
- `theme-factory`
- `slack-gif-creator`
- `doc-coauthoring`

Included as adapted Apache-licensed source from Codex sample skills:

- `plugin-creator`
- `skill-installer`

Included as adapted Apache-licensed source from Cline:

- `create-pull-request`

Included as adapted Apache-licensed source from Gemini CLI:

- `pr-creator` guidance consolidated into `create-pull-request`
- `pr-address-comments`
- `async-pr-review`

Additional Otto-native reimplementation inspired by public Codex workflow ideas:

- `babysit-pr`

Intentionally excluded from this repository:

- Anthropic-restricted/source-available document skills such as `docx`, `pdf`, `pptx`, and `xlsx`
- Anthropic-specific branding content such as `brand-guidelines`
- Product-specific API guidance such as `claude-api`
- Content with no clear redistribution license unless it is reimplemented Otto-native from scratch

Remote mirrored entries follow a different rule:

- the catalog metadata lives here
- the plugin code stays upstream
- licensing remains with the upstream repository referenced by the entry source
- upstream-managed entries must not be presented as Otto-authored plugins
- vendored `external_plugins/*` copies inside Anthropic's public marketplace repo are not used as Otto install sources

Otto-maintained MCP compatibility wrappers follow another rule:

- the wrapper manifest is authored in this repository
- the server implementation remains with the upstream vendor or community project
- no Anthropic-authored plugin code is copied into the wrapper
- wrapper plugins currently cover `context7`, `firebase`, `github`, `gitlab`, `greptile`, `laravel-boost`, `linear`, `playwright-mcp`, `serena`, and `terraform`

Where the original Apache-licensed source included a `LICENSE.txt`, that notice has been preserved alongside the adapted skill when copied directly. Rewritten ports carry plugin-level `NOTICE` files plus inline modified-file notices.
