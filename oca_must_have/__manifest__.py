# -*- coding: utf-8 -*-
{
    "name": "OCA Must Have Modules",
    "summary": (
        "Meta-module that installs all OCA 'Must Have' modules for Base, "
        "Accounting, Sales, Purchases, and Projects."
    ),
    "version": "17.0.1.0.0",
    "category": "Technical",
    "author": "Odoo Community Association (OCA)",
    "website": "https://odoo-community.org/page/must-have-modules",
    "license": "LGPL-3",
    "depends": [
        # ----------------------------------------------------------------
        # Base
        # ----------------------------------------------------------------
        "base_setup",
        "base_technical_user",
        "base_tier_validation",
        "base_field_m2m_view",
        "base_import_match",
        "auditlog",
        "database_cleanup",
        "module_auto_update",
        "queue_job",
        "mail_tracking",
        "web_responsive",
        "web_refresher",
        "base_address_extended",
        "partner_firstname",
        # ----------------------------------------------------------------
        # Accounting
        # ----------------------------------------------------------------
        "account_financial_report",
        "account_tax_balance",
        "mis_builder",
        "account_due_list",
        "account_payment_term_extension",
        "account_move_line_purchase_info",
        "account_invoice_report_due_date",
        "currency_rate_update",
        # ----------------------------------------------------------------
        # Sales
        # ----------------------------------------------------------------
        "sale_order_lot_selection",
        "sale_order_line_description",
        "sale_order_price_recalculation",
        "product_pricelist_direct_print",
        "sale_partner_pricelist",
        "sale_planner_calendar",
        "sale_stock_picking_note",
        "crm_lead_lost_reason_required",
        # ----------------------------------------------------------------
        # Purchases
        # ----------------------------------------------------------------
        "purchase_order_type",
        "purchase_request",
        "purchase_price_security",
        "purchase_order_approved",
        "purchase_stock_picking_return_invoicing",
        "purchase_order_line_description",
        # ----------------------------------------------------------------
        # Projects
        # ----------------------------------------------------------------
        "project_timeline",
        "project_task_add_very_high",
        "project_status",
        "project_stage_closed",
        "project_task_dependency",
        "project_recurring_task",
    ],
    "data": [],
    "installable": True,
    "auto_install": False,
    "application": False,
}
