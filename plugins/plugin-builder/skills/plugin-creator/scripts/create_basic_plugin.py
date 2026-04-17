#!/usr/bin/env python3
"""Scaffold an Otto plugin directory and optionally update marketplace.json.

Adapted from the public openai/codex `plugin-creator` sample and rewritten for
the Otto/LEG3NDY `.otto-plugin` marketplace format.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


MAX_PLUGIN_NAME_LENGTH = 64
DEFAULT_PLUGIN_PARENT = Path.cwd() / "plugins"
DEFAULT_MARKETPLACE_PATH = Path.cwd() / ".otto-plugin" / "marketplace.json"
DEFAULT_VERSION = "0.1.0"
DEFAULT_CATEGORY = "developer-tools"


def normalize_plugin_name(plugin_name: str) -> str:
    normalized = plugin_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def validate_plugin_name(plugin_name: str) -> None:
    if not plugin_name:
        raise ValueError("Plugin name must include at least one letter or digit.")
    if len(plugin_name) > MAX_PLUGIN_NAME_LENGTH:
        raise ValueError(
            f"Plugin name '{plugin_name}' is too long ({len(plugin_name)} characters). "
            f"Maximum is {MAX_PLUGIN_NAME_LENGTH} characters."
        )


def build_plugin_json(plugin_name: str, version: str) -> dict[str, Any]:
    return {
        "name": plugin_name,
        "version": version,
        "description": "[TODO: Brief plugin description]",
        "author": {
            "name": "OttoAI",
            "url": "https://github.com/LEG3NDY/otto-plugins-official",
        },
        "homepage": "https://github.com/LEG3NDY/otto-plugins-official",
        "repository": "https://github.com/LEG3NDY/otto-plugins-official",
        "license": "Apache-2.0",
        "keywords": [
            "[TODO: keyword-1]",
            "[TODO: keyword-2]",
        ],
        "skills": "./skills",
    }


def build_marketplace_entry(
    plugin_name: str,
    category: str,
    version: str,
    tags: list[str],
    strict: bool,
) -> dict[str, Any]:
    return {
        "name": plugin_name,
        "description": "[TODO: Brief plugin description]",
        "category": category,
        "tags": tags or ["[TODO: tag-1]", "[TODO: tag-2]"],
        "source": f"./plugins/{plugin_name}",
        "version": version,
        "strict": strict,
    }


def load_json(path: Path) -> dict[str, Any]:
    with path.open() as handle:
        return json.load(handle)


def build_default_marketplace() -> dict[str, Any]:
    return {
        "name": "[TODO: marketplace-name]",
        "owner": {
            "name": "[TODO: Owner Name]",
            "url": "[TODO: https://github.com/org/repo]",
        },
        "metadata": {
            "version": DEFAULT_VERSION,
            "description": "[TODO: Marketplace description]",
        },
        "plugins": [],
    }


def validate_marketplace(payload: dict[str, Any], marketplace_path: Path) -> None:
    if not isinstance(payload, dict):
        raise ValueError(f"{marketplace_path} must contain a JSON object.")

    plugins = payload.get("plugins")
    if plugins is None:
        payload["plugins"] = []
        return
    if not isinstance(plugins, list):
        raise ValueError(f"{marketplace_path} field 'plugins' must be an array.")


def write_json(path: Path, data: dict[str, Any], force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists. Use --force to overwrite.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def update_marketplace_json(
    marketplace_path: Path,
    plugin_name: str,
    category: str,
    version: str,
    tags: list[str],
    strict: bool,
    force: bool,
) -> None:
    payload = load_json(marketplace_path) if marketplace_path.exists() else build_default_marketplace()
    validate_marketplace(payload, marketplace_path)

    plugins = payload["plugins"]
    new_entry = build_marketplace_entry(plugin_name, category, version, tags, strict)

    for index, entry in enumerate(plugins):
        if isinstance(entry, dict) and entry.get("name") == plugin_name:
            if not force:
                raise FileExistsError(
                    f"Marketplace entry '{plugin_name}' already exists in {marketplace_path}. "
                    "Use --force to overwrite that entry."
                )
            plugins[index] = new_entry
            break
    else:
        plugins.append(new_entry)

    write_json(marketplace_path, payload, force=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an Otto plugin skeleton with placeholder manifests."
    )
    parser.add_argument("plugin_name")
    parser.add_argument(
        "--path",
        default=str(DEFAULT_PLUGIN_PARENT),
        help="Parent directory for plugin creation (defaults to <cwd>/plugins).",
    )
    parser.add_argument("--with-skills", action="store_true", help="Create skills/ directory")
    parser.add_argument("--with-scripts", action="store_true", help="Create scripts/ directory")
    parser.add_argument("--with-assets", action="store_true", help="Create assets/ directory")
    parser.add_argument(
        "--with-marketplace",
        action="store_true",
        help="Create or update <cwd>/.otto-plugin/marketplace.json.",
    )
    parser.add_argument(
        "--marketplace-path",
        default=str(DEFAULT_MARKETPLACE_PATH),
        help="Path to marketplace.json (defaults to <cwd>/.otto-plugin/marketplace.json).",
    )
    parser.add_argument(
        "--category",
        default=DEFAULT_CATEGORY,
        help="Marketplace category value",
    )
    parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Marketplace tag value. Pass multiple times for multiple tags.",
    )
    parser.add_argument(
        "--version",
        default=DEFAULT_VERSION,
        help="Plugin version string",
    )
    parser.add_argument(
        "--non-strict",
        action="store_true",
        help="Set marketplace strict=false for the generated entry.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_plugin_name = args.plugin_name
    plugin_name = normalize_plugin_name(raw_plugin_name)
    if plugin_name != raw_plugin_name:
        print(f"Note: Normalized plugin name from '{raw_plugin_name}' to '{plugin_name}'.")
    validate_plugin_name(plugin_name)

    plugin_root = Path(args.path).expanduser().resolve() / plugin_name
    plugin_root.mkdir(parents=True, exist_ok=True)

    plugin_json_path = plugin_root / ".otto-plugin" / "plugin.json"
    write_json(plugin_json_path, build_plugin_json(plugin_name, args.version), args.force)

    optional_directories = {
        "skills": args.with_skills,
        "scripts": args.with_scripts,
        "assets": args.with_assets,
    }
    for folder, enabled in optional_directories.items():
        if enabled:
            (plugin_root / folder).mkdir(parents=True, exist_ok=True)

    if args.with_marketplace:
        marketplace_path = Path(args.marketplace_path).expanduser().resolve()
        update_marketplace_json(
            marketplace_path=marketplace_path,
            plugin_name=plugin_name,
            category=args.category,
            version=args.version,
            tags=args.tag,
            strict=not args.non_strict,
            force=args.force,
        )

    print(f"Created plugin scaffold: {plugin_root}")
    print(f"plugin manifest: {plugin_json_path}")
    if args.with_marketplace:
        print(f"marketplace manifest: {marketplace_path}")


if __name__ == "__main__":
    main()
