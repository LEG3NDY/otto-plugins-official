# Otto Plugin Manifest Spec

<!-- Adapted from the public openai/codex `plugin-creator` sample reference and rewritten for the Otto/LEG3NDY `.otto-plugin` schema. -->

This repository uses a simple plugin manifest under `.otto-plugin/plugin.json`.

```json
{
  "name": "plugin-name",
  "version": "0.1.0",
  "description": "Brief plugin description",
  "author": {
    "name": "OttoAI",
    "url": "https://github.com/LEG3NDY/otto-plugins-official"
  },
  "homepage": "https://github.com/LEG3NDY/otto-plugins-official",
  "repository": "https://github.com/LEG3NDY/otto-plugins-official",
  "license": "Apache-2.0",
  "keywords": ["keyword-1", "keyword-2"],
  "skills": "./skills"
}
```

## Field guide

- `name`: plugin identifier; use kebab-case and keep it aligned with the folder name.
- `version`: semantic version string.
- `description`: short summary of what the plugin provides.
- `author`: publisher identity for the marketplace.
- `homepage`: documentation or repository homepage.
- `repository`: source repository URL.
- `license`: plugin license string.
- `keywords`: search and discovery tags.
- `skills`: relative path to the plugin skill directory.

## Path conventions

- The manifest must live at `<plugin-root>/.otto-plugin/plugin.json`.
- Path values should stay relative and begin with `./`.
- In this repository, plugins normally expose `./skills`.

# Otto Marketplace Spec

This repository keeps the marketplace definition at `.otto-plugin/marketplace.json`.

```json
{
  "name": "otto-plugins-official",
  "owner": {
    "name": "OttoAI",
    "url": "https://github.com/LEG3NDY/otto-plugins-official"
  },
  "metadata": {
    "version": "0.1.0",
    "description": "Official Otto marketplace with curated plugins."
  },
  "plugins": [
    {
      "name": "plugin-name",
      "description": "Brief plugin description",
      "category": "developer-tools",
      "tags": ["plugins", "authoring"],
      "source": "./plugins/plugin-name",
      "version": "0.1.0",
      "strict": true
    }
  ]
}
```

## Marketplace field guide

- `name`: marketplace identifier.
- `owner`: publisher metadata for the marketplace itself.
- `metadata`: top-level marketplace version and description.
- `plugins`: ordered plugin entries.

Each plugin entry should include:

- `name`: plugin identifier matching the plugin folder and plugin manifest.
- `description`: short plugin summary.
- `category`: marketplace bucket such as `design`, `browser`, `productivity`, or `developer-tools`.
- `tags`: searchable discovery terms.
- `source`: repository-relative path like `./plugins/plugin-name`.
- `version`: plugin version string.
- `strict`: boolean guard used by the current marketplace format.

## Marketplace generation rules

- Preserve existing `name`, `owner`, and `metadata` when adding entries.
- Append new plugin entries unless there is an explicit reorder request.
- Replace an existing entry for the same plugin only when overwrite is intentional.
- Keep `source` relative to the repository root as `./plugins/<plugin-name>`.
