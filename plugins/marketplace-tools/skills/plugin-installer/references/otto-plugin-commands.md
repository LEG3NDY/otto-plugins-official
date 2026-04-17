# Otto Plugin Command Reference

<!-- Adapted from the public openai/codex `skill-installer` sample and rewritten for Otto plugin marketplaces and local state inspection. -->

Use these commands for Otto-native plugin and marketplace operations.

## Marketplace commands

```bash
otto plugin marketplace list
otto plugin marketplace list --json
otto plugin marketplace add LEG3NDY/otto-plugins-official
otto plugin marketplace add /absolute/path/to/otto-plugins-official
otto plugin marketplace update
otto plugin marketplace update otto-plugins-official
otto plugin marketplace remove <marketplace-name>
```

## Plugin commands

```bash
otto plugin install <plugin>@<marketplace>
otto plugin uninstall <plugin>@<marketplace>
otto plugin enable <plugin>@<marketplace>
otto plugin disable <plugin>@<marketplace>
otto plugin update <plugin>@<marketplace>
otto plugin list
otto plugin list --json
otto plugin validate /absolute/path/to/marketplace-or-plugin
```

## State files

Otto stores plugin state under `~/.otto/plugins/`:

- `known_marketplaces.json`: configured marketplace sources
- `installed_plugins.json`: installed plugin metadata and cache locations
- `marketplaces/`: cached marketplace manifests or cloned checkouts
- `cache/`: installed plugin payload cache

## Practical guidance

- Use `plugin@marketplace` whenever the source is not obvious.
- Prefer Otto's built-in commands over manually editing plugin state files.
- Read raw JSON state only when the user asks for debugging detail or when the built-in command output is not enough.
- For local marketplace repos, inspect `.otto-plugin/marketplace.json` directly before installation.
