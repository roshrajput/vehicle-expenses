"""
Vehicle Expense Tracker — Main Entry Point
Uses st.navigation / st.Page for multi-page routing.
Includes connection check and first-time setup assistant.
"""

import json
import streamlit as st
from utils.sheets import check_connection, initialize_sheets
from utils.constants import SHEET_ID, APP_NAME, APP_VERSION, APP_RELEASE_DATE, GIT_COMMIT_HASH
from utils.ui import apply_custom_css

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AutoExpense OS",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Apply SaaS Theme ────────────────────────────────────────────────────────
apply_custom_css()

# ── Check Google Sheets connection ──────────────────────────────────────────
is_connected, message = check_connection()

if not is_connected:
    st.markdown(
        f"""
        <div style="text-align: center; margin: 30px 0 24px 0;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; background: linear-gradient(135deg, #2563EB, #1D4ED8); border-radius: 18px; box-shadow: 0 10px 20px -5px rgba(37,99,235,0.4); margin-bottom: 16px;">
                <span style="font-size: 2rem;">⚡</span>
            </div>
            <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; color: #0F172A; letter-spacing: -0.03em;">Welcome to AutoExpense OS</h1>
            <p style="margin: 6px auto 0 auto; max-width: 500px; font-size: 1rem; color: #64748B;">
                Quickly connect your Google Spreadsheet to activate real-time expense tracking.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        with st.container(border=True):
            st.markdown("### 🔑 Step 1: Upload Service Account Key")
            st.markdown(
                """
                Upload your downloaded Google Cloud service account `.json` key.
                It will be saved securely into `.streamlit/secrets.toml` and kept git-ignored.
                """
            )
            st.write("")

            uploaded_json = st.file_uploader(
                "Upload Google Service Account JSON file:",
                type=["json"],
                help="Downloaded from Google Cloud Console > IAM & Admin > Service Accounts > Keys",
            )

            if uploaded_json is not None:
                try:
                    key_dict = json.load(uploaded_json)
                    if "client_email" in key_dict and "private_key" in key_dict:
                        toml_content = '[gcp_service_account]\n'
                        for k, v in key_dict.items():
                            v_str = json.dumps(v)
                            toml_content += f'{k} = {v_str}\n'

                        import os
                        os.makedirs(".streamlit", exist_ok=True)
                        with open(".streamlit/secrets.toml", "w", encoding="utf-8") as f:
                            f.write(toml_content)

                        st.success("✅ Credentials verified & stored in `.streamlit/secrets.toml`!")
                        st.info("Ensure Step 2 is completed, then click Test Connection.")
                        if st.button("🚀 Test Connection & Launch App", type="primary"):
                            st.rerun()
                    else:
                        st.error("The uploaded file does not match a Google Service Account JSON key.")
                except Exception as e:
                    st.error(f"Error parsing JSON: {e}")

    with col2:
        with st.container(border=True):
            st.markdown("### 📋 Step 2: Grant Sheet Access")
            st.markdown(
                f"""
                Your designated Google Spreadsheet:  
                👉 **[Open vehicle-expense-sheet](https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit)**

                **How to grant access:**
                1. Click the link above to open your sheet.
                2. Click the blue **Share** button in the top right.
                3. Paste the **client_email** from your downloaded service account JSON.
                4. Set permission to **Editor** and click **Share**.
                """
            )
            st.write("")
            st.markdown(
                f"""
                <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 10px; padding: 12px 16px; font-size: 0.88rem; color: #92400E; margin-bottom: 16px;">
                    <b>Current Status:</b> {message}
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("🔄 Retry Connection", key="retry_conn"):
                st.rerun()

    st.stop()


# ── One-time Google Sheets initialisation ────────────────────────────────────
if not st.session_state.get("sheets_initialized"):
    try:
        initialize_sheets()
        st.session_state.sheets_initialized = True
    except Exception as e:
        st.error(f"Failed to initialize Google Sheet tabs: {e}")
        st.stop()

# ── Define pages ─────────────────────────────────────────────────────────────
login_page = st.Page("pages/login.py", title="Login / Register", icon="🔐", default=True)
home_page = st.Page("pages/home.py", title="My Garage", icon="🚗")
expenses_page = st.Page("pages/expenses.py", title="Log Expense", icon="⛽")
dashboard_page = st.Page("pages/dashboard.py", title="Analytics", icon="📊")

# ── Navigation: unauthenticated → login only; authenticated → main pages ────
if st.session_state.get("user") is None:
    nav = st.navigation([login_page])
else:
    nav = st.navigation([home_page, expenses_page, dashboard_page])

nav.run()

# ── Sidebar Version Footer ───────────────────────────────────────────────────
curr_user = st.session_state.get("user")
with st.sidebar:
    st.write("")
    if curr_user:
        u_name = curr_user.get("display_name", curr_user.get("username", "Driver"))
        st.caption(f"👤 {u_name} &nbsp;·&nbsp; {APP_VERSION}")
    else:
        st.caption(f"{APP_NAME} {APP_VERSION}")
