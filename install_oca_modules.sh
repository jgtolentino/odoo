#!/usr/bin/env bash
# =============================================================================
# install_oca_modules.sh
#
# Installs all OCA "Must Have" modules into an Odoo addons directory by
# cloning the required OCA GitHub repositories and creating symlinks.
#
# Usage:
#   ./install_oca_modules.sh [OPTIONS]
#
# Options:
#   -p, --addons-path  DIR     Target addons directory (required)
#   -r, --repos-dir   DIR     Where to clone OCA repos (default: <addons-path>/oca_repos)
#   -v, --odoo-version VER    Odoo/OCA branch (default: 17.0)
#   -c, --category    CAT     Only install one category: base|accounting|sales|purchases|projects
#   -n, --dry-run             Show what would be done without making changes
#   -h, --help                Show this help and exit
#
# Examples:
#   # Install all OCA Must Have modules for Odoo 17.0
#   ./install_oca_modules.sh -p /opt/odoo/extra-addons
#
#   # Install only accounting modules for Odoo 16.0
#   ./install_oca_modules.sh -p /opt/odoo/extra-addons -v 16.0 -c accounting
#
#   # Dry-run
#   ./install_oca_modules.sh -p /opt/odoo/extra-addons -n
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
ADDONS_PATH=""
REPOS_DIR=""
ODOO_VERSION="17.0"
CATEGORY=""
DRY_RUN=false
OCA_GITHUB="https://github.com/OCA"

# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Colour

info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ---------------------------------------------------------------------------
# OCA Must Have module catalogue
# Format: "module_name:repo_slug:category"
# ---------------------------------------------------------------------------
OCA_MUST_HAVE_MODULES=(
    # Base
    "base_setup:server-tools:base"
    "base_technical_user:server-tools:base"
    "base_tier_validation:server-tools:base"
    "base_field_m2m_view:server-tools:base"
    "base_import_match:server-tools:base"
    "auditlog:server-tools:base"
    "database_cleanup:server-tools:base"
    "module_auto_update:server-tools:base"
    "queue_job:queue:base"
    "mail_tracking:social:base"
    "web_responsive:web:base"
    "web_refresher:web:base"
    "base_address_extended:partner-contact:base"
    "partner_firstname:partner-contact:base"
    # Accounting
    "account_financial_report:account-financial-reporting:accounting"
    "account_tax_balance:account-financial-reporting:accounting"
    "mis_builder:mis-builder:accounting"
    "account_due_list:account-financial-tools:accounting"
    "account_payment_term_extension:account-financial-tools:accounting"
    "account_move_line_purchase_info:account-financial-tools:accounting"
    "account_invoice_report_due_date:account-invoice-reporting:accounting"
    "currency_rate_update:currency:accounting"
    # Sales
    "sale_order_lot_selection:sale-workflow:sales"
    "sale_order_line_description:sale-workflow:sales"
    "sale_order_price_recalculation:sale-workflow:sales"
    "product_pricelist_direct_print:sale-workflow:sales"
    "sale_partner_pricelist:sale-workflow:sales"
    "sale_planner_calendar:sale-workflow:sales"
    "sale_stock_picking_note:sale-workflow:sales"
    "crm_lead_lost_reason_required:crm:sales"
    # Purchases
    "purchase_order_type:purchase-workflow:purchases"
    "purchase_request:purchase-workflow:purchases"
    "purchase_price_security:purchase-workflow:purchases"
    "purchase_order_approved:purchase-workflow:purchases"
    "purchase_stock_picking_return_invoicing:purchase-workflow:purchases"
    "purchase_order_line_description:purchase-workflow:purchases"
    # Projects
    "project_timeline:project:projects"
    "project_task_add_very_high:project:projects"
    "project_status:project:projects"
    "project_stage_closed:project:projects"
    "project_task_dependency:project:projects"
    "project_recurring_task:project:projects"
)

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
usage() {
    sed -n '/^# Usage/,/^# ====/p' "$0" | head -n -1 | sed 's/^# \?//'
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--addons-path)  ADDONS_PATH="$2"; shift 2 ;;
        -r|--repos-dir)    REPOS_DIR="$2";   shift 2 ;;
        -v|--odoo-version) ODOO_VERSION="$2"; shift 2 ;;
        -c|--category)     CATEGORY="$2";    shift 2 ;;
        -n|--dry-run)      DRY_RUN=true;     shift   ;;
        -h|--help)         usage ;;
        *) error "Unknown option: $1"; usage ;;
    esac
done

if [[ -z "$ADDONS_PATH" ]]; then
    error "--addons-path is required."
    usage
fi

REPOS_DIR="${REPOS_DIR:-${ADDONS_PATH}/oca_repos}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
clone_or_update() {
    local repo_slug="$1"
    local dest="$2"
    local url="${OCA_GITHUB}/${repo_slug}.git"

    if [[ -d "$dest/.git" ]]; then
        info "Updating ${repo_slug} …"
        if [[ "$DRY_RUN" == "true" ]]; then
            info "[dry-run] git -C '${dest}' pull --ff-only"
            return 0
        fi
        git -C "$dest" pull --ff-only 2>&1 | tail -1 || {
            warn "git pull failed for ${repo_slug}; continuing with existing clone."
        }
    else
        info "Cloning ${url} → ${dest} …"
        if [[ "$DRY_RUN" == "true" ]]; then
            info "[dry-run] git clone --depth 1 --branch '${ODOO_VERSION}' '${url}' '${dest}'"
            return 0
        fi
        if ! git clone --depth 1 --branch "${ODOO_VERSION}" "$url" "$dest" 2>&1; then
            warn "Failed to clone ${repo_slug} (branch ${ODOO_VERSION}). Skipping."
            return 1
        fi
    fi
}

link_module() {
    local module="$1"
    local repo_dir="$2"
    local source="${repo_dir}/${module}"
    local target="${ADDONS_PATH}/${module}"

    if [[ ! -d "$source" ]]; then
        warn "Module directory not found: ${source}"
        SKIPPED+=("$module")
        return
    fi

    if [[ -e "$target" || -L "$target" ]]; then
        info "Already linked: ${module}"
        ALREADY_PRESENT+=("$module")
        return
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        info "[dry-run] ln -s '${source}' '${target}'"
        LINKED+=("$module")
        return
    fi

    ln -s "$(realpath "$source")" "$target"
    success "Linked: ${module}"
    LINKED+=("$module")
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
LINKED=()
ALREADY_PRESENT=()
SKIPPED=()
FAILED=()
CLONED_REPOS=()

[[ "$DRY_RUN" == "true" ]] && info "=== DRY-RUN MODE – no changes will be made ==="

mkdir -p "$ADDONS_PATH" "$REPOS_DIR"

# Group entries by repo to avoid redundant clones.
declare -A REPO_MODULE_MAP
for entry in "${OCA_MUST_HAVE_MODULES[@]}"; do
    IFS=':' read -r mod repo cat <<<"$entry"
    if [[ -n "$CATEGORY" && "$cat" != "$CATEGORY" ]]; then
        continue
    fi
    REPO_MODULE_MAP["$repo"]+=" $mod"
done

for repo in "${!REPO_MODULE_MAP[@]}"; do
    dest="${REPOS_DIR}/${repo}"
    if clone_or_update "$repo" "$dest"; then
        CLONED_REPOS+=("$repo")
        for mod in ${REPO_MODULE_MAP["$repo"]}; do
            link_module "$mod" "$dest"
        done
    else
        for mod in ${REPO_MODULE_MAP["$repo"]}; do
            FAILED+=("$mod")
        done
    fi
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "============================================================"
echo " OCA Must Have Modules – Installation Summary"
echo "============================================================"
echo ""
echo "  ✅ Newly linked     : ${#LINKED[@]}"
for m in "${LINKED[@]}"; do echo "      • $m"; done

echo "  ⏭  Already present  : ${#ALREADY_PRESENT[@]}"
for m in "${ALREADY_PRESENT[@]}"; do echo "      • $m"; done

if [[ ${#SKIPPED[@]} -gt 0 ]]; then
    echo "  ⚠️  Not found in repo : ${#SKIPPED[@]}"
    for m in "${SKIPPED[@]}"; do echo "      • $m"; done
fi

if [[ ${#FAILED[@]} -gt 0 ]]; then
    echo "  ❌ Clone failed      : ${#FAILED[@]}"
    for m in "${FAILED[@]}"; do echo "      • $m"; done
fi

TOTAL=$(( ${#LINKED[@]} + ${#ALREADY_PRESENT[@]} + ${#SKIPPED[@]} + ${#FAILED[@]} ))
OK=$(( ${#LINKED[@]} + ${#ALREADY_PRESENT[@]} ))
echo ""
echo "  Total processed     : ${TOTAL}"
echo "  Successfully linked : ${OK}"
echo "============================================================"
echo ""

if [[ ${#FAILED[@]} -gt 0 ]]; then
    error "Some modules could not be installed.  Check the output above."
    exit 1
fi
exit 0
