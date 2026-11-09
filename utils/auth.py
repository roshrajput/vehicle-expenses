"""
Authentication helpers — login, register, session guard, and password security.
"""

import hashlib
import secrets
import time
import streamlit as st

from utils.sheets import get_all_records, append_record, update_record
from utils.constants import TAB_USERS
from utils.helpers import generate_id, now_ist

# 10 minutes inactivity timeout
INACTIVITY_TIMEOUT_SECONDS = 10 * 60


def hash_password(password: str, salt: str | None = None) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a cryptographically secure salt."""
    if not salt:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    )
    return f"pbkdf2:sha256:100000${salt}${dk.hex()}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Verify a password against stored PBKDF2 hash, or legacy plaintext.
    Maintains 100% backward compatibility for existing users without disruption.
    """
    if not stored_hash:
        return False

    stored_str = str(stored_hash).strip()
    if stored_str.startswith("pbkdf2:sha256:"):
        try:
            parts = stored_str.split("$")
            if len(parts) == 3:
                salt = parts[1]
                expected_dk = parts[2]
                computed_dk = hashlib.pbkdf2_hmac(
                    "sha256",
                    plain_password.encode("utf-8"),
                    salt.encode("utf-8"),
                    100000,
                ).hex()
                return secrets.compare_digest(computed_dk, expected_dk)
        except Exception:
            return False

    # Backward-compatible fallback for legacy plaintext passwords
    return secrets.compare_digest(plain_password, stored_str)


def authenticate(username: str, password: str) -> dict | None:
    """
    Return the user dict if credentials match, else None.
    Automatically upgrades legacy plaintext passwords to PBKDF2 hashes in Google Sheets.
    Strips raw/hashed password from the returned dictionary to secure session state.
    """
    df = get_all_records(TAB_USERS)
    if df.empty:
        return None

    clean_user = username.strip().lower()
    user_match = df[df["username"].astype(str).str.strip().str.lower() == clean_user]
    if user_match.empty:
        return None

    user_row = user_match.iloc[0]
    stored_pw = str(user_row.get("password", "")).strip()

    if not verify_password(password, stored_pw):
        return None

    # Seamless migration: if stored password is still plaintext, upgrade to secure hash now
    if not stored_pw.startswith("pbkdf2:sha256:"):
        try:
            new_hash = hash_password(password)
            user_id = str(user_row["user_id"])
            update_record(TAB_USERS, "user_id", user_id, {"password": new_hash})
        except Exception:
            pass  # Non-blocking if sheet update fails

    user_dict = user_row.to_dict()
    user_dict.pop("password", None)  # Never expose password in session state
    return user_dict


def register_user(username: str, password: str,
                  display_name: str, email: str = "") -> tuple:
    """Create a new user with hashed password. Returns (user_dict, message)."""
    df = get_all_records(TAB_USERS)
    clean_user = username.strip()
    if not df.empty and clean_user.lower() in df["username"].astype(str).str.strip().str.lower().values:
        return None, "Username already exists!"

    hashed_pw = hash_password(password)
    user_data = {
        "user_id": generate_id(),
        "username": clean_user,
        "password": hashed_pw,
        "display_name": display_name.strip(),
        "email": email.strip(),
        "created_at": now_ist(),
        "is_deleted": "FALSE",
        "updated_at": "",
    }
    append_record(TAB_USERS, user_data)
    safe_user = {k: v for k, v in user_data.items() if k != "password"}
    return safe_user, "Registration successful! You can now log in."


def check_session_timeout() -> bool:
    """Check if the user's active session has exceeded 10 minutes of inactivity.

    If inactive > 10 min, clears session, sets timeout alert, and redirects to login.
    Otherwise updates last_activity_time to the current timestamp.
    """
    if "user" not in st.session_state or st.session_state.user is None:
        return True

    now = time.time()
    last_act = st.session_state.get("last_activity_time")

    if last_act is not None and (now - last_act) > INACTIVITY_TIMEOUT_SECONDS:
        logout()
        st.session_state["session_timeout_msg"] = (
            "⚠️ You were logged out due to 10 minutes of inactivity. Please sign in again."
        )
        st.switch_page("pages/login.py")
        st.stop()
        return False

    st.session_state["last_activity_time"] = now
    return True


def require_auth():
    """Call at the top of every protected page.

    Enforces active authentication and 10-minute inactivity timeout.
    """
    if "user" not in st.session_state or st.session_state.user is None:
        st.switch_page("pages/login.py")
        st.stop()
    check_session_timeout()


def get_current_user() -> dict | None:
    """Return the logged-in user dict, or None."""
    return st.session_state.get("user")


def logout():
    """Clear session and redirect to login."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
