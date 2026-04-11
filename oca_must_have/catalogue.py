"""
Catalogue of all OCA "Must Have" modules.

Each entry in :data:`OCA_MODULES` is a dictionary with the following keys:

``name``
    Technical Odoo module name (used in ``__manifest__.py`` depends and
    ``-i`` / ``-u`` command-line flags).

``repo``
    OCA GitHub repository slug (the part after ``github.com/OCA/``).

``category``
    One of ``base``, ``accounting``, ``sales``, ``purchases``, ``projects``.

``description``
    Short human-readable description of what the module does.

``oca_apps_url``
    Direct link to the module on https://odoo-community.org/shop.

Source: https://odoo-community.org/page/must-have-modules
"""

from __future__ import annotations

from typing import Dict, List

# ---------------------------------------------------------------------------
# Full catalogue
# ---------------------------------------------------------------------------

OCA_MODULES: List[Dict[str, str]] = [
    # -----------------------------------------------------------------------
    # BASE
    # -----------------------------------------------------------------------
    {
        "name": "base_setup",
        "repo": "server-tools",
        "category": "base",
        "description": "Adds a step-by-step setup wizard that guides the "
                       "administrator through initial Odoo configuration.",
        "oca_apps_url": "https://odoo-community.org/shop/base-setup",
    },
    {
        "name": "base_technical_user",
        "repo": "server-tools",
        "category": "base",
        "description": "Provides a dedicated technical/system user that can be "
                       "used for scheduled actions without consuming a license seat.",
        "oca_apps_url": "https://odoo-community.org/shop/base-technical-user",
    },
    {
        "name": "base_tier_validation",
        "repo": "server-tools",
        "category": "base",
        "description": "Generic multi-level validation / approval workflow "
                       "that can be applied to any Odoo model.",
        "oca_apps_url": "https://odoo-community.org/shop/base-tier-validation",
    },
    {
        "name": "base_field_m2m_view",
        "repo": "server-tools",
        "category": "base",
        "description": "Allows many2many fields to be used in list/pivot/graph "
                       "views without extra development effort.",
        "oca_apps_url": "https://odoo-community.org/shop/base-field-m2m-view",
    },
    {
        "name": "base_import_match",
        "repo": "server-tools",
        "category": "base",
        "description": "Enables deduplication when importing CSV/Excel files "
                       "by matching records on configurable key fields.",
        "oca_apps_url": "https://odoo-community.org/shop/base-import-match",
    },
    {
        "name": "auditlog",
        "repo": "server-tools",
        "category": "base",
        "description": "Full audit-trail logging of create/write/unlink "
                       "operations on any model, stored inside Odoo.",
        "oca_apps_url": "https://odoo-community.org/shop/auditlog",
    },
    {
        "name": "database_cleanup",
        "repo": "server-tools",
        "category": "base",
        "description": "Detects and removes orphaned database columns, tables, "
                       "and properties left behind by uninstalled modules.",
        "oca_apps_url": "https://odoo-community.org/shop/database-cleanup",
    },
    {
        "name": "module_auto_update",
        "repo": "server-tools",
        "category": "base",
        "description": "Automatically upgrades installed modules when their "
                       "source checksum changes, avoiding manual -u flags.",
        "oca_apps_url": "https://odoo-community.org/shop/module-auto-update",
    },
    {
        "name": "queue_job",
        "repo": "queue",
        "category": "base",
        "description": "Asynchronous job queue for Odoo.  Moves heavy "
                       "processing out of the HTTP request cycle.",
        "oca_apps_url": "https://odoo-community.org/shop/queue-job",
    },
    {
        "name": "mail_tracking",
        "repo": "social",
        "category": "base",
        "description": "Tracks e-mail open/bounce/click events and surfaces "
                       "them directly on Odoo messages.",
        "oca_apps_url": "https://odoo-community.org/shop/mail-tracking",
    },
    {
        "name": "web_responsive",
        "repo": "web",
        "category": "base",
        "description": "Makes the Odoo backend fully responsive so it works "
                       "properly on tablets and smartphones.",
        "oca_apps_url": "https://odoo-community.org/shop/web-responsive",
    },
    {
        "name": "web_refresher",
        "repo": "web",
        "category": "base",
        "description": "Adds a manual refresh button to list views so users "
                       "can reload data without a full page reload.",
        "oca_apps_url": "https://odoo-community.org/shop/web-refresher",
    },
    {
        "name": "base_address_extended",
        "repo": "partner-contact",
        "category": "base",
        "description": "Splits the street field into street name + number to "
                       "enable accurate address parsing for many countries.",
        "oca_apps_url": "https://odoo-community.org/shop/base-address-extended",
    },
    {
        "name": "partner_firstname",
        "repo": "partner-contact",
        "category": "base",
        "description": "Stores first name and last name as separate fields "
                       "for better data quality and salutation generation.",
        "oca_apps_url": "https://odoo-community.org/shop/partner-firstname",
    },
    # -----------------------------------------------------------------------
    # ACCOUNTING
    # -----------------------------------------------------------------------
    {
        "name": "account_financial_report",
        "repo": "account-financial-reporting",
        "category": "accounting",
        "description": "Generates general ledger, trial balance, aged "
                       "receivable/payable, and other statutory financial "
                       "reports with drill-down capability.",
        "oca_apps_url": "https://odoo-community.org/shop/account-financial-report",
    },
    {
        "name": "account_tax_balance",
        "repo": "account-financial-reporting",
        "category": "accounting",
        "description": "Shows tax balance per period/account, replacing the "
                       "native tax report with a more complete view.",
        "oca_apps_url": "https://odoo-community.org/shop/account-tax-balance",
    },
    {
        "name": "mis_builder",
        "repo": "mis-builder",
        "category": "accounting",
        "description": "Management Information System report builder – "
                       "create P&L, balance sheets, and KPI dashboards with "
                       "Excel-like formula syntax.",
        "oca_apps_url": "https://odoo-community.org/shop/mis-builder",
    },
    {
        "name": "account_due_list",
        "repo": "account-financial-tools",
        "category": "accounting",
        "description": "Adds a dedicated 'Due List' view listing all overdue "
                       "and upcoming invoice/bill maturities.",
        "oca_apps_url": "https://odoo-community.org/shop/account-due-list",
    },
    {
        "name": "account_payment_term_extension",
        "repo": "account-financial-tools",
        "category": "accounting",
        "description": "Extends payment terms with day-of-month rounding and "
                       "month-end date calculation options.",
        "oca_apps_url": "https://odoo-community.org/shop/account-payment-term-extension",
    },
    {
        "name": "account_move_line_purchase_info",
        "repo": "account-financial-tools",
        "category": "accounting",
        "description": "Links journal items back to their originating purchase "
                       "order line for complete audit traceability.",
        "oca_apps_url": "https://odoo-community.org/shop/account-move-line-purchase-info",
    },
    {
        "name": "account_invoice_report_due_date",
        "repo": "account-invoice-reporting",
        "category": "accounting",
        "description": "Prints the due date on invoice PDF reports for clearer "
                       "payment instructions to customers.",
        "oca_apps_url": "https://odoo-community.org/shop/account-invoice-report-due-date",
    },
    {
        "name": "currency_rate_update",
        "repo": "currency",
        "category": "accounting",
        "description": "Automatically fetches exchange rates from ECB, "
                       "Yahoo Finance, and other public sources on a schedule.",
        "oca_apps_url": "https://odoo-community.org/shop/currency-rate-update",
    },
    # -----------------------------------------------------------------------
    # SALES
    # -----------------------------------------------------------------------
    {
        "name": "sale_order_lot_selection",
        "repo": "sale-workflow",
        "category": "sales",
        "description": "Allows selecting specific lots/serial numbers directly "
                       "on the sale order line before confirming the order.",
        "oca_apps_url": "https://odoo-community.org/shop/sale-order-lot-selection",
    },
    {
        "name": "sale_order_line_description",
        "repo": "sale-workflow",
        "category": "sales",
        "description": "Uses the product's sales description as the default "
                       "order line description instead of the product name.",
        "oca_apps_url": "https://odoo-community.org/shop/sale-order-line-description",
    },
    {
        "name": "sale_order_price_recalculation",
        "repo": "sale-workflow",
        "category": "sales",
        "description": "Adds a wizard to recalculate prices on confirmed sale "
                       "orders using the current pricelist.",
        "oca_apps_url": "https://odoo-community.org/shop/sale-order-price-recalculation",
    },
    {
        "name": "product_pricelist_direct_print",
        "repo": "sale-workflow",
        "category": "sales",
        "description": "Lets users print a pricelist PDF directly from the "
                       "pricelist form or list views.",
        "oca_apps_url": "https://odoo-community.org/shop/product-pricelist-direct-print",
    },
    {
        "name": "sale_partner_pricelist",
        "repo": "sale-workflow",
        "category": "sales",
        "description": "Automatically suggests the most appropriate pricelist "
                       "based on partner category or country.",
        "oca_apps_url": "https://odoo-community.org/shop/sale-partner-pricelist",
    },
    {
        "name": "sale_planner_calendar",
        "repo": "sale-workflow",
        "category": "sales",
        "description": "Adds a calendar/planner view that helps sales reps "
                       "schedule customer visits and link them to quotations.",
        "oca_apps_url": "https://odoo-community.org/shop/sale-planner-calendar",
    },
    {
        "name": "sale_stock_picking_note",
        "repo": "sale-workflow",
        "category": "sales",
        "description": "Propagates notes written on a sale order to the "
                       "generated stock pickings for warehouse staff.",
        "oca_apps_url": "https://odoo-community.org/shop/sale-stock-picking-note",
    },
    {
        "name": "crm_lead_lost_reason_required",
        "repo": "crm",
        "category": "sales",
        "description": "Forces users to provide a lost reason when marking a "
                       "CRM lead as lost, improving pipeline analytics.",
        "oca_apps_url": "https://odoo-community.org/shop/crm-lead-lost-reason-required",
    },
    # -----------------------------------------------------------------------
    # PURCHASES
    # -----------------------------------------------------------------------
    {
        "name": "purchase_order_type",
        "repo": "purchase-workflow",
        "category": "purchases",
        "description": "Introduces configurable purchase order types "
                       "(e.g. blanket, spot, consignment) with different "
                       "accounting and approval behaviours.",
        "oca_apps_url": "https://odoo-community.org/shop/purchase-order-type",
    },
    {
        "name": "purchase_request",
        "repo": "purchase-workflow",
        "category": "purchases",
        "description": "Adds a purchase request workflow that allows employees "
                       "to request purchases before a formal PO is created.",
        "oca_apps_url": "https://odoo-community.org/shop/purchase-request",
    },
    {
        "name": "purchase_price_security",
        "repo": "purchase-workflow",
        "category": "purchases",
        "description": "Restricts who can modify unit prices on confirmed "
                       "purchase orders based on configurable security groups.",
        "oca_apps_url": "https://odoo-community.org/shop/purchase-price-security",
    },
    {
        "name": "purchase_order_approved",
        "repo": "purchase-workflow",
        "category": "purchases",
        "description": "Adds an 'Approved' state between 'Confirmed' and "
                       "'Done' so that a manager must explicitly approve large "
                       "or out-of-policy POs.",
        "oca_apps_url": "https://odoo-community.org/shop/purchase-order-approved",
    },
    {
        "name": "purchase_stock_picking_return_invoicing",
        "repo": "purchase-workflow",
        "category": "purchases",
        "description": "Generates vendor credit notes automatically when "
                       "stock is returned to the supplier.",
        "oca_apps_url": "https://odoo-community.org/shop/purchase-stock-picking-return-invoicing",
    },
    {
        "name": "purchase_order_line_description",
        "repo": "purchase-workflow",
        "category": "purchases",
        "description": "Uses the product's purchase description as the "
                       "default order line description, matching vendor "
                       "product names for easier reconciliation.",
        "oca_apps_url": "https://odoo-community.org/shop/purchase-order-line-description",
    },
    # -----------------------------------------------------------------------
    # PROJECTS
    # -----------------------------------------------------------------------
    {
        "name": "project_timeline",
        "repo": "project",
        "category": "projects",
        "description": "Adds an interactive Gantt/timeline view to the "
                       "project task list for visual project planning.",
        "oca_apps_url": "https://odoo-community.org/shop/project-timeline",
    },
    {
        "name": "project_task_add_very_high",
        "repo": "project",
        "category": "projects",
        "description": "Adds 'Very High' and 'Very Low' priority levels to "
                       "project tasks for finer-grained triage.",
        "oca_apps_url": "https://odoo-community.org/shop/project-task-add-very-high",
    },
    {
        "name": "project_status",
        "repo": "project",
        "category": "projects",
        "description": "Adds a colour-coded status field (On Track / At Risk "
                       "/ Off Track / Done) to project records for portfolio "
                       "dashboard visibility.",
        "oca_apps_url": "https://odoo-community.org/shop/project-status",
    },
    {
        "name": "project_stage_closed",
        "repo": "project",
        "category": "projects",
        "description": "Marks certain task stages as 'closed' so that KPI "
                       "calculations and reports can distinguish done work "
                       "from work in progress.",
        "oca_apps_url": "https://odoo-community.org/shop/project-stage-closed",
    },
    {
        "name": "project_task_dependency",
        "repo": "project",
        "category": "projects",
        "description": "Allows tasks to be blocked by other tasks, surfacing "
                       "dependency chains that would otherwise be invisible.",
        "oca_apps_url": "https://odoo-community.org/shop/project-task-dependency",
    },
    {
        "name": "project_recurring_task",
        "repo": "project",
        "category": "projects",
        "description": "Creates recurring project tasks automatically "
                       "according to a configurable schedule (daily, weekly, "
                       "monthly, etc.).",
        "oca_apps_url": "https://odoo-community.org/shop/project-recurring-task",
    },
]

# ---------------------------------------------------------------------------
# Helper accessors
# ---------------------------------------------------------------------------

VALID_CATEGORIES = frozenset({"base", "accounting", "sales", "purchases", "projects"})


def get_modules_by_category(category: str) -> List[Dict[str, str]]:
    """Return all catalogue entries for *category*.

    :param category: One of ``base``, ``accounting``, ``sales``,
        ``purchases``, ``projects``.
    :raises ValueError: If *category* is not recognised.
    """
    if category not in VALID_CATEGORIES:
        raise ValueError(
            f"Unknown category {category!r}. "
            f"Valid categories: {sorted(VALID_CATEGORIES)}"
        )
    return [m for m in OCA_MODULES if m["category"] == category]


def get_all_module_names() -> List[str]:
    """Return a sorted list of every module's technical name."""
    return sorted(m["name"] for m in OCA_MODULES)


def get_unique_repos() -> List[str]:
    """Return a sorted, deduplicated list of OCA repository slugs needed."""
    return sorted({m["repo"] for m in OCA_MODULES})
