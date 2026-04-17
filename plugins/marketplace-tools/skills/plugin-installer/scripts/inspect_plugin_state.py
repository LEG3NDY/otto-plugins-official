#!/usr/bin/env python3
"""Inspect Otto marketplace and installed plugin state.

Adapted from the public openai/codex `skill-installer` helper pattern and
rewritten for Otto's `~/.otto/plugins` marketplace and installation files.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


def default_otto_home() -> Path:
    override = os.environ.get("OTTO_HOME")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".otto"


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def summarize_marketplaces(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []

    rows: list[dict[str, Any]] = []
    for name in sorted(payload):
        entry = payload.get(name)
        if not isinstance(entry, dict):
            continue
        source = entry.get("source")
        row: dict[str, Any] = {
            "name": name,
            "installLocation": entry.get("installLocation"),
            "autoUpdate": entry.get("autoUpdate"),
        }
        if isinstance(source, dict):
            row["sourceType"] = source.get("source")
            for key in ("repo", "url", "path", "ref"):
                if key in source:
                    row[key] = source.get(key)
            if "sparsePaths" in source:
                row["sparsePaths"] = source.get("sparsePaths")
        rows.append(row)
    return rows


def summarize_installed(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []

    plugins = payload.get("plugins")
    if not isinstance(plugins, dict):
        return []

    rows: list[dict[str, Any]] = []
    for plugin_id in sorted(plugins):
        entries = plugins.get(plugin_id)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            rows.append(
                {
                    "id": plugin_id,
                    "scope": entry.get("scope"),
                    "version": entry.get("version"),
                    "installPath": entry.get("installPath"),
                    "installedAt": entry.get("installedAt"),
                    "lastUpdated": entry.get("lastUpdated"),
                    "projectPath": entry.get("projectPath"),
                }
            )
    return rows


def render_text(
    otto_home: Path,
    marketplace_path: Path,
    installed_path: Path,
    marketplaces: list[dict[str, Any]],
    installed: list[dict[str, Any]],
) -> str:
    lines = [
        f"Otto home: {otto_home}",
        f"Marketplace config: {marketplace_path}",
        f"Installed plugins: {installed_path}",
        "",
        "Configured marketplaces:",
    ]

    if marketplaces:
        for row in marketplaces:
            bits = [f"- {row['name']}"]
            source_type = row.get("sourceType")
            if source_type:
                bits.append(f"[{source_type}]")
            if row.get("repo"):
                bits.append(f"repo={row['repo']}")
            if row.get("url"):
                bits.append(f"url={row['url']}")
            if row.get("path"):
                bits.append(f"path={row['path']}")
            if row.get("installLocation"):
                bits.append(f"installLocation={row['installLocation']}")
            lines.append(" ".join(bits))
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Installed plugin entries:")

    if installed:
        for row in installed:
            bits = [f"- {row['id']}"]
            if row.get("scope"):
                bits.append(f"[{row['scope']}]")
            if row.get("version"):
                bits.append(f"version={row['version']}")
            if row.get("installPath"):
                bits.append(f"path={row['installPath']}")
            lines.append(" ".join(bits))
    else:
        lines.append("- none")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect Otto marketplace and installed plugin state."
    )
    parser.add_argument(
        "--otto-home",
        default=str(default_otto_home()),
        help="Path to the Otto home directory (defaults to ~/.otto or OTTO_HOME).",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    otto_home = Path(args.otto_home).expanduser().resolve()
    plugins_root = otto_home / "plugins"
    marketplace_path = plugins_root / "known_marketplaces.json"
    installed_path = plugins_root / "installed_plugins.json"

    try:
        marketplaces_payload = load_json(marketplace_path)
        installed_payload = load_json(installed_path)
    except json.JSONDecodeError as exc:
        print(f"Error: Failed to parse plugin state JSON: {exc}", file=sys.stderr)
        return 1

    marketplaces = summarize_marketplaces(marketplaces_payload)
    installed = summarize_installed(installed_payload)

    if args.format == "json":
        payload = {
            "ottoHome": str(otto_home),
            "marketplaceConfig": str(marketplace_path),
            "installedPluginsConfig": str(installed_path),
            "marketplaces": marketplaces,
            "installedPlugins": installed,
        }
        print(json.dumps(payload, indent=2))
        return 0

    print(
        render_text(
            otto_home,
            marketplace_path,
            installed_path,
            marketplaces,
            installed,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
