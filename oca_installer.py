#!/usr/bin/env python3
"""
oca_installer.py – Install all OCA Must Have modules into an Odoo addons path.

Usage
-----
::

    # Clone/update all OCA repos and link modules into /opt/odoo/addons:
    python oca_installer.py --addons-path /opt/odoo/addons

    # Only install modules from a specific category:
    python oca_installer.py --addons-path /opt/odoo/addons --category accounting

    # Dry-run (show what would be done without making changes):
    python oca_installer.py --addons-path /opt/odoo/addons --dry-run

    # Install a specific Odoo version (default: 17.0):
    python oca_installer.py --addons-path /opt/odoo/addons --odoo-version 16.0

Description
-----------
The script:

1. Creates a ``oca_repos/`` directory inside *--addons-path* (or a directory
   you specify with ``--repos-dir``).
2. Clones (or ``git pull``) each OCA repository that contains a Must Have
   module.
3. Creates a symlink from ``<addons-path>/<module_name>`` to
   ``oca_repos/<repo>/<module_name>`` for every Must Have module found.

At the end it prints a summary of every module that was linked, skipped, or
not found (e.g. because the repository does not contain a directory with that
name for the chosen Odoo version).
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Local catalogue import – works whether run as a script or as a module.
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from oca_must_have.catalogue import (  # noqa: E402
    OCA_MODULES,
    get_modules_by_category,
    get_unique_repos,
    VALID_CATEGORIES,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
_logger = logging.getLogger(__name__)

OCA_GITHUB_BASE = "https://github.com/OCA"
DEFAULT_ODOO_VERSION = "17.0"


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def clone_or_update(repo_slug: str, dest: Path, branch: str, dry_run: bool) -> bool:
    """Clone *repo_slug* into *dest* or pull if it already exists.

    :returns: ``True`` on success, ``False`` on failure.
    """
    url = f"{OCA_GITHUB_BASE}/{repo_slug}.git"
    if dest.exists():
        _logger.info("Updating %s …", dest)
        cmd = ["git", "-C", str(dest), "pull", "--ff-only"]
    else:
        _logger.info("Cloning %s → %s …", url, dest)
        cmd = ["git", "clone", "--depth", "1", "--branch", branch, url, str(dest)]

    if dry_run:
        _logger.info("[dry-run] would run: %s", " ".join(cmd))
        return True

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        _logger.error(
            "Failed to %s %s:\n%s",
            "update" if dest.exists() else "clone",
            repo_slug,
            result.stderr.strip(),
        )
        return False
    return True


def link_module(
    module_name: str,
    repo_dir: Path,
    addons_path: Path,
    dry_run: bool,
) -> str:
    """Create a symlink in *addons_path* pointing at *module_name* inside *repo_dir*.

    :returns: One of ``"linked"``, ``"exists"``, ``"not_found"``, ``"error"``.
    """
    source = repo_dir / module_name
    if not source.is_dir():
        _logger.warning("Module directory not found: %s", source)
        return "not_found"

    target = addons_path / module_name
    if target.exists() or target.is_symlink():
        _logger.debug("Symlink already exists: %s", target)
        return "exists"

    if dry_run:
        _logger.info("[dry-run] would symlink %s → %s", target, source)
        return "linked"

    try:
        target.symlink_to(source.resolve())
        _logger.info("Linked %s → %s", target, source)
        return "linked"
    except OSError as exc:
        _logger.error("Could not create symlink %s: %s", target, exc)
        return "error"


def install_modules(
    addons_path: Path,
    repos_dir: Path,
    odoo_version: str,
    category: Optional[str],
    dry_run: bool,
) -> Dict[str, List[str]]:
    """Clone repos and link modules.

    :param category: If provided, must be one of the values in
        :data:`~oca_must_have.catalogue.VALID_CATEGORIES`.
    :returns: Summary dict with keys ``linked``, ``exists``, ``not_found``,
        ``clone_failed``, ``error``.
    :raises ValueError: If *category* is not a recognised category name.
    """
    if category is not None and category not in VALID_CATEGORIES:
        raise ValueError(
            f"Unknown category {category!r}. "
            f"Valid categories: {sorted(VALID_CATEGORIES)}"
        )
    modules = (
        get_modules_by_category(category) if category else OCA_MODULES
    )

    # Group modules by repository to minimise clone operations.
    repo_to_modules: Dict[str, List[str]] = {}
    for mod in modules:
        repo_to_modules.setdefault(mod["repo"], []).append(mod["name"])

    addons_path.mkdir(parents=True, exist_ok=True)
    repos_dir.mkdir(parents=True, exist_ok=True)

    summary: Dict[str, List[str]] = {
        "linked": [],
        "exists": [],
        "not_found": [],
        "clone_failed": [],
        "error": [],
    }

    for repo_slug, module_names in sorted(repo_to_modules.items()):
        repo_dir = repos_dir / repo_slug
        ok = clone_or_update(repo_slug, repo_dir, odoo_version, dry_run)
        if not ok:
            summary["clone_failed"].extend(module_names)
            continue

        for module_name in module_names:
            status = link_module(module_name, repo_dir, addons_path, dry_run)
            summary[status].append(module_name)

    return summary


def print_summary(summary: Dict[str, List[str]]) -> None:
    """Print a human-readable installation summary."""
    print("\n" + "=" * 60)
    print("OCA Must Have Modules – Installation Summary")
    print("=" * 60)

    labels = {
        "linked": ("✅ Newly linked", True),
        "exists": ("⏭  Already present", False),
        "not_found": ("⚠️  Module directory not found", True),
        "clone_failed": ("❌ Clone/update failed (module skipped)", True),
        "error": ("❌ Symlink error", True),
    }

    for key, (label, always_show) in labels.items():
        items = summary.get(key, [])
        if items or always_show:
            print(f"\n{label} ({len(items)}):")
            for name in sorted(items):
                print(f"  • {name}")

    total = sum(len(v) for v in summary.values())
    linked = len(summary.get("linked", []))
    ok = linked + len(summary.get("exists", []))
    print(f"\nTotal modules processed : {total}")
    print(f"Successfully available  : {ok}")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--addons-path",
        required=True,
        type=Path,
        metavar="DIR",
        help="Directory where module symlinks will be created.",
    )
    parser.add_argument(
        "--repos-dir",
        type=Path,
        metavar="DIR",
        default=None,
        help=(
            "Directory where OCA repositories will be cloned. "
            "Defaults to <addons-path>/oca_repos."
        ),
    )
    parser.add_argument(
        "--odoo-version",
        default=DEFAULT_ODOO_VERSION,
        metavar="VER",
        help=f"Odoo/OCA branch to check out (default: {DEFAULT_ODOO_VERSION}).",
    )
    parser.add_argument(
        "--category",
        choices=sorted(VALID_CATEGORIES),
        default=None,
        metavar="CAT",
        help="Install only modules from this category.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making any changes.",
    )
    parser.add_argument(
        "--list-modules",
        action="store_true",
        help="Print all module names in the catalogue and exit.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.list_modules:
        modules = (
            get_modules_by_category(args.category) if args.category else OCA_MODULES
        )
        for mod in sorted(modules, key=lambda m: (m["category"], m["name"])):
            print(f"{mod['category']:12s}  {mod['name']}")
        return 0

    repos_dir = args.repos_dir or (args.addons_path / "oca_repos")

    _logger.info(
        "Installing OCA Must Have modules → addons: %s | repos: %s | version: %s%s%s",
        args.addons_path,
        repos_dir,
        args.odoo_version,
        f" | category: {args.category}" if args.category else "",
        " | DRY-RUN" if args.dry_run else "",
    )

    summary = install_modules(
        addons_path=args.addons_path,
        repos_dir=repos_dir,
        odoo_version=args.odoo_version,
        category=args.category,
        dry_run=args.dry_run,
    )

    print_summary(summary)

    # Non-zero exit if any module could not be installed.
    failures = summary.get("clone_failed", []) + summary.get("error", [])
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
