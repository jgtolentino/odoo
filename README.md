# Odoo – OCA Must Have Modules & Performance Utilities

[![OCA](https://img.shields.io/badge/OCA-Must%20Have%20Modules-brightgreen)](https://odoo-community.org/page/must-have-modules)
[![License: LGPL-3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

A repository that:

1. **Installs all OCA "Must Have" modules** across five functional categories
   (Base, Accounting, Sales, Purchases, Projects).
2. **Bundles Odoo performance-optimization utilities** (batch ORM processing,
   LRU/TTL caching, query analysis).

---

## OCA Must Have Modules

The [Odoo Community Association (OCA)](https://odoo-community.org) maintains
curated lists of modules that every serious Odoo installation should include.
This repository automates their installation.

### Covered categories

| Category    | # Modules | Key modules |
|-------------|-----------|-------------|
| **Base**    | 14 | `auditlog`, `base_tier_validation`, `queue_job`, `web_responsive`, `mail_tracking` |
| **Accounting** | 8 | `account_financial_report`, `mis_builder`, `currency_rate_update` |
| **Sales**   | 8 | `sale_order_lot_selection`, `product_pricelist_direct_print` |
| **Purchases** | 6 | `purchase_request`, `purchase_order_type`, `purchase_order_approved` |
| **Projects** | 6 | `project_timeline`, `project_status`, `project_task_dependency` |

Full module list → [oca_must_have/catalogue.py](oca_must_have/catalogue.py)

---

## Quick Start

### Option A – Python installer (recommended)

```bash
# Install all OCA Must Have modules for Odoo 17.0
python oca_installer.py --addons-path /opt/odoo/extra-addons

# Install only accounting modules for Odoo 16.0
python oca_installer.py \
    --addons-path /opt/odoo/extra-addons \
    --odoo-version 16.0 \
    --category accounting

# Preview what would be done (no changes)
python oca_installer.py --addons-path /opt/odoo/extra-addons --dry-run

# List all modules in the catalogue
python oca_installer.py --addons-path /opt/odoo/extra-addons --list-modules
```

### Option B – Shell script

```bash
chmod +x install_oca_modules.sh

# Install all modules
./install_oca_modules.sh -p /opt/odoo/extra-addons

# Install only sales modules for Odoo 16.0
./install_oca_modules.sh -p /opt/odoo/extra-addons -v 16.0 -c sales

# Dry-run
./install_oca_modules.sh -p /opt/odoo/extra-addons -n
```

### Option C – Odoo meta-module

Copy or symlink the `oca_must_have/` directory into your Odoo addons path,
then install the `oca_must_have` module:

```bash
# Link the meta-module
ln -s "$(pwd)/oca_must_have" /opt/odoo/extra-addons/oca_must_have

# Install via Odoo CLI (installs all dependencies automatically)
./odoo-bin -d mydb -i oca_must_have --stop-after-init
```

### Option D – pip / git install

```bash
pip install -r requirements_oca.txt
```

---

## OCA Dependencies (MQT)

The [`oca_dependencies.txt`](oca_dependencies.txt) file lists all required
OCA repositories in the format expected by
[Maintainer Quality Tools (MQT)](https://github.com/OCA/maintainer-quality-tools)
for CI/CD pipelines.

---

## Performance Utilities

The [`odoo_performance/`](odoo_performance/) package provides helpers for
tuning Odoo at scale:

### ORM (`odoo_performance.orm`)

| Helper | Purpose |
|--------|---------|
| `BatchProcessor` | Iterate large record-sets in fixed-size chunks, avoiding ORM prefetch overflow |
| `prefetch_fields(records, fields)` | Eager-load specific fields in one SQL query |
| `QueryOptimizer` | Track repeated/slow queries and emit warnings |
| `suggest_field_subset(model, fields)` | Return a minimal field list for `read()` calls |
| `build_optimised_domain(base, extras)` | Safely merge Odoo domain lists |

### Cache (`odoo_performance.cache`)

| Helper | Purpose |
|--------|---------|
| `LRUCache` | Thread-safe LRU cache with optional TTL |
| `lru_cache_method(maxsize, ttl)` | Decorator for Odoo model methods |
| `memoize(maxsize, ttl)` | Decorator for pure functions |
| `CacheInvalidator` | Registry for coordinated cache invalidation by tag |
| `auto_invalidate(invalidator, tags)` | Decorator to auto-clear caches on ORM write/create/unlink |

### Quick example

```python
from odoo_performance.orm.batch import BatchProcessor, prefetch_fields
from odoo_performance.cache.lru import lru_cache_method

# Stream 50 000 sale orders without memory blow-up
processor = BatchProcessor(self.env["sale.order"], batch_size=500)
for order in processor.iter_records(domain=[("state", "=", "sale")]):
    _process(order)

# Cache a costly computation for 5 minutes
class ResPartner(models.Model):
    _name = "res.partner"

    @lru_cache_method(maxsize=256, ttl=300)
    def get_credit_score(self):
        return _expensive_call(self)
```

---

## Running Tests

```bash
# Catalogue + manifest tests (no Odoo installation needed)
python -m unittest oca_must_have/tests/test_catalogue.py -v
```

---

## Repository Layout

```
.
├── oca_must_have/              # OCA Must Have meta-module + catalogue
│   ├── __init__.py
│   ├── __manifest__.py         # Odoo addon manifest (depends on all OCA modules)
│   ├── catalogue.py            # Machine-readable module catalogue
│   └── tests/
│       └── test_catalogue.py
├── odoo_performance/           # Performance optimization utilities
│   ├── orm/
│   │   ├── batch.py
│   │   └── query_optimizer.py
│   └── cache/
│       ├── lru.py
│       └── invalidation.py
├── oca_installer.py            # Python CLI installer
├── install_oca_modules.sh      # Bash installer for CI/CD
├── oca_dependencies.txt        # OCA MQT dependency file
└── requirements_oca.txt        # pip/git install requirements
```

---

## License

LGPL-3 – see [https://www.gnu.org/licenses/lgpl-3.0](https://www.gnu.org/licenses/lgpl-3.0)

## About OCA

The [Odoo Community Association](https://odoo-community.org) is a non-profit
organization based in Switzerland that supports collaborative development of
Odoo features and provides thousands of open-source Odoo modules.
