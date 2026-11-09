"""
UI Design System & Component Library for Vehicle Expense Tracker.
Provides modern SaaS CSS styling, custom cards, badges, and component helpers.
Fully optimized for mobile (iPhone 12 mini, 12 Pro Max, Pixel) and tablet (iPad M3 11").
"""

import streamlit as st
from utils.constants import CURRENCY
from utils.helpers import fmt_currency, fmt_number

# ---------------------------------------------------------------------------
# Global CSS Design System — Mobile & Tablet Responsive
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* Import modern font */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* Apply font across Streamlit elements */
html, body, [class*="css"], .stMarkdown, .stText, .stButton, .stTextInput, .stSelectbox {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

/* Page background */
.stApp {
    background-color: #F8FAFC !important;
}

/* Base Typography */
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
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04);
}
.welcome-eyebrow {
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #2563EB;
    font-weight: 700;
    margin-bottom: 4px;
}
.welcome-title {
    font-size: clamp(1.4rem, 4vw, 1.8rem);
    font-weight: 800;
    color: #0F172A !important;
    letter-spacing: -0.02em;
    line-height: 1.25;
    margin: 0;
}
.welcome-sub {
    font-size: 0.9rem;
    color: #64748B;
    margin-top: 6px;
    line-height: 1.45;
}

/* Modern Card Container */
.custom-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.04), 0 2px 4px -2px rgba(15, 23, 42, 0.04);
    transition: all 0.2s ease-in-out;
    margin-bottom: 16px;
}

/* Vehicle Plate Badge (Authentic Indian Plate Style) */
.reg-plate {
    display: inline-flex;
    align-items: center;
    background: #FEF08A;
    color: #1E293B;
    border: 1.5px solid #0F172A;
    border-radius: 6px;
    padding: 3px 8px;
    font-family: 'Courier New', Courier, monospace;
    font-weight: 800;
    font-size: 0.82rem;
    letter-spacing: 0.06em;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    white-space: nowrap;
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

/* Responsive KPI Card System */
.kpi-container {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 14px 16px;
    box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04);
    min-height: 108px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-sizing: border-box;
    width: 100%;
    overflow: hidden;
}
.kpi-title {
    font-size: 0.72rem;
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
    font-size: clamp(1.2rem, 3.2vw, 1.45rem);
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -0.02em;
    line-height: 1.25;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin: 4px 0 5px 0;
}
.kpi-footer {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    min-height: 20px;
}
.kpi-sub-text {
    font-size: 0.73rem;
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
    padding: 20px 22px !important;
    box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.03) !important;
}

/* Touch-Friendly Primary Button (Min 44px tap target on mobile) */
div.stButton > button[kind="primary"],
div.stFormSubmitButton > button[kind="primary"],
div.stButton > button:first-child:not([kind="secondary"]) {
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    min-height: 44px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
    transition: all 0.15s ease-in-out !important;
    touch-action: manipulation !important;
}
div.stButton > button:hover {
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35) !important;
    transform: translateY(-1px) !important;
}

/* Touch-Friendly Secondary Button */
div.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #334155 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
    min-height: 44px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    touch-action: manipulation !important;
}
div.stButton > button[kind="secondary"]:hover {
    background: #F8FAFC !important;
    border-color: #94A3B8 !important;
    color: #0F172A !important;
}

/* Tabs styling */
div[data-testid="stTabs"] button[role="tab"] {
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    color: #64748B !important;
    padding: 10px 16px !important;
    min-height: 44px !important;
    border-radius: 8px !important;
    touch-action: manipulation !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #2563EB !important;
    font-weight: 700 !important;
}

/* Metric card overrides */
div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 12px 16px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
}
div[data-testid="stMetricLabel"] {
    font-size: 0.74rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: #64748B !important;
}
div[data-testid="stMetricValue"] {
    font-size: clamp(1.2rem, 3.2vw, 1.45rem) !important;
    font-weight: 800 !important;
    color: #0F172A !important;
}

/* ══════════════════════════════════════════════════════════════════
   MOBILE & TABLET RESPONSIVE OVERRIDES
   Targets: iPhone 12 mini (360px-375px), iPhone 12 Pro Max (428px),
   Google Pixel 11 Pro (412px), iPad M3 11" (834px-1194px)
   ══════════════════════════════════════════════════════════════════ */

/* Stop iOS Safari auto-zoom on input focus (requires 16px+ font size) */
@media (max-width: 1024px) {
    input, select, textarea, .stTextInput input, .stNumberInput input, .stDateInput input {
        font-size: 16px !important;
    }
}

/* Mobile Screens: iPhone 12 mini (360px), 12 Pro Max (428px), Pixel (412px) */
@media (max-width: 640px) {
    /* Hide side columns on mobile */
    div[data-testid="column"]:has(.hide-on-mobile) {
        display: none !important;
    }

    /* Compact container padding to maximize screen width */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        padding-left: 0.85rem !important;
        padding-right: 0.85rem !important;
    }

    /* Welcome banner compact */
    .welcome-banner {
        padding: 16px 18px !important;
        border-radius: 14px !important;
    }
    .welcome-title {
        font-size: 1.45rem !important;
    }

    /* Form padding */
    div[data-testid="stForm"] {
        padding: 16px 14px !important;
        border-radius: 14px !important;
    }

    /* Responsive KPI cards: 2x2 grid on mobile phones */
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(4)) {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 10px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(4)) > div[data-testid="column"] {
        width: 100% !important;
        min-width: 100% !important;
    }

    /* Filter strip stack */
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3)) {
        display: flex !important;
        flex-direction: column !important;
        gap: 10px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3)) > div[data-testid="column"] {
        width: 100% !important;
        min-width: 100% !important;
    }

    /* Vehicle list 2-column cards stack to 1-column on phone */
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(2)) {
        display: flex !important;
        flex-direction: column !important;
        gap: 12px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(2)) > div[data-testid="column"] {
        width: 100% !important;
        min-width: 100% !important;
    }

    /* Full width buttons on mobile */
    div.stButton > button {
        width: 100% !important;
    }

    /* Tab bar scrollable on small phones (iPhone 12 mini) */
    div[data-testid="stTabs"] {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
    }
    div[data-testid="stTabs"] [role="tablist"] {
        gap: 4px !important;
        flex-wrap: nowrap !important;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        padding: 8px 12px !important;
        font-size: 0.85rem !important;
        white-space: nowrap !important;
    }
}

/* Tablet Screens: iPad M3 11-inch (834px portrait / 1194px landscape) */
@media (min-width: 641px) and (max-width: 1024px) {
    .block-container {
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    /* 4-column KPI cards on iPad: balanced 2x2 or 4x1 */
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(4)) {
        display: grid !important;
        grid-template-columns: 1fr 1fr 1fr 1fr !important;
        gap: 12px !important;
    }

    /* Vehicle cards 2 columns */
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(2)) {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 16px !important;
    }
}
</style>
"""


def apply_custom_css():
    """Inject custom SaaS theme styling with mobile & tablet responsiveness."""
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
        <div style="text-align: center; padding: 36px 18px; background: #FFFFFF; border: 1.5px dashed #CBD5E1; border-radius: 16px; margin: 16px 0;">
            <div style="font-size: 2.6rem; margin-bottom: 10px;">{icon}</div>
            <h3 style="margin: 0 0 6px 0; font-size: 1.15rem; font-weight: 700; color: #1E293B;">{title}</h3>
            <p style="margin: 0 auto; max-width: 440px; font-size: 0.88rem; color: #64748B; line-height: 1.5;">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_version_badge():
    """Return an HTML snippet for a sleek version pill badge."""
    from utils.constants import APP_VERSION
    return f'<span class="badge badge-blue" style="font-size: 0.74rem; font-weight: 700; padding: 2px 7px; border-radius: 9999px;">{APP_VERSION}</span>'


def render_app_footer():
    """Render a subtle SaaS app footer with version number and backend status."""
    from utils.constants import APP_NAME, APP_VERSION, APP_RELEASE_DATE
    st.markdown(
        f"""
        <div style="text-align: center; margin: 48px auto 20px auto; padding-top: 16px; border-top: 1px solid #E2E8F0; max-width: 650px; font-size: 0.78rem; color: #94A3B8;">
            <b>{APP_NAME}</b> <span class="badge badge-slate" style="font-size: 0.72rem; padding: 2px 7px; margin: 0 4px;">{APP_VERSION}</span> &nbsp;·&nbsp; Build {APP_RELEASE_DATE} &nbsp;·&nbsp; Google Sheets Connected
        </div>
        """,
        unsafe_allow_html=True,
    )
