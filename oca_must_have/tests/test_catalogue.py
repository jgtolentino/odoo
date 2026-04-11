"""
Tests for the OCA Must Have module catalogue and installer.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Set

# Adjust path so tests can be run from repo root without installation.
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from oca_must_have.catalogue import (
    OCA_MODULES,
    VALID_CATEGORIES,
    get_all_module_names,
    get_modules_by_category,
    get_unique_repos,
)


class TestCatalogue(unittest.TestCase):
    """Validate the structure and consistency of the module catalogue."""

    def test_catalogue_is_non_empty(self):
        self.assertGreater(len(OCA_MODULES), 0)

    def test_all_entries_have_required_keys(self):
        required_keys = {"name", "repo", "category", "description", "oca_apps_url"}
        for mod in OCA_MODULES:
            with self.subTest(module=mod.get("name", "<no name>")):
                self.assertEqual(
                    set(mod.keys()),
                    required_keys,
                    msg=f"Module entry is missing keys or has extra keys: {mod}",
                )

    def test_all_categories_are_valid(self):
        for mod in OCA_MODULES:
            with self.subTest(module=mod["name"]):
                self.assertIn(
                    mod["category"],
                    VALID_CATEGORIES,
                    msg=f"Invalid category {mod['category']!r} in module {mod['name']!r}",
                )

    def test_module_names_are_unique(self):
        names = [m["name"] for m in OCA_MODULES]
        duplicates = {n for n in names if names.count(n) > 1}
        self.assertEqual(duplicates, set(), msg=f"Duplicate module names: {duplicates}")

    def test_module_names_are_lowercase_with_underscores(self):
        import re
        pattern = re.compile(r"^[a-z][a-z0-9_]*$")
        for mod in OCA_MODULES:
            with self.subTest(module=mod["name"]):
                self.assertRegex(
                    mod["name"],
                    pattern,
                    msg=f"Module name {mod['name']!r} does not match expected pattern",
                )

    def test_all_five_categories_are_represented(self):
        categories_in_catalogue = {m["category"] for m in OCA_MODULES}
        self.assertEqual(
            categories_in_catalogue,
            VALID_CATEGORIES,
            msg="Not all categories are represented in the catalogue",
        )

    def test_oca_apps_url_starts_with_https(self):
        for mod in OCA_MODULES:
            with self.subTest(module=mod["name"]):
                self.assertTrue(
                    mod["oca_apps_url"].startswith("https://"),
                    msg=f"oca_apps_url should start with https://: {mod['oca_apps_url']!r}",
                )

    def test_descriptions_are_non_empty(self):
        for mod in OCA_MODULES:
            with self.subTest(module=mod["name"]):
                self.assertTrue(
                    mod["description"].strip(),
                    msg=f"Empty description for module {mod['name']!r}",
                )


class TestGetModulesByCategory(unittest.TestCase):
    """Tests for :func:`get_modules_by_category`."""

    def test_returns_list(self):
        for cat in VALID_CATEGORIES:
            with self.subTest(category=cat):
                result = get_modules_by_category(cat)
                self.assertIsInstance(result, list)

    def test_returns_only_matching_category(self):
        for cat in VALID_CATEGORIES:
            with self.subTest(category=cat):
                result = get_modules_by_category(cat)
                for mod in result:
                    self.assertEqual(mod["category"], cat)

    def test_all_categories_return_at_least_one_module(self):
        for cat in VALID_CATEGORIES:
            with self.subTest(category=cat):
                result = get_modules_by_category(cat)
                self.assertGreater(
                    len(result),
                    0,
                    msg=f"Category {cat!r} has no modules in the catalogue",
                )

    def test_invalid_category_raises(self):
        with self.assertRaises(ValueError):
            get_modules_by_category("nonexistent_category")

    def test_union_of_all_categories_equals_full_catalogue(self):
        all_from_categories: Set[str] = set()
        for cat in VALID_CATEGORIES:
            for mod in get_modules_by_category(cat):
                all_from_categories.add(mod["name"])
        all_names = set(get_all_module_names())
        self.assertEqual(all_from_categories, all_names)


class TestGetAllModuleNames(unittest.TestCase):
    """Tests for :func:`get_all_module_names`."""

    def test_returns_sorted_list(self):
        names = get_all_module_names()
        self.assertEqual(names, sorted(names))

    def test_length_matches_catalogue(self):
        self.assertEqual(len(get_all_module_names()), len(OCA_MODULES))

    def test_known_modules_are_present(self):
        names = set(get_all_module_names())
        expected = {
            # Base
            "auditlog",
            "base_tier_validation",
            "queue_job",
            "web_responsive",
            "mail_tracking",
            # Accounting
            "account_financial_report",
            "mis_builder",
            "currency_rate_update",
            # Sales
            "sale_order_lot_selection",
            "product_pricelist_direct_print",
            # Purchases
            "purchase_request",
            "purchase_order_type",
            # Projects
            "project_timeline",
            "project_status",
        }
        missing = expected - names
        self.assertEqual(
            missing,
            set(),
            msg=f"Expected modules missing from catalogue: {missing}",
        )


class TestGetUniqueRepos(unittest.TestCase):
    """Tests for :func:`get_unique_repos`."""

    def test_returns_sorted_list(self):
        repos = get_unique_repos()
        self.assertEqual(repos, sorted(repos))

    def test_no_duplicates(self):
        repos = get_unique_repos()
        self.assertEqual(len(repos), len(set(repos)))

    def test_known_repos_present(self):
        repos = set(get_unique_repos())
        expected = {
            "server-tools",
            "queue",
            "social",
            "web",
            "partner-contact",
            "account-financial-reporting",
            "mis-builder",
            "account-financial-tools",
            "account-invoice-reporting",
            "currency",
            "sale-workflow",
            "crm",
            "purchase-workflow",
            "project",
        }
        missing = expected - repos
        self.assertEqual(missing, set(), msg=f"Expected repos missing: {missing}")


class TestManifest(unittest.TestCase):
    """Validate that __manifest__.py depends list matches the catalogue."""

    def _load_manifest_depends(self) -> Set[str]:
        """Parse ``__manifest__.py`` and return the set of dependencies."""
        manifest_path = (
            Path(__file__).resolve().parents[1] / "__manifest__.py"
        )
        with open(manifest_path) as fh:
            content = fh.read()
        manifest = eval(content, {"__builtins__": {}})  # noqa: S307
        return set(manifest.get("depends", []))

    def test_manifest_depends_contains_all_catalogue_modules(self):
        manifest_depends = self._load_manifest_depends()
        catalogue_names = set(get_all_module_names())
        missing = catalogue_names - manifest_depends
        self.assertEqual(
            missing,
            set(),
            msg=(
                f"These catalogue modules are missing from __manifest__.py depends: "
                f"{sorted(missing)}"
            ),
        )

    def test_manifest_depends_has_no_extra_oca_modules(self):
        """Every OCA module in depends should appear in the catalogue."""
        manifest_depends = self._load_manifest_depends()
        catalogue_names = set(get_all_module_names())
        # Odoo built-ins are not in our catalogue – ignore them.
        odoo_builtins = {"base", "mail", "sale", "purchase", "account", "project"}
        extra = (manifest_depends - odoo_builtins) - catalogue_names
        self.assertEqual(
            extra,
            set(),
            msg=(
                f"These modules are in __manifest__.py depends but not in the "
                f"catalogue: {sorted(extra)}"
            ),
        )


if __name__ == "__main__":
    unittest.main()
