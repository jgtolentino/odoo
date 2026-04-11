"""
OCA Must Have Modules – central catalogue and installer entry-point.

The Odoo Community Association (OCA) maintains curated lists of "Must Have"
modules for every major functional area.  This package provides:

* A machine-readable catalogue of every OCA Must Have module grouped by
  category (Base, Accounting, Sales, Purchases, Projects).
* A Python installer (``oca_installer.py``) that clones/updates the required
  OCA repositories and links them into your Odoo addons path.
* A companion shell script (``install_oca_modules.sh``) for CI/CD pipelines.
* An Odoo "meta" addon (``oca_must_have``) whose ``__manifest__.py``
  declares all modules as dependencies so that a single ``-i oca_must_have``
  command installs everything.

Source: https://odoo-community.org/page/must-have-modules
"""

from .catalogue import OCA_MODULES, get_modules_by_category, get_all_module_names

__all__ = [
    "OCA_MODULES",
    "get_modules_by_category",
    "get_all_module_names",
]
