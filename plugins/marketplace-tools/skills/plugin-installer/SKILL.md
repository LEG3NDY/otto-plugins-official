---
name: plugin-installer
description: Add Otto plugin marketplaces, install plugins from them, and inspect local plugin state. Use when the user asks what plugins are available, wants to add or update a marketplace, or needs to install, enable, disable, or troubleshoot a plugin.
---

<!-- Adapted from the public openai/codex `skill-installer` sample and rewritten for Otto plugin marketplaces and `~/.otto/plugins` state. -->

# Plugin Installer

This skill handles Otto-native plugin installation and marketplace management. Do not treat Otto plugins like standalone skill folders and do not copy them into unrelated runtime directories.

## When to use

- User asks what plugins or marketplaces are available
- User wants to add, list, update, or remove a marketplace
- User wants to install, uninstall, enable, disable, or update a plugin
- User wants to inspect `known_marketplaces.json` or `installed_plugins.json`
- User wants to validate a local marketplace checkout before using it

## Default workflow

1. Determine whether the request is about:
   - marketplace discovery or configuration
   - a specific plugin install or management action
   - debugging local plugin state
2. Use Otto's built-in plugin commands first:

```bash
otto plugin marketplace list --json
otto plugin list --json
```

3. If the user is asking about raw local state, inspect:
   - `~/.otto/plugins/known_marketplaces.json`
   - `~/.otto/plugins/installed_plugins.json`
   - or `scripts/inspect_plugin_state.py --format json`
4. To add a marketplace, use:

```bash
otto plugin marketplace add <source>
```

Supported sources include:
- GitHub repos like `LEG3NDY/otto-plugins-official`
- URLs
- local directories
- local `marketplace.json` files

5. To install a plugin, prefer the explicit marketplace-qualified form:

```bash
otto plugin install <plugin>@<marketplace>
```

Examples:
- `otto plugin install frontend-design@otto-plugins-official`
- `otto plugin install plugin-builder@otto-plugins-official`

6. After install, update, or removal, verify with:

```bash
otto plugin list --json
python3 plugins/marketplace-tools/skills/plugin-installer/scripts/inspect_plugin_state.py
```

## Scope and state rules

- Use `--scope user`, `--scope project`, or `--scope local` when the user needs a specific installation scope.
- `known_marketplaces.json` stores configured marketplace sources.
- `installed_plugins.json` stores installation metadata and on-disk cache locations.
- Enabled or disabled intent lives in Otto settings, not only in `installed_plugins.json`.
- Do not install Otto plugins by manually copying directories into Otto cache folders.
- Do not delete marketplaces or installed plugin data unless the user explicitly asks.

## Local marketplace workflow

When the user points at a local marketplace checkout:

1. Read its `.otto-plugin/marketplace.json` directly instead of guessing.
2. Validate the checkout before installation when possible:

```bash
otto plugin validate /absolute/path/to/marketplace-or-plugin
```

3. Add the local checkout as a directory marketplace if the user wants to install from it repeatedly:

```bash
otto plugin marketplace add /absolute/path/to/otto-plugins-official
```

## Troubleshooting

- If a plugin name resolves ambiguously, use the explicit `plugin@marketplace` form.
- If a marketplace is configured but stale, run `otto plugin marketplace update <name>`.
- If the user asks "what is installed?", prefer `otto plugin list --json` and cross-check with `installed_plugins.json`.
- If the user asks "what is available in this repo?", read the local `.otto-plugin/marketplace.json` file directly.
- Remote marketplace add or update operations may require network access.

## Reference

For concrete command patterns and the state-file layout, read:

- `references/otto-plugin-commands.md`
