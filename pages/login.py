"""
Login / Register page for Vehicle Expense Tracker.
Provides a modern, consumer-grade SaaS authentication UI.
"""

import streamlit as st
from utils.auth import authenticate, register_user
from utils.constants import APP_NAME, APP_VERSION
from utils.ui import apply_custom_css, render_app_footer

# ── Global Styling ──────────────────────────────────────────────────────────
apply_custom_css()

# ── Redirect if already logged in ───────────────────────────────────────────
if st.session_state.get("user") is not None:
    st.switch_page("pages/home.py")

# ── Top Hero Banner ─────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="text-align: center; margin: 24px 0 32px 0;">
        <div style="display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; background: linear-gradient(135deg, #2563EB, #1D4ED8); border-radius: 18px; box-shadow: 0 10px 20px -5px rgba(37,99,235,0.4); margin-bottom: 16px;">
            <span style="font-size: 2rem;">🚗</span>
        </div>
        <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; color: #0F172A; letter-spacing: -0.03em;">{APP_NAME}</h1>
        <p style="margin: 8px auto 0 auto; max-width: 480px; font-size: 1rem; color: #64748B; line-height: 1.5;">
            Track fuel efficiency, maintenance bills, and vehicle expenses seamlessly backed by Google Sheets.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Centered Auth Card Container (Responsive across mobile & desktop) ──────
col_l, main_col, col_r = st.columns([1, 2.4, 1])

with col_l:
    st.markdown('<div class="hide-on-mobile"></div>', unsafe_allow_html=True)

with col_r:
    st.markdown('<div class="hide-on-mobile"></div>', unsafe_allow_html=True)

with main_col:
    # Feature Badges
    st.markdown(
        """
        <div style="display: flex; justify-content: center; gap: 8px; margin-bottom: 20px; flex-wrap: wrap;">
            <span class="badge badge-blue">⛽ Smart km/L Mileage</span>
            <span class="badge badge-amber">🔧 Service Alerts</span>
            <span class="badge badge-green">🔒 Google Cloud Secure</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, register_tab = st.tabs(["🔐 Sign In", "✨ Create Account"])

    # ── Login Tab ────────────────────────────────────────────────────────────
    with login_tab:
        with st.form("login_form"):
            st.markdown("### Welcome Back")
            st.caption("Sign in to access your garage and expense analytics.")
            st.write("")

            username = st.text_input("Username", placeholder="e.g. roshan").strip()
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            st.write("")
            submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

        if submitted:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                user_dict = authenticate(username, password)
                if user_dict:
                    st.session_state.user = user_dict
                    st.success(f"Welcome back, {user_dict.get('display_name', username)}! Redirecting...")
                    st.rerun()
                else:
                    st.error("Invalid username or password. Please try again.")

    # ── Register Tab ─────────────────────────────────────────────────────────
    with register_tab:
        with st.form("register_form"):
            st.markdown("### Get Started")
            st.caption("Create a new account to start tracking your fleet.")
            st.write("")

            new_username = st.text_input("Choose Username *", placeholder="e.g. roshan").strip()
            new_password = st.text_input("Password *", type="password", placeholder="Choose a password")
            display_name = st.text_input("Full Name / Display Name *", placeholder="e.g. Roshan Sharma").strip()
            email = st.text_input("Email Address (optional)", placeholder="e.g. roshan@example.com").strip()

            st.write("")
            reg_submitted = st.form_submit_button("Create My Account →", use_container_width=True, type="primary")

        if reg_submitted:
            if not new_username or not new_password:
                st.error("Username and password are required.")
            elif not display_name:
                st.error("Display name is required.")
            else:
                user_dict, msg = register_user(new_username, new_password, display_name, email)
                if user_dict:
                    st.success(msg)
                    st.info("👉 Switch to the **Sign In** tab to log in with your new credentials.")
                else:
                    st.error(msg)

    # Trust note
    st.markdown(
        """
        <div style="text-align: center; margin-top: 24px; font-size: 0.8rem; color: #94A3B8;">
            🔒 All expense logs and vehicle data are safely stored in your private Google Spreadsheet.
        </div>
        """,
        unsafe_allow_html=True,
    )


