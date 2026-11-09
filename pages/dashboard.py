"""
📊 Dashboard — Executive Vehicle Expense & Mileage Analytics
Modern SaaS dashboard with live KPI cards, interactive Plotly charts, and service forecasting.
Currency: INR (₹)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

from utils.auth import require_auth, get_current_user
from utils.sheets import get_records_by_user, clear_sheet_cache
from utils.constants import TAB_VEHICLES, TAB_FUEL, TAB_SERVICE, TAB_MISC, CURRENCY
from utils.helpers import fmt_currency, fmt_number
from utils.ui import apply_custom_css, render_empty_state, render_kpi

# ── Apply SaaS Theme ────────────────────────────────────────────────────────
apply_custom_css()

# ── Authentication Gate ──────────────────────────────────────────────────────
require_auth()
user = get_current_user()
user_id = user["user_id"]

# ── Header Banner ────────────────────────────────────────────────────────────
dash_h1, dash_h2 = st.columns([8, 2])
with dash_h1:
    st.markdown(
        """
        <div style="margin-bottom: 18px;">
            <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #2563EB; font-weight: 700;">Executive Insights</div>
            <h1 style="margin: 0; font-size: 2rem; font-weight: 800; color: #0F172A; letter-spacing: -0.03em;">Vehicle Analytics & KPIs</h1>
            <p style="margin: 4px 0 0 0; font-size: 0.95rem; color: #64748B;">Comprehensive financial tracking, fuel consumption metrics, and maintenance schedules.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with dash_h2:
    st.write("")
    if st.button("🔄 Sync & Refresh", use_container_width=True, type="secondary"):
        clear_sheet_cache()
        st.toast("✅ Google Sheets data refreshed!")
        st.rerun()

# ── Load Raw Data ────────────────────────────────────────────────────────────
vehicles_df = get_records_by_user(TAB_VEHICLES, user_id)
fuel_df = get_records_by_user(TAB_FUEL, user_id)
service_df = get_records_by_user(TAB_SERVICE, user_id)
misc_df = get_records_by_user(TAB_MISC, user_id)

if vehicles_df.empty:
    render_empty_state("🚗", "No Vehicles Found", "Add your vehicles in the Garage before viewing analytics.")
    if st.button("➕ Go to My Vehicles", type="primary"):
        st.switch_page("pages/home.py")
    st.stop()

# ── Vehicle Mappings ─────────────────────────────────────────────────────────
vehicle_names = vehicles_df["vehicle_name"].dropna().astype(str).tolist()
vehicle_id_map = dict(zip(vehicles_df["vehicle_name"].astype(str), vehicles_df["vehicle_id"].astype(str)))
vehicle_name_map = dict(zip(vehicles_df["vehicle_id"].astype(str), vehicles_df["vehicle_name"].astype(str)))
vehicle_type_map = dict(zip(vehicles_df["vehicle_id"].astype(str), vehicles_df.get("vehicle_type", pd.Series(dtype=str)).astype(str)))

# ── Filter Strip Container ───────────────────────────────────────────────────
with st.container(border=True):
    fc1, fc2, fc3 = st.columns([4, 4, 2])

    default_veh_idx = 0
    if st.session_state.get("selected_vehicle"):
        sel_st = st.session_state["selected_vehicle"]
        if isinstance(sel_st, dict):
            sel_st = sel_st.get("vehicle_name", "")
        if sel_st in vehicle_names:
            default_veh_idx = vehicle_names.index(sel_st) + 1

    with fc1:
        selected_vehicle_name = st.selectbox(
            "🚗 Filter by Vehicle",
            options=["All Vehicles"] + vehicle_names,
            index=default_veh_idx if default_veh_idx <= len(vehicle_names) else 0,
        )

    with fc2:
        today = date.today()
        start_default = today - timedelta(days=365)
        date_range = st.date_input(
            "📅 Date Range Filter",
            value=(start_default, today),
            max_value=today,
        )

    with fc3:
        st.write("")
        st.markdown(
            f"""
            <div style="text-align: right; margin-top: 6px;">
                <span class="badge badge-blue">Fleet: {len(vehicle_names)} active</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

selected_vehicle_id = (
    vehicle_id_map.get(selected_vehicle_name)
    if selected_vehicle_name != "All Vehicles"
    else None
)

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = date_range[0] if isinstance(date_range, (list, tuple)) and len(date_range) > 0 else today - timedelta(days=365)
    end_date = today

st.write("")


# ══════════════════════════════════════════════════════════════════════════════
#  FILTER & DATA TRANSFORMATION
# ══════════════════════════════════════════════════════════════════════════════
def apply_filters(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    if df.empty or date_col not in df.columns:
        return pd.DataFrame(columns=df.columns)
    filtered = df.copy()
    filtered[date_col] = pd.to_datetime(filtered[date_col], errors="coerce")
    filtered = filtered.dropna(subset=[date_col])

    if selected_vehicle_id is not None and "vehicle_id" in filtered.columns:
        filtered = filtered[filtered["vehicle_id"].astype(str) == str(selected_vehicle_id)]

    filtered = filtered[
        (filtered[date_col].dt.date >= start_date) & (filtered[date_col].dt.date <= end_date)
    ]
    return filtered


def calculate_fuel_efficiency(f_df: pd.DataFrame):
    if f_df.empty or "is_full_tank" not in f_df.columns:
        return None

    results = []
    unique_vids = f_df["vehicle_id"].unique() if "vehicle_id" in f_df.columns else []

    for vid in unique_vids:
        vdf = f_df[f_df["vehicle_id"] == vid].copy()
        vdf["odo_reading_km"] = pd.to_numeric(vdf["odo_reading_km"], errors="coerce")
        vdf["fuel_quantity_liters"] = pd.to_numeric(vdf["fuel_quantity_liters"], errors="coerce")
        vdf = vdf.dropna(subset=["odo_reading_km", "fuel_quantity_liters"])
        vdf = vdf.sort_values("odo_reading_km").reset_index(drop=True)

        full_mask = vdf["is_full_tank"].astype(str).str.strip().str.upper() == "TRUE"
        full_indices = vdf[full_mask].index.tolist()

        if len(full_indices) < 2:
            continue

        total_dist = 0.0
        total_fuel = 0.0
        for i in range(len(full_indices) - 1):
            idx1 = full_indices[i]
            idx2 = full_indices[i + 1]
            dist = vdf.loc[idx2, "odo_reading_km"] - vdf.loc[idx1, "odo_reading_km"]
            fuel = vdf.loc[idx1 + 1 : idx2, "fuel_quantity_liters"].sum()
            if dist > 0 and fuel > 0:
                total_dist += dist
                total_fuel += fuel

        if total_fuel > 0:
            results.append(total_dist / total_fuel)

    if results:
        return round(sum(results) / len(results), 2)
    return None


fuel_filtered = apply_filters(fuel_df, "date")
service_filtered = apply_filters(service_df, "date")
misc_filtered = apply_filters(misc_df, "date")

for col in ["total_fuel_cost", "odo_reading_km", "fuel_quantity_liters", "fuel_rate_per_liter"]:
    if col in fuel_filtered.columns:
        fuel_filtered[col] = pd.to_numeric(fuel_filtered[col], errors="coerce").fillna(0.0)

for col in ["total_service_cost", "odo_reading_km"]:
    if col in service_filtered.columns:
        service_filtered[col] = pd.to_numeric(service_filtered[col], errors="coerce").fillna(0.0)

if "amount" in misc_filtered.columns:
    misc_filtered["amount"] = pd.to_numeric(misc_filtered["amount"], errors="coerce").fillna(0.0)

# Build unified expenses table
frames = []
if not fuel_filtered.empty and "total_fuel_cost" in fuel_filtered.columns:
    f = fuel_filtered[["date", "total_fuel_cost", "vehicle_id"]].copy().rename(columns={"total_fuel_cost": "amount"})
    f["type"] = "Fuel"
    frames.append(f)

if not service_filtered.empty and "total_service_cost" in service_filtered.columns:
    s = service_filtered[["date", "total_service_cost", "vehicle_id"]].copy().rename(columns={"total_service_cost": "amount"})
    s["type"] = "Service"
    frames.append(s)

if not misc_filtered.empty and "amount" in misc_filtered.columns:
    m = misc_filtered[["date", "amount", "vehicle_id"]].copy()
    m["type"] = "Misc"
    frames.append(m)

if frames:
    all_expenses_df = pd.concat(frames, ignore_index=True)
    all_expenses_df["amount"] = pd.to_numeric(all_expenses_df["amount"], errors="coerce").fillna(0.0)
    all_expenses_df["date"] = pd.to_datetime(all_expenses_df["date"], errors="coerce")
else:
    all_expenses_df = pd.DataFrame(columns=["date", "amount", "vehicle_id", "type"])


# ══════════════════════════════════════════════════════════════════════════════
#  KPI CALCULATIONS
# ══════════════════════════════════════════════════════════════════════════════
def _first_of_month(y: int, m: int) -> date:
    return date(y, m, 1)

def _prev_month(y: int, m: int):
    return (y - 1, 12) if m == 1 else (y, m - 1)

now = datetime.now()
cur_year, cur_month = now.year, now.month
prev_year, prev_month = _prev_month(cur_year, cur_month)
prev2_year, prev2_month = _prev_month(prev_year, prev_month)

first_this_month = _first_of_month(cur_year, cur_month)
first_last_month = _first_of_month(prev_year, prev_month)
first_two_months_ago = _first_of_month(prev2_year, prev2_month)

def _sum_for_period(df: pd.DataFrame, start: date, end: date) -> float:
    if df.empty or "date" not in df.columns or "amount" not in df.columns:
        return 0.0
    mask = (df["date"].dt.date >= start) & (df["date"].dt.date < end)
    return float(df.loc[mask, "amount"].sum())

this_month_total = _sum_for_period(all_expenses_df, first_this_month, today + timedelta(days=1))
last_month_total = _sum_for_period(all_expenses_df, first_last_month, first_this_month)
two_months_ago_total = _sum_for_period(all_expenses_df, first_two_months_ago, first_last_month)
last_month_delta = last_month_total - two_months_ago_total

efficiency = calculate_fuel_efficiency(fuel_filtered)
efficiency_display = f"{efficiency} km/l" if efficiency is not None else "N/A"

total_distance = 0.0
if not fuel_filtered.empty and "odo_reading_km" in fuel_filtered.columns:
    for vid in fuel_filtered["vehicle_id"].unique():
        vdf = fuel_filtered[fuel_filtered["vehicle_id"] == vid]
        odo = vdf["odo_reading_km"].dropna()
        if len(odo) >= 2 and odo.max() > odo.min():
            total_distance += float(odo.max() - odo.min())

fuel_cost_per_km = "N/A"
if not fuel_filtered.empty and total_distance > 0:
    total_fuel_cost = fuel_filtered["total_fuel_cost"].sum()
    fuel_cost_per_km = f"{CURRENCY}{total_fuel_cost / total_distance:.2f} / km"

avg_fillup = "N/A"
if not fuel_filtered.empty:
    avg_val = fuel_filtered[fuel_filtered["total_fuel_cost"] > 0]["total_fuel_cost"].mean()
    if pd.notna(avg_val):
        avg_fillup = fmt_currency(avg_val)

next_service_display = "No service log"
service_badge_type = "slate"
if not service_df.empty and "odo_reading_km" in service_df.columns:
    upcoming = []
    target_vids = [selected_vehicle_id] if selected_vehicle_id else vehicles_df["vehicle_id"].unique()
    for vid in target_vids:
        v_svc = service_df[service_df["vehicle_id"].astype(str) == str(vid)]
        odo_series = pd.to_numeric(v_svc["odo_reading_km"], errors="coerce").dropna()
        if odo_series.empty or odo_series.max() <= 0:
            continue
        last_service_odo = odo_series.max()
        vtype = str(vehicle_type_map.get(vid, "")).strip().lower()
        interval = 5000 if vtype in ("bike", "motorcycle", "scooter") else 10000
        next_due_odo = last_service_odo + interval

        current_odo = last_service_odo
        if not fuel_df.empty and "odo_reading_km" in fuel_df.columns:
            v_fuel = fuel_df[fuel_df["vehicle_id"].astype(str) == str(vid)]
            fuel_odo = pd.to_numeric(v_fuel["odo_reading_km"], errors="coerce").dropna()
            if not fuel_odo.empty:
                current_odo = max(current_odo, fuel_odo.max())

        remaining = next_due_odo - current_odo
        upcoming.append(remaining)

    if upcoming:
        soonest = min(upcoming)
        if soonest > 0:
            next_service_display = f"in {fmt_number(soonest, 0)} km"
            service_badge_type = "green"
        else:
            next_service_display = f"⚠️ Overdue {fmt_number(abs(soonest), 0)} km"
            service_badge_type = "amber"


# ══════════════════════════════════════════════════════════════════════════════
#  MODERN KPI CARDS ROW
# ══════════════════════════════════════════════════════════════════════════════
k1, k2, k3, k4 = st.columns(4)

with k1:
    delta_pill = ""
    badge_color = "slate"
    if last_month_delta > 0:
        delta_pill = f"↑ {fmt_currency(last_month_delta)}"
        badge_color = "amber"
    elif last_month_delta < 0:
        delta_pill = f"↓ {fmt_currency(abs(last_month_delta))}"
        badge_color = "green"
    else:
        delta_pill = "No change"
        badge_color = "slate"

    render_kpi(
        title="Last Month Spend",
        value=fmt_currency(last_month_total),
        sub="vs 2 mos prior",
        badge_text=delta_pill,
        badge_type=badge_color,
    )

with k2:
    render_kpi(
        title="This Month Spend",
        value=fmt_currency(this_month_total),
        sub="month to date",
        badge_text="Active Month",
        badge_type="blue",
    )

with k3:
    render_kpi(
        title="Fuel Efficiency",
        value=efficiency_display,
        sub="full-tank math",
        badge_text="Real Mileage" if efficiency else "Need 2 Fills",
        badge_type="green" if efficiency else "slate",
    )

with k4:
    render_kpi(
        title="Tracked Distance",
        value=f"{fmt_number(total_distance, 0)} km",
        sub="recorded fill-ups",
        badge_text="Odometer",
        badge_type="blue",
    )

st.write("")

k5, k6, k7, k8 = st.columns(4)

with k5:
    render_kpi(
        title="Running Cost / km",
        value=fuel_cost_per_km,
        sub="fuel spent ÷ km",
        badge_text="Economy",
        badge_type="blue",
    )

with k6:
    total_spend_filtered = all_expenses_df["amount"].sum() if not all_expenses_df.empty else 0.0
    try:
        s_str = start_date.strftime("%d %b")
        e_str = end_date.strftime("%d %b")
        range_sub = f"{s_str} – {e_str}"
    except Exception:
        range_sub = "filtered period"

    render_kpi(
        title="Period Spend",
        value=fmt_currency(total_spend_filtered),
        sub=range_sub,
        badge_text="Custom Range",
        badge_type="purple",
    )

with k7:
    render_kpi(
        title="Average Fill-up",
        value=avg_fillup,
        sub="mean pump invoice",
        badge_text="Per Fill",
        badge_type="slate",
    )

with k8:
    render_kpi(
        title="Next Service",
        value=next_service_display,
        sub="10k car / 5k bike",
        badge_text="Schedule",
        badge_type=service_badge_type,
    )

st.write("")
st.write("")

# ══════════════════════════════════════════════════════════════════════════════
#  INTERACTIVE CHARTS (MODERN SAAS PALETTE)
# ══════════════════════════════════════════════════════════════════════════════
COLOR_FUEL = "#2563EB"     # Royal Blue
COLOR_SERVICE = "#D97706"  # Amber
COLOR_MISC = "#059669"     # Emerald Green
COLOR_TOTAL = "#4F46E5"    # Indigo
COLOR_MAP = {"Fuel": COLOR_FUEL, "Service": COLOR_SERVICE, "Misc": COLOR_MISC, "Total": COLOR_TOTAL}
CHART_HEIGHT = 380

BASE_LAYOUT = dict(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#334155", size=12),
    margin=dict(l=20, r=20, t=50, b=30),
    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
    height=CHART_HEIGHT,
)

# ── Charts Row 1 ─────────────────────────────────────────────────────────────
c_row1_1, c_row1_2 = st.columns([6, 4])

with c_row1_1:
    with st.container(border=True):
        st.markdown("### 📈 Monthly Expense Trajectory")
        st.caption("Month-by-month spend across fuel, service, and miscellaneous categories.")

        if all_expenses_df.empty or (all_expenses_df["amount"] == 0).all():
            render_empty_state("📉", "No Monthly Data", "Expenses will be grouped into monthly trends as you log them.")
        else:
            trend_df = all_expenses_df.copy()
            trend_df["month_dt"] = trend_df["date"].dt.to_period("M").dt.to_timestamp()

            monthly_type = trend_df.groupby(["month_dt", "type"])["amount"].sum().reset_index()
            monthly_total = trend_df.groupby("month_dt")["amount"].sum().reset_index()
            monthly_total["type"] = "Total"

            combined = pd.concat([monthly_type, monthly_total], ignore_index=True)
            combined["month_label"] = combined["month_dt"].dt.strftime("%b %Y")

            fig_trend = px.line(
                combined,
                x="month_dt",
                y="amount",
                color="type",
                color_discrete_map=COLOR_MAP,
                markers=True,
                labels={"amount": f"Expense ({CURRENCY})", "month_dt": "Month", "type": "Category"},
            )
            fig_trend.update_layout(**BASE_LAYOUT)
            fig_trend.update_xaxes(dtick="M1", tickformat="%b %Y", showgrid=True, gridcolor="#F1F5F9")
            fig_trend.update_yaxes(showgrid=True, gridcolor="#F1F5F9", tickprefix=f"{CURRENCY} ")
            st.plotly_chart(fig_trend, use_container_width=True)

with c_row1_2:
    with st.container(border=True):
        st.markdown("### 🍩 Category Allocation")
        st.caption("Distribution of expenses between Fuel, Service, and Misc.")

        if all_expenses_df.empty or (all_expenses_df["amount"] == 0).all():
            render_empty_state("🍩", "No Category Data", "Category share will appear when expenses are added.")
        else:
            breakdown = all_expenses_df.groupby("type")["amount"].sum().reset_index()
            breakdown = breakdown[breakdown["amount"] > 0]

            fig_donut = px.pie(
                breakdown,
                values="amount",
                names="type",
                hole=0.55,
                color="type",
                color_discrete_map=COLOR_MAP,
            )
            fig_donut.update_traces(
                textposition="outside",
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>Spent: " + CURRENCY + "%{value:,.2f}<br>Share: %{percent}",
            )
            fig_donut.update_layout(**BASE_LAYOUT)
            st.plotly_chart(fig_donut, use_container_width=True)

st.write("")

# ── Charts Row 2 ─────────────────────────────────────────────────────────────
c_row2_1, c_row2_2 = st.columns([5, 5])

with c_row2_1:
    with st.container(border=True):
        st.markdown("### 🚗 Spend Comparison by Vehicle")
        st.caption("Total cost incurred per vehicle in your garage.")

        if all_expenses_df.empty or (all_expenses_df["amount"] == 0).all():
            render_empty_state("📊", "No Vehicle Data", "Vehicle spend breakdown will appear once entries are logged.")
        else:
            by_vehicle = (
                all_expenses_df.groupby("vehicle_id")["amount"]
                .sum()
                .reset_index()
                .sort_values("amount", ascending=True)
            )
            by_vehicle["vehicle_name"] = by_vehicle["vehicle_id"].map(vehicle_name_map).fillna("Unknown")

            fig_bar = px.bar(
                by_vehicle,
                x="amount",
                y="vehicle_name",
                orientation="h",
                labels={"amount": f"Total Spent ({CURRENCY})", "vehicle_name": "Vehicle"},
                color_discrete_sequence=[COLOR_FUEL],
                text_auto=".2s",
            )
            fig_bar.update_layout(**BASE_LAYOUT)
            fig_bar.update_xaxes(showgrid=True, gridcolor="#F1F5F9", tickprefix=f"{CURRENCY} ")
            st.plotly_chart(fig_bar, use_container_width=True)

with c_row2_2:
    with st.container(border=True):
        st.markdown("### ⛽ Fuel Price Trajectory (₹ / Litre)")
        st.caption("Historical price per litre changes recorded across fill-ups.")

        if fuel_filtered.empty or "fuel_rate_per_liter" not in fuel_filtered.columns:
            render_empty_state("📈", "No Price Data", "Log fuel entries to see price fluctuation curves.")
        else:
            price_df = fuel_filtered[fuel_filtered["fuel_rate_per_liter"] > 0][["date", "fuel_rate_per_liter", "vehicle_id"]].dropna().copy()
            if price_df.empty:
                render_empty_state("📈", "No Price Data", "No valid fuel rate recorded yet.")
            else:
                price_df["vehicle_name"] = price_df["vehicle_id"].map(vehicle_name_map).fillna("Unknown")
                price_df = price_df.sort_values("date")

                fig_price = px.line(
                    price_df,
                    x="date",
                    y="fuel_rate_per_liter",
                    color="vehicle_name",
                    markers=True,
                    labels={
                        "fuel_rate_per_liter": f"Price ({CURRENCY}/L)",
                        "date": "Date",
                        "vehicle_name": "Vehicle",
                    },
                )
                fig_price.update_layout(**BASE_LAYOUT)
                fig_price.update_xaxes(showgrid=True, gridcolor="#F1F5F9")
                fig_price.update_yaxes(showgrid=True, gridcolor="#F1F5F9", tickprefix=f"{CURRENCY} ")
                st.plotly_chart(fig_price, use_container_width=True)
