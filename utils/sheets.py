"""
Google Sheets CRUD operations via gspread.

All reads filter out soft-deleted rows (is_deleted == TRUE) by default.
Uses @st.cache_data for fast navigation and clears cache on write/update.
"""

import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd

from utils.constants import (
    SHEET_ID, TAB_COLUMNS,
    TAB_USERS, TAB_VEHICLES, TAB_FUEL, TAB_SERVICE, TAB_MISC,
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# ---------------------------------------------------------------------------
# Connection & Configuration Check
# ---------------------------------------------------------------------------
def check_connection() -> tuple[bool, str]:
    """Test if Google Sheets connection is valid and reachable."""
    try:
        if "gcp_service_account" not in st.secrets:
            return False, "Missing `[gcp_service_account]` section in `.streamlit/secrets.toml`."
        
        client = _get_client()
        spreadsheet = client.open_by_key(SHEET_ID)
        return True, f"Connected to '{spreadsheet.title}' successfully!"
    except Exception as e:
        return False, str(e)


@st.cache_resource(show_spinner=False)
def _get_client():
    """Authorize and return a gspread client (cached across reruns)."""
    creds_dict = dict(st.secrets["gcp_service_account"])
    # Handle private key formatting (escaped newlines)
    if "private_key" in creds_dict and "\\n" in creds_dict["private_key"]:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


def _get_spreadsheet():
    return _get_client().open_by_key(SHEET_ID)


def _get_worksheet(tab_name: str):
    return _get_spreadsheet().worksheet(tab_name)


# ---------------------------------------------------------------------------
# Cache Management
# ---------------------------------------------------------------------------
def clear_sheet_cache():
    """Clear cached sheet data after any write/update/delete operation."""
    get_all_records.clear()


# ---------------------------------------------------------------------------
# Initialization — create tabs & headers if missing
# ---------------------------------------------------------------------------
def initialize_sheets():
    """Ensure every tab exists with the correct header row."""
    spreadsheet = _get_spreadsheet()
    existing_tabs = [ws.title for ws in spreadsheet.worksheets()]

    for tab_name, columns in TAB_COLUMNS.items():
        if tab_name not in existing_tabs:
            ws = spreadsheet.add_worksheet(
                title=tab_name, rows=1000, cols=len(columns),
            )
            ws.update([columns], "A1")
        else:
            ws = spreadsheet.worksheet(tab_name)
            headers = ws.row_values(1)
            if not headers:
                ws.update([columns], "A1")


# ---------------------------------------------------------------------------
# READ helpers
# ---------------------------------------------------------------------------
@st.cache_data(ttl=60, show_spinner=False)
def get_all_records(tab_name: str, include_deleted: bool = False) -> pd.DataFrame:
    """Return every row of *tab_name* as a DataFrame.

    Soft-deleted rows are excluded unless *include_deleted* is True.
    """
    ws = _get_worksheet(tab_name)
    data = ws.get_all_records()

    expected_cols = TAB_COLUMNS.get(tab_name, [])
    if not data:
        return pd.DataFrame(columns=expected_cols)

    df = pd.DataFrame(data)
    # Ensure all expected columns exist
    for col in expected_cols:
        if col not in df.columns:
            df[col] = ""

    if not include_deleted and "is_deleted" in df.columns:
        # Treat "TRUE", "True", True, 1 as deleted
        mask = df["is_deleted"].astype(str).str.strip().str.upper() == "TRUE"
        df = df[~mask]

    return df.reset_index(drop=True)


def get_records_by_user(tab_name: str, user_id: str,
                        include_deleted: bool = False) -> pd.DataFrame:
    """Rows where user_id matches, as DataFrame."""
    df = get_all_records(tab_name, include_deleted)
    if df.empty or "user_id" not in df.columns:
        return pd.DataFrame(columns=TAB_COLUMNS.get(tab_name, []))
    return df[df["user_id"].astype(str) == str(user_id)].reset_index(drop=True)


def get_records_by_vehicle(tab_name: str, vehicle_id: str,
                           include_deleted: bool = False) -> pd.DataFrame:
    """Rows where vehicle_id matches, as DataFrame."""
    df = get_all_records(tab_name, include_deleted)
    if df.empty or "vehicle_id" not in df.columns:
        return pd.DataFrame(columns=TAB_COLUMNS.get(tab_name, []))
    return df[df["vehicle_id"].astype(str) == str(vehicle_id)].reset_index(drop=True)


def get_records_by_user_list(tab_name: str, user_id: str,
                             include_deleted: bool = False) -> list[dict]:
    """Rows where user_id matches, as a list of dicts."""
    df = get_records_by_user(tab_name, user_id, include_deleted)
    if df.empty:
        return []
    return df.to_dict(orient="records")


def get_records_by_vehicle_list(tab_name: str, vehicle_id: str,
                                include_deleted: bool = False) -> list[dict]:
    """Rows where vehicle_id matches, as a list of dicts."""
    df = get_records_by_vehicle(tab_name, vehicle_id, include_deleted)
    if df.empty:
        return []
    return df.to_dict(orient="records")


# ---------------------------------------------------------------------------
# WRITE helpers
# ---------------------------------------------------------------------------
def append_record(tab_name: str, data_dict: dict):
    """Append a single row to *tab_name*."""
    ws = _get_worksheet(tab_name)
    headers = ws.row_values(1)
    if not headers:
        headers = TAB_COLUMNS.get(tab_name, [])
        ws.update([headers], "A1")
    row = [str(data_dict.get(h, "")) for h in headers]
    ws.append_row(row, value_input_option="USER_ENTERED")
    clear_sheet_cache()


# ---------------------------------------------------------------------------
# UPDATE helpers
# ---------------------------------------------------------------------------
def _find_row_index(ws, id_column: str, record_id: str):
    """Return the 1-based row number of the record, or None."""
    data = ws.get_all_values()
    if not data:
        return None
    headers = data[0]
    try:
        col_idx = headers.index(id_column)
    except ValueError:
        return None
    for i, row in enumerate(data[1:], start=2):
        if len(row) > col_idx and str(row[col_idx]).strip() == str(record_id).strip():
            return i
    return None


def update_record(tab_name: str, id_column: str, record_id: str,
                  updates: dict) -> bool:
    """Update specific columns of the row identified by *id_column* == *record_id*."""
    ws = _get_worksheet(tab_name)
    row_idx = _find_row_index(ws, id_column, record_id)
    if row_idx is None:
        return False

    headers = ws.row_values(1)
    cells = []
    for key, value in updates.items():
        if key in headers:
            col_idx = headers.index(key) + 1
            cells.append(gspread.Cell(row_idx, col_idx, str(value)))

    if cells:
        ws.update_cells(cells, value_input_option="USER_ENTERED")
        clear_sheet_cache()
    return True


def soft_delete_record(tab_name: str, id_column: str,
                       record_id: str) -> bool:
    """Mark a record as deleted (soft delete — row stays in the sheet)."""
    from utils.helpers import now_ist
    return update_record(tab_name, id_column, record_id, {
        "is_deleted": "TRUE",
        "updated_at": now_ist(),
    })
