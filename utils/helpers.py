"""
Utility / helper functions.
"""

import uuid
from datetime import datetime, date

from utils.constants import CURRENCY, DATE_FORMAT, DATETIME_FORMAT


# ---------------------------------------------------------------------------
# ID generation
# ---------------------------------------------------------------------------
def generate_id() -> str:
    """Return a short unique ID (8 hex chars)."""
    return uuid.uuid4().hex[:8]


# ---------------------------------------------------------------------------
# Date / time
# ---------------------------------------------------------------------------
def now_ist() -> str:
    """Current timestamp as a string (server local time)."""
    return datetime.now().strftime(DATETIME_FORMAT)


def today_date() -> date:
    """Today as a date object."""
    return date.today()


def parse_date(date_str: str):
    """Parse a YYYY-MM-DD string into a date, or return None."""
    try:
        return datetime.strptime(str(date_str), DATE_FORMAT).date()
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Currency formatting
# ---------------------------------------------------------------------------
def fmt_currency(amount) -> str:
    """Format a number as ₹X,XXX.XX."""
    try:
        return f"{CURRENCY}{float(amount):,.2f}"
    except (ValueError, TypeError):
        return f"{CURRENCY}0.00"


def fmt_number(value, decimals: int = 1) -> str:
    """Format a number with commas and given decimal places."""
    try:
        return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        return "0"
