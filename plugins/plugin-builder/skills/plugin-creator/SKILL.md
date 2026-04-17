---
name: plugin-creator
description: Create and scaffold Otto plugins with the `.otto-plugin/plugin.json` and `.otto-plugin/marketplace.json` format used by this repository. Use when Otto needs a new plugin skeleton, a new marketplace entry, or a safe starting point for expanding the official Otto/LEG3NDY plugin catalog.
---

<!-- Adapted from the public openai/codex `plugin-creator` sample skill and rewritten for the Otto/LEG3NDY marketplace format. -->

# Plugin Creator

This skill is for creating new plugins in the Otto/LEG3NDY marketplace format used by `otto-plugins-official`.

## Quick start

Run the scaffold script from the repository root:

```bash
python3 plugins/plugin-builder/skills/plugin-creator/scripts/create_basic_plugin.py my-plugin --with-skills --with-marketplace
```

This creates:

- `plugins/my-plugin/.otto-plugin/plugin.json`
- `plugins/my-plugin/skills/` if `--with-skills` is passed
- a new entry in `.otto-plugin/marketplace.json` if `--with-marketplace` is passed

## What this skill generates

- Plugin names are normalized to lowercase hyphen-case.
- The plugin folder name and plugin manifest `"name"` always match.
- The manifest format matches the current repository convention:
  - `.otto-plugin/plugin.json`
  - repo marketplace at `.otto-plugin/marketplace.json`
- Marketplace entries use the same shape as the existing official plugins:
  - `name`
  - `description`
  - `category`
  - `tags`
  - `source`
  - `version`
  - `strict`

## Workflow

1. Decide whether the new plugin belongs in this repository's official marketplace or in another parent directory.
2. Normalize the plugin name to hyphen-case.
3. Create the plugin root and `.otto-plugin/plugin.json`.
4. Create companion directories as needed:
   - `skills/`
   - `scripts/`
   - `assets/`
5. If the plugin should be visible in the official marketplace, append or replace its entry in `.otto-plugin/marketplace.json`.
6. Open the generated JSON placeholders and replace them with real metadata before publishing or relying on the plugin.

## Repository-specific rules

- Default plugin location is `<repo-root>/plugins/<plugin-name>`.
- Default marketplace location is `<repo-root>/.otto-plugin/marketplace.json`.
- Default plugin manifest location is `<plugin-root>/.otto-plugin/plugin.json`.
- Marketplace `source` must remain `./plugins/<plugin-name>` relative to the repository root.
- `strict` should default to `true` unless there is a deliberate reason to relax it.
- Categories should follow the existing marketplace vocabulary when possible:
  - `design`
  - `browser`
  - `productivity`
  - `developer-tools`

## Required behavior

- Always keep `.otto-plugin/plugin.json` present.
- Do not overwrite an existing plugin or marketplace entry unless the user explicitly asks for it or `--force` is used intentionally.
- Leave generated metadata as obvious placeholders when the real values are unknown.
- Preserve existing root marketplace metadata (`name`, `owner`, `metadata`) when updating `.otto-plugin/marketplace.json`.
- Append new marketplace entries unless the user explicitly requests reordering.

## Reference

For the exact plugin and marketplace shapes used here, read:

- `references/plugin-json-spec.md`

## Validation

After modifying the scaffold script, run:

```bash
python3 -m py_compile plugins/plugin-builder/skills/plugin-creator/scripts/create_basic_plugin.py
```
