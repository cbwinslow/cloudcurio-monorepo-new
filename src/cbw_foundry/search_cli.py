#!/usr/bin/env python3
"""cbw-search CLI - search and browse the CloudCurio inventory.

Commands::

    cbw-search index               Rebuild the registry/index.json
    cbw-search list [--type TYPE]  List all items (optionally by type)
    cbw-search query TERM          Search for items matching TERM
    cbw-search info NAME           Show full details for a named item
    cbw-search types               List available item types
    cbw-search summary             Show item count per type
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .inventory import ITEM_TYPES, Inventory

console = Console()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_root() -> Path:
    """Walk up from cwd to find the repo root (contains Makefile + agents/)."""
    cwd = Path.cwd()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "Makefile").exists() and (candidate / "agents").is_dir():
            return candidate
    return cwd


def _make_table(items: list[dict], title: str = "") -> Table:
    t = Table(title=title, show_lines=False, expand=False)
    t.add_column("Icon", style="bold", no_wrap=True, width=3)
    t.add_column("Type", style="cyan", no_wrap=True)
    t.add_column("Name", style="green bold", no_wrap=True)
    t.add_column("Version", style="dim", no_wrap=True)
    t.add_column("Description")
    t.add_column("Tags", style="dim")
    for item in items:
        tags = ", ".join(item.get("tags") or [])
        t.add_row(
            item.get("icon", ""),
            item.get("type", ""),
            item.get("name", ""),
            item.get("version", ""),
            item.get("description", "") or "",
            tags,
        )
    return t


def _output_json(items: list[dict]) -> None:
    print(json.dumps(items, indent=2, ensure_ascii=False))


def _output_plain(items: list[dict]) -> None:
    for item in items:
        icon = item.get("icon", "")
        name = item.get("name", "")
        item_type = item.get("type", "")
        desc = item.get("description", "") or ""
        path = item.get("path", "")
        print(f"{icon}  {item_type:<10}  {name:<35}  {desc[:60]:<60}  {path}")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_index(root: Path, args: argparse.Namespace) -> int:
    """Rebuild the inventory index."""
    inv = Inventory(root=root)
    items = inv.scan()
    inv.save()
    summary = inv.summary()
    console.print(f"[green]✓[/green] Indexed [bold]{len(items)}[/bold] items → [dim]{inv.index_path}[/dim]")
    for item_type, count in sorted(summary.items()):
        icon = ITEM_TYPES.get(item_type, "•")
        console.print(f"  {icon}  [cyan]{item_type:<12}[/cyan] {count}")
    return 0


def cmd_list(root: Path, args: argparse.Namespace) -> int:
    """List all inventory items."""
    inv = Inventory(root=root)
    items = inv.list_all(item_type=args.type)
    if not items:
        console.print("[yellow]No items found. Run 'cbw-search index' first.[/yellow]")
        return 1
    if args.format == "json":
        _output_json(items)
    elif args.format == "plain":
        _output_plain(items)
    else:
        title = f"CloudCurio Inventory ({args.type})" if args.type else "CloudCurio Inventory"
        console.print(_make_table(items, title=title))
    return 0


def cmd_query(root: Path, args: argparse.Namespace) -> int:
    """Search the inventory."""
    inv = Inventory(root=root)
    results = inv.search(args.term, item_type=args.type)
    if not results:
        console.print(f"[yellow]No results for '{args.term}'[/yellow]")
        return 1
    if args.format == "json":
        _output_json(results)
    elif args.format == "plain":
        _output_plain(results)
    else:
        console.print(_make_table(results, title=f"Search: {args.term}"))
    return 0


def cmd_info(root: Path, args: argparse.Namespace) -> int:
    """Show full details for a named item."""
    inv = Inventory(root=root)
    item = inv.get(args.name)
    if not item:
        console.print(f"[red]Not found:[/red] {args.name}")
        return 1
    if args.format == "json":
        _output_json([item])
        return 0
    icon = item.get("icon", "")
    console.rule(f"{icon} [bold]{item['name']}[/bold]")
    console.print(f"[cyan]Type:[/cyan]        {item.get('type', '')}")
    console.print(f"[cyan]Version:[/cyan]     {item.get('version', '')}")
    console.print(f"[cyan]Description:[/cyan] {item.get('description', '')}")
    console.print(f"[cyan]Tags:[/cyan]        {', '.join(item.get('tags') or [])}")
    console.print(f"[cyan]Path:[/cyan]        {item.get('path', '')}")
    if item.get("command"):
        console.print(f"[cyan]Command:[/cyan]     {item['command']}")
    return 0


def cmd_types(root: Path, args: argparse.Namespace) -> int:
    """List available item types."""
    inv = Inventory(root=root)
    for t in inv.types():
        icon = ITEM_TYPES.get(t, "•")
        print(f"{icon}  {t}")
    return 0


def cmd_summary(root: Path, args: argparse.Namespace) -> int:
    """Show item count per type."""
    inv = Inventory(root=root)
    summary = inv.summary()
    if not summary:
        console.print("[yellow]Index is empty. Run 'cbw-search index' first.[/yellow]")
        return 1
    t = Table(title="Inventory Summary")
    t.add_column("Type", style="cyan")
    t.add_column("Count", style="green bold", justify="right")
    for item_type, count in sorted(summary.items()):
        icon = ITEM_TYPES.get(item_type, "•")
        t.add_row(f"{icon} {item_type}", str(count))
    console.print(t)
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    root = _find_root()

    ap = argparse.ArgumentParser(
        prog="cbw-search",
        description="Search and browse the CloudCurio monorepo inventory.",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    # index
    sub.add_parser("index", help="Rebuild registry/index.json by scanning the repo")

    # list
    pl = sub.add_parser("list", help="List inventory items")
    pl.add_argument("--type", metavar="TYPE", help="Filter by type (agent|tool|skill|workflow|mcp|script)")
    pl.add_argument("--format", choices=["table", "json", "plain"], default="table")

    # query
    pq = sub.add_parser("query", help="Search inventory items")
    pq.add_argument("term", help="Search term")
    pq.add_argument("--type", metavar="TYPE", help="Restrict search to a specific type")
    pq.add_argument("--format", choices=["table", "json", "plain"], default="table")

    # info
    pi = sub.add_parser("info", help="Show details for a named item")
    pi.add_argument("name", help="Item name")
    pi.add_argument("--format", choices=["table", "json", "plain"], default="table")

    # types
    sub.add_parser("types", help="List available asset types")

    # summary
    sub.add_parser("summary", help="Show item counts per type")

    args = ap.parse_args()

    dispatch = {
        "index": cmd_index,
        "list": cmd_list,
        "query": cmd_query,
        "info": cmd_info,
        "types": cmd_types,
        "summary": cmd_summary,
    }

    fn = dispatch.get(args.cmd)
    if fn is None:
        ap.print_help()
        sys.exit(2)

    sys.exit(fn(root, args))


if __name__ == "__main__":
    main()
