"""
Authentication helpers — login, register, session guard.
"""

import streamlit as st

from utils.sheets import get_all_records, append_record
from utils.constants import TAB_USERS
from utils.helpers import generate_id, now_ist


def authenticate(username: str, password: str) -> dict | None:
    """Return the user dict if credentials match, else None."""
    df = get_all_records(TAB_USERS)
    if df.empty:
        return None
    match = df[
        (df["username"].astype(str) == username)
        & (df["password"].astype(str) == password)
    ]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def register_user(username: str, password: str,
                  display_name: str, email: str = "") -> tuple:
    """Create a new user. Returns (user_dict, message)."""
    df = get_all_records(TAB_USERS)
    if not df.empty and username in df["username"].astype(str).values:
        return None, "Username already exists!"

    user_data = {
        "user_id": generate_id(),
        "username": username,
        "password": password,
        "display_name": display_name,
        "email": email,
        "created_at": now_ist(),
        "is_deleted": "FALSE",
        "updated_at": "",
    }
    append_record(TAB_USERS, user_data)
    return user_data, "Registration successful! You can now log in."


def require_auth():
    """Call at the top of every protected page.

    Redirects to the login page if the user is not authenticated.
    """
    if "user" not in st.session_state or st.session_state.user is None:
        st.switch_page("pages/login.py")
        st.stop()


def get_current_user() -> dict | None:
    """Return the logged-in user dict, or None."""
    return st.session_state.get("user")


def logout():
    """Clear session and redirect to login."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
