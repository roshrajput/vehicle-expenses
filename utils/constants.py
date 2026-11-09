"""
Constants and configuration for the Vehicle Expense Tracker.
"""

# ---------------------------------------------------------------------------
# Application Metadata
# ---------------------------------------------------------------------------
APP_NAME = "AutoExpense OS"
APP_VERSION = "v1.3.0"
APP_RELEASE_DATE = "November 2026"


def _resolve_git_hash() -> str:
    """Dynamically determine git short hash for internal debugging."""
    try:
        import subprocess
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except Exception:
        return ""


GIT_COMMIT_HASH = _resolve_git_hash()

# ---------------------------------------------------------------------------
# Google Sheet
# ---------------------------------------------------------------------------
SHEET_ID = "1wR0BmHktXMGs1q9_39k7gg86BCdfuPbxuLMSwC6H85A"

# Tab (worksheet) names
TAB_USERS = "Users"
TAB_VEHICLES = "Vehicles"
TAB_FUEL = "Fuel_Expenses"
TAB_SERVICE = "Service_Expenses"
TAB_MISC = "Misc_Expenses"

# ---------------------------------------------------------------------------
# Column headers for each tab
# ---------------------------------------------------------------------------
USERS_COLUMNS = [
    "user_id", "username", "password", "display_name", "email",
    "created_at", "is_deleted", "updated_at",
]

VEHICLES_COLUMNS = [
    "vehicle_id", "user_id", "vehicle_name", "vehicle_type", "make",
    "model", "year", "registration_no", "fuel_type",
    "insurance_expiry", "pucc_expiry",
    "created_at", "is_deleted", "updated_at",
]

FUEL_COLUMNS = [
    "expense_id", "vehicle_id", "user_id", "date", "odo_reading_km",
    "trip_km", "fuel_quantity_liters", "fuel_rate_per_liter",
    "total_fuel_cost", "is_full_tank", "is_first_fill", "fuel_type", "comments",
    "created_at", "is_deleted", "updated_at",
]

SERVICE_COLUMNS = [
    "expense_id", "vehicle_id", "user_id", "date", "odo_reading_km",
    "service_type", "total_service_cost", "parts_details", "comments",
    "created_at", "is_deleted", "updated_at",
]

MISC_COLUMNS = [
    "expense_id", "vehicle_id", "user_id", "date", "amount",
    "category", "comments",
    "created_at", "is_deleted", "updated_at",
]

# Mapping tab name -> column list
TAB_COLUMNS = {
    TAB_USERS: USERS_COLUMNS,
    TAB_VEHICLES: VEHICLES_COLUMNS,
    TAB_FUEL: FUEL_COLUMNS,
    TAB_SERVICE: SERVICE_COLUMNS,
    TAB_MISC: MISC_COLUMNS,
}

# ---------------------------------------------------------------------------
# Dropdown options
# ---------------------------------------------------------------------------
VEHICLE_TYPES = ["Car", "Bike", "Truck", "Bus", "Auto", "Other"]
FUEL_TYPES = ["Petrol", "Diesel", "CNG", "Electric", "Hybrid"]
SERVICE_TYPES = [
    "Regular Service", "Repair", "Tyre Change", "Battery",
    "Insurance", "Body Work", "Electrical", "Other",
]
MISC_CATEGORIES = [
    "Toll", "Parking", "Car Wash", "Accessories",
    "Fine / Challan", "FASTag Recharge", "Other",
]

# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------
CURRENCY = "₹"
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
