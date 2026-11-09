"""
UI Design System & Component Library for Vehicle Expense Tracker.
Provides modern SaaS CSS styling, custom cards, badges, and component helpers.
"""

import streamlit as st
from utils.constants import CURRENCY
from utils.helpers import fmt_currency, fmt_number

# ---------------------------------------------------------------------------
# Global CSS Design System
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* Import modern font */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* Apply font across Streamlit elements */
html, body, [class*="css"], .stMarkdown, .stText, .stButton, .stTextInput, .stSelectbox {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Page background */
.stApp {
    background-color: #F8FAFC !important;
}

/* Base Typography (no !important on color so containers can override safely) */
h1 {
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    color: #0F172A;
}
h2 {
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #1E293B;
}
h3 {
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    color: #334155;
}

/* Welcome & Section Banner (Clean, high-contrast white card) */
.welcome-banner {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 22px 28px;
    margin-bottom: 24px;
    box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04);
}
.welcome-eyebrow {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #2563EB;
    font-weight: 700;
    margin-bottom: 4px;
}
.welcome-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #0F172A !important;
    letter-spacing: -0.02em;
    line-height: 1.25;
    margin: 0;
}
.welcome-sub {
    font-size: 0.92rem;
    color: #64748B;
    margin-top: 6px;
    line-height: 1.4;
}

/* Modern Card Container */
.custom-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.04), 0 2px 4px -2px rgba(15, 23, 42, 0.04);
    transition: all 0.2s ease-in-out;
    margin-bottom: 16px;
}
.custom-card:hover {
    border-color: #CBD5E1;
    box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.04);
}

/* Vehicle Plate Badge (Authentic Indian Plate Style) */
.reg-plate {
    display: inline-flex;
    align-items: center;
    background: #FEF08A;
    color: #1E293B;
    border: 1.5px solid #0F172A;
    border-radius: 6px;
    padding: 3px 10px;
    font-family: 'Courier New', Courier, monospace;
    font-weight: 800;
    font-size: 0.85rem;
    letter-spacing: 0.08em;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

/* Modern Pill Badges */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.01em;
    white-space: nowrap;
    line-height: 1.2;
}
.badge-blue { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
.badge-amber { background: #FEF3C7; color: #B45309; border: 1px solid #FDE68A; }
.badge-green { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
.badge-purple { background: #FAF5FF; color: #7E22CE; border: 1px solid #E9D5FF; }
.badge-slate { background: #F1F5F9; color: #475569; border: 1px solid #E2E8F0; }

/* Rock-Solid KPI Card System */
.kpi-container {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04);
    min-height: 114px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-sizing: border-box;
    width: 100%;
    overflow: hidden;
}
.kpi-title {
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #64748B;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.2;
}
.kpi-value {
    font-size: 1.45rem;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -0.02em;
    line-height: 1.25;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin: 5px 0 6px 0;
}
.kpi-footer {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    min-height: 22px;
}
.kpi-sub-text {
    font-size: 0.75rem;
    color: #64748B;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Streamlit Native Form & Buttons Styling */
div[data-testid="stForm"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 16px !important;
    padding: 24px 28px !important;
    box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.03) !important;
}

/* Primary Button */
div.stButton > button[kind="primary"],
div.stFormSubmitButton > button[kind="primary"],
div.stButton > button:first-child:not([kind="secondary"]) {
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 8px 20px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
    transition: all 0.15s ease-in-out !important;
}
div.stButton > button:hover {
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35) !important;
    transform: translateY(-1px) !important;
}

/* Secondary Button */
div.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #334155 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
div.stButton > button[kind="secondary"]:hover {
    background: #F8FAFC !important;
    border-color: #94A3B8 !important;
    color: #0F172A !important;
}

/* Tabs styling */
div[data-testid="stTabs"] button[role="tab"] {
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    color: #64748B !important;
    padding: 10px 20px !important;
    border-radius: 8px !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #2563EB !important;
    font-weight: 700 !important;
}

/* Metric card overrides (for native st.metric if used) */
div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 14px 18px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
}
div[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: #64748B !important;
}
div[data-testid="stMetricValue"] {
    font-size: 1.45rem !important;
    font-weight: 800 !important;
    color: #0F172A !important;
}
</style>
"""


def apply_custom_css():
    """Inject custom SaaS theme styling."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_kpi(title: str, value: str, sub: str = "", badge_text: str = "", badge_type: str = "blue"):
    """Render a rock-solid, responsive SaaS KPI metric box."""
    badge_html = f'<span class="badge badge-{badge_type}">{badge_text}</span>' if badge_text else ""
    sub_html = f'<span class="kpi-sub-text">{sub}</span>' if sub else ""

    html = f"""
    <div class="kpi-container">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-footer">
            {badge_html}
            {sub_html}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_vehicle_badge(reg_no: str):
    """Render an authentic registration number badge."""
    if not reg_no:
        return ""
    return f'<span class="reg-plate">IND {reg_no.upper()}</span>'


def render_empty_state(icon: str, title: str, description: str):
    """Render a clean, illustrated empty state."""
    st.markdown(
        f"""
        <div style="text-align: center; padding: 48px 24px; background: #FFFFFF; border: 1.5px dashed #CBD5E1; border-radius: 16px; margin: 20px 0;">
            <div style="font-size: 3rem; margin-bottom: 12px;">{icon}</div>
            <h3 style="margin: 0 0 6px 0; font-size: 1.2rem; font-weight: 700; color: #1E293B;">{title}</h3>
            <p style="margin: 0 auto; max-width: 440px; font-size: 0.92rem; color: #64748B; line-height: 1.5;">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
