"""
Expense Logging Page — Fuel, Service, and Miscellaneous expenses.
Modern SaaS design with active vehicle banner, smart calculator, and financial transaction stream.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date

from utils.auth import require_auth, get_current_user
from utils.sheets import (
    get_records_by_user_list,
    get_records_by_vehicle,
    append_record,
    update_record,
    soft_delete_record,
)
from utils.constants import (
    TAB_VEHICLES,
    TAB_FUEL,
    TAB_SERVICE,
    TAB_MISC,
    FUEL_TYPES,
    SERVICE_TYPES,
    MISC_CATEGORIES,
    CURRENCY,
)
from utils.helpers import generate_id, now_ist, today_date, fmt_currency, parse_date, fmt_number
from utils.ui import apply_custom_css, render_empty_state, render_vehicle_badge

# ── Apply Styling ────────────────────────────────────────────────────────────
apply_custom_css()

# ── Authentication gate ──────────────────────────────────────────────────────
require_auth()
user = get_current_user()
user_id = user["user_id"]

# ── Fetch user's vehicles ────────────────────────────────────────────────────
vehicles = get_records_by_user_list(TAB_VEHICLES, user_id)

if not vehicles:
    render_empty_state(
        icon="🚗",
        title="No Vehicles Registered",
        description="You need to register at least one vehicle before logging expenses.",
    )
    if st.button("➕ Register a Vehicle Now", type="primary"):
        st.switch_page("pages/home.py")
    st.stop()

vehicle_names = [v["vehicle_name"] for v in vehicles]
vehicle_map = {v["vehicle_name"]: v for v in vehicles}

# Pre-select vehicle
default_idx = 0
sel_from_state = st.session_state.get("selected_vehicle")
if isinstance(sel_from_state, dict):
    sel_name = sel_from_state.get("vehicle_name", "")
else:
    sel_name = str(sel_from_state) if sel_from_state else ""

if sel_name in vehicle_names:
    default_idx = vehicle_names.index(sel_name)

# ── Active Vehicle Top Banner ────────────────────────────────────────────────
top_v_col1, top_v_col2 = st.columns([7, 3])

with top_v_col2:
    selected_vehicle_name = st.selectbox(
        "🚗 Active Vehicle",
        vehicle_names,
        index=default_idx,
        key="expense_vehicle_selector",
    )
    st.session_state["selected_vehicle"] = selected_vehicle_name

vehicle = vehicle_map[selected_vehicle_name]
vehicle_id = vehicle["vehicle_id"]
v_reg = vehicle.get("registration_no", "").strip()
v_fuel = vehicle.get("fuel_type", "Petrol")
v_type = vehicle.get("vehicle_type", "Car")

with top_v_col1:
    plate_html = render_vehicle_badge(v_reg) if v_reg else ""
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 12px;">
            <div style="width: 52px; height: 52px; background: linear-gradient(135deg, #2563EB, #1D4ED8); border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; box-shadow: 0 4px 10px rgba(37,99,235,0.25);">
                ⛽
            </div>
            <div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <h2 style="margin: 0; font-size: 1.6rem; font-weight: 800; color: #0F172A;">{selected_vehicle_name}</h2>
                    {plate_html}
                </div>
                <div style="font-size: 0.85rem; color: #64748B; margin-top: 2px;">
                    Category: <b>{v_type}</b> &nbsp;|&nbsp; Primary Fuel: <b>{v_fuel}</b>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# ── Tabs ─────────────────────────────────────────────────────────────────────
fuel_tab, service_tab, misc_tab = st.tabs(
    ["⛽ Fuel Fill-Up", "🔧 Service & Maintenance", "📦 Miscellaneous & Tolls"]
)


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def _safe_float(val, default=0.0):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _safe_str(val, default=""):
    if val is None:
        return default
    return str(val).strip() or default


def _resolve_date(raw_val):
    if isinstance(raw_val, (date, datetime)):
        return raw_val.date() if isinstance(raw_val, datetime) else raw_val
    parsed = parse_date(raw_val)
    return parsed if parsed else today_date()


# ═══════════════════════════════════════════════════════════════════════════════
#  ⛽ FUEL TAB
# ═══════════════════════════════════════════════════════════════════════════════
with fuel_tab:
    editing_fuel = st.session_state.get("editing_fuel")
    is_editing_fuel = editing_fuel is not None

    if is_editing_fuel:
        st.markdown(
            """
            <div style="background: #FEF3C7; border: 1px solid #FDE68A; border-radius: 12px; padding: 12px 18px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 600; color: #92400E;">✏️ Editing Fuel Entry — Updates will sync directly to Google Sheets</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("❌ Cancel Edit", key="fuel_cancel_edit"):
            st.session_state.pop("editing_fuel", None)
            st.rerun()

    fuel_defaults = {
        "date": today_date(),
        "odo_reading_km": 0.0,
        "trip_km": 0.0,
        "fuel_quantity_liters": 0.0,
        "fuel_rate_per_liter": 0.0,
        "total_fuel_cost": 0.0,
        "is_full_tank": True,
        "fuel_type": v_fuel if v_fuel in FUEL_TYPES else FUEL_TYPES[0],
        "comments": "",
    }
    if is_editing_fuel:
        fuel_defaults.update(
            {
                "date": _resolve_date(editing_fuel.get("date")),
                "odo_reading_km": _safe_float(editing_fuel.get("odo_reading_km")),
                "trip_km": _safe_float(editing_fuel.get("trip_km")),
                "fuel_quantity_liters": _safe_float(editing_fuel.get("fuel_quantity_liters"), 0.0),
                "fuel_rate_per_liter": _safe_float(editing_fuel.get("fuel_rate_per_liter")),
                "total_fuel_cost": _safe_float(editing_fuel.get("total_fuel_cost")),
                "is_full_tank": str(editing_fuel.get("is_full_tank", "TRUE")).upper() == "TRUE",
                "fuel_type": _safe_str(editing_fuel.get("fuel_type"), v_fuel),
                "comments": _safe_str(editing_fuel.get("comments")),
            }
        )

    prefix = "fuel_edit_" if is_editing_fuel else "fuel_"

    with st.form(key=f"{prefix}form", clear_on_submit=not is_editing_fuel):
        st.markdown("#### ⛽ Log Fuel Fill-Up")
        st.caption("Record odometer reading and fuel amount. Rate or total cost will be calculated automatically.")
        st.write("")

        col1, col2 = st.columns(2)
        with col1:
            fuel_date = st.date_input("Date of Fill-up", value=fuel_defaults["date"], key=f"{prefix}date")
            fuel_odo = st.number_input(
                "Odometer Reading (km) *",
                min_value=0.0,
                step=1.0,
                format="%.1f",
                value=fuel_defaults["odo_reading_km"],
                key=f"{prefix}odo",
                help="Total kilometers shown on the dashboard",
            )
            fuel_trip = st.number_input(
                "Trip Meter Reading (km) — optional",
                min_value=0.0,
                step=1.0,
                format="%.1f",
                value=fuel_defaults["trip_km"],
                key=f"{prefix}trip",
            )

        with col2:
            ft_default = fuel_defaults["fuel_type"]
            ft_idx = FUEL_TYPES.index(ft_default) if ft_default in FUEL_TYPES else 0
            fuel_type = st.selectbox("Fuel Type", FUEL_TYPES, index=ft_idx, key=f"{prefix}fuel_type")
            fuel_qty = st.number_input(
                "Fuel Quantity Filled (Litres) *",
                min_value=0.0,
                step=0.5,
                format="%.2f",
                value=fuel_defaults["fuel_quantity_liters"],
                key=f"{prefix}qty",
            )

        st.markdown(
            """
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px 14px; margin: 10px 0 16px 0; font-size: 0.85rem; color: #475569;">
                💡 <b>Smart Cost Calculator</b>: Enter <b>either</b> Rate per Litre <b>or</b> Total Bill. The missing value will be auto-calculated.
            </div>
            """,
            unsafe_allow_html=True,
        )

        cost_col1, cost_col2 = st.columns(2)
        with cost_col1:
            fuel_rate = st.number_input(
                "Fuel Rate (₹ / Litre)",
                min_value=0.0,
                step=0.5,
                format="%.2f",
                value=fuel_defaults["fuel_rate_per_liter"],
                key=f"{prefix}rate",
            )
        with cost_col2:
            fuel_total = st.number_input(
                "Total Bill Paid (₹)",
                min_value=0.0,
                step=10.0,
                format="%.2f",
                value=fuel_defaults["total_fuel_cost"],
                key=f"{prefix}total",
            )

        fuel_full_tank = st.checkbox(
            "✅ Full Tank Fill (enables accurate km/l mileage computation via full-tank method)",
            value=fuel_defaults["is_full_tank"],
            key=f"{prefix}full_tank",
        )

        fuel_comments = st.text_input(
            "Fuel Station / Pump Notes (optional)",
            value=fuel_defaults["comments"],
            key=f"{prefix}comments",
            placeholder="e.g. IndianOil XP95, Shell V-Power, HP Highway Bunk",
        )

        st.write("")
        submitted_fuel = st.form_submit_button(
            "💾 Update Fuel Entry" if is_editing_fuel else "💾 Save Fuel Fill-Up",
            type="primary",
            use_container_width=True,
        )

    if submitted_fuel:
        if fuel_odo <= 0:
            st.error("Please enter a valid odometer reading (> 0).")
        elif fuel_qty <= 0:
            st.error("Please enter a valid fuel quantity in litres (> 0).")
        elif fuel_rate <= 0 and fuel_total <= 0:
            st.error("Please provide either Fuel Rate per Litre OR Total Cost.")
        else:
            if fuel_total > 0 and fuel_rate <= 0:
                fuel_rate = round(fuel_total / fuel_qty, 2)
            elif fuel_rate > 0 and fuel_total <= 0:
                fuel_total = round(fuel_qty * fuel_rate, 2)
            else:
                fuel_rate = round(fuel_total / fuel_qty, 2)

            if is_editing_fuel:
                eid = editing_fuel["expense_id"]
                updates = {
                    "date": str(fuel_date),
                    "odo_reading_km": str(fuel_odo),
                    "trip_km": str(fuel_trip),
                    "fuel_quantity_liters": str(fuel_qty),
                    "fuel_rate_per_liter": str(fuel_rate),
                    "total_fuel_cost": str(fuel_total),
                    "is_full_tank": "TRUE" if fuel_full_tank else "FALSE",
                    "fuel_type": fuel_type,
                    "comments": fuel_comments.strip(),
                    "updated_at": now_ist(),
                }
                update_record(TAB_FUEL, "expense_id", eid, updates)
                st.session_state.pop("editing_fuel", None)
                st.toast("✅ Fuel entry updated in Google Sheets!")
                st.rerun()
            else:
                data = {
                    "expense_id": generate_id(),
                    "vehicle_id": vehicle_id,
                    "user_id": user_id,
                    "date": str(fuel_date),
                    "odo_reading_km": str(fuel_odo),
                    "trip_km": str(fuel_trip),
                    "fuel_quantity_liters": str(fuel_qty),
                    "fuel_rate_per_liter": str(fuel_rate),
                    "total_fuel_cost": str(fuel_total),
                    "is_full_tank": "TRUE" if fuel_full_tank else "FALSE",
                    "fuel_type": fuel_type,
                    "comments": fuel_comments.strip(),
                    "created_at": now_ist(),
                    "is_deleted": "FALSE",
                    "updated_at": "",
                }
                append_record(TAB_FUEL, data)
                st.toast("✅ Fuel fill-up recorded successfully!")
                st.rerun()

    st.write("")
    st.markdown("### 📋 Recent Fuel Logs")

    df_fuel = get_records_by_vehicle(TAB_FUEL, vehicle_id)
    if not df_fuel.empty:
        df_fuel["_sort_date"] = pd.to_datetime(df_fuel["date"], errors="coerce")
        df_fuel = df_fuel.sort_values("_sort_date", ascending=False).reset_index(drop=True)

        for idx, row in df_fuel.iterrows():
            odo_val = _safe_float(row.get("odo_reading_km"))
            qty_val = _safe_float(row.get("fuel_quantity_liters"))
            rate_val = _safe_float(row.get("fuel_rate_per_liter"))
            total_val = _safe_float(row.get("total_fuel_cost"))
            is_full = str(row.get("is_full_tank", "")).upper() == "TRUE"
            comment = _safe_str(row.get("comments"))
            eid = row.get("expense_id", str(idx))

            with st.container(border=True):
                c_main, c_act1, c_act2 = st.columns([7, 1.2, 1.2])
                with c_main:
                    tank_pill = '<span class="badge badge-green">⛽ Full Tank</span>' if is_full else '<span class="badge badge-slate">Partial</span>'
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div>
                                <span style="font-weight: 700; color: #0F172A; font-size: 1.05rem;">{row.get('date', '')}</span>
                                &nbsp; {tank_pill}
                                <div style="font-size: 0.88rem; color: #475569; margin-top: 4px;">
                                    <b>{qty_val:.2f} L</b> filled @ {fmt_currency(rate_val)}/L &nbsp;·&nbsp; ODO: <b>{fmt_number(odo_val, 1)} km</b>
                                </div>
                                {f'<div style="font-size: 0.82rem; color: #64748B; margin-top: 3px;">💬 {comment}</div>' if comment else ''}
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.25rem; font-weight: 800; color: #2563EB;">{fmt_currency(total_val)}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c_act1:
                    if st.button("✏️ Edit", key=f"f_edit_{eid}", use_container_width=True):
                        st.session_state["editing_fuel"] = row.to_dict()
                        st.rerun()
                with c_act2:
                    confirm_key = f"del_confirm_fuel_{eid}"
                    if st.session_state.get(confirm_key):
                        if st.button("Confirm", key=f"f_del_yes_{eid}", type="primary", use_container_width=True):
                            soft_delete_record(TAB_FUEL, "expense_id", eid)
                            st.session_state.pop(confirm_key, None)
                            st.toast("🗑️ Entry deleted.")
                            st.rerun()
                    else:
                        if st.button("🗑️ Del", key=f"f_del_{eid}", use_container_width=True):
                            st.session_state[confirm_key] = True
                            st.rerun()
    else:
        render_empty_state("⛽", "No Fuel Records Yet", "Log your first fuel fill-up using the form above.")


# ═══════════════════════════════════════════════════════════════════════════════
#  🔧 SERVICE TAB
# ═══════════════════════════════════════════════════════════════════════════════
with service_tab:
    editing_service = st.session_state.get("editing_service")
    is_editing_service = editing_service is not None

    if is_editing_service:
        st.markdown(
            """
            <div style="background: #FEF3C7; border: 1px solid #FDE68A; border-radius: 12px; padding: 12px 18px; margin-bottom: 16px;">
                <span style="font-weight: 600; color: #92400E;">✏️ Editing Service Record</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("❌ Cancel Edit", key="svc_cancel_edit"):
            st.session_state.pop("editing_service", None)
            st.rerun()

    svc_defaults = {
        "date": today_date(),
        "odo_reading_km": 0.0,
        "service_type": SERVICE_TYPES[0] if SERVICE_TYPES else "Regular Service",
        "total_service_cost": 0.0,
        "parts_details": "",
        "comments": "",
    }
    if is_editing_service:
        svc_defaults.update(
            {
                "date": _resolve_date(editing_service.get("date")),
                "odo_reading_km": _safe_float(editing_service.get("odo_reading_km")),
                "service_type": _safe_str(editing_service.get("service_type"), SERVICE_TYPES[0]),
                "total_service_cost": _safe_float(editing_service.get("total_service_cost")),
                "parts_details": _safe_str(editing_service.get("parts_details")),
                "comments": _safe_str(editing_service.get("comments")),
            }
        )

    svc_prefix = "service_edit_" if is_editing_service else "service_"

    with st.form(key=f"{svc_prefix}form", clear_on_submit=not is_editing_service):
        st.markdown("#### 🔧 Log Maintenance & Repair")
        st.caption("Record periodic servicing, tyre replacement, oil changes, or repairs.")
        st.write("")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            svc_date = st.date_input("Service Date", value=svc_defaults["date"], key=f"{svc_prefix}date")
            svc_odo = st.number_input(
                "Odometer at Service (km) *",
                min_value=0.0,
                step=100.0,
                format="%.1f",
                value=svc_defaults["odo_reading_km"],
                key=f"{svc_prefix}odo",
            )
        with col_s2:
            st_default = svc_defaults["service_type"]
            st_idx = SERVICE_TYPES.index(st_default) if st_default in SERVICE_TYPES else 0
            svc_type = st.selectbox("Service Classification", SERVICE_TYPES, index=st_idx, key=f"{svc_prefix}type")
            svc_cost = st.number_input(
                "Total Service Bill Cost (₹) *",
                min_value=0.0,
                step=100.0,
                format="%.2f",
                value=svc_defaults["total_service_cost"],
                key=f"{svc_prefix}cost",
            )

        svc_parts = st.text_area(
            "Parts & Labour Breakdown (optional)",
            value=svc_defaults["parts_details"],
            placeholder="e.g. Engine Oil (₹1,450), Oil Filter (₹350), Wheel Alignment (₹600), Labour (₹850)",
            key=f"{svc_prefix}parts",
        )
        svc_comments = st.text_input(
            "Service Center / Workshop Notes (optional)",
            value=svc_defaults["comments"],
            placeholder="e.g. Authorized Hyundai Service Center - Next service due at 40,000 km",
            key=f"{svc_prefix}comments",
        )

        st.write("")
        submitted_service = st.form_submit_button(
            "💾 Update Service Entry" if is_editing_service else "💾 Save Service Record",
            type="primary",
            use_container_width=True,
        )

    if submitted_service:
        if svc_odo <= 0:
            st.error("Please enter a valid odometer reading (> 0).")
        elif svc_cost <= 0:
            st.error("Please enter the total service cost (> 0).")
        else:
            if is_editing_service:
                eid = editing_service["expense_id"]
                updates = {
                    "date": str(svc_date),
                    "odo_reading_km": str(svc_odo),
                    "service_type": svc_type,
                    "total_service_cost": str(svc_cost),
                    "parts_details": svc_parts.strip(),
                    "comments": svc_comments.strip(),
                    "updated_at": now_ist(),
                }
                update_record(TAB_SERVICE, "expense_id", eid, updates)
                st.session_state.pop("editing_service", None)
                st.toast("✅ Service entry updated!")
                st.rerun()
            else:
                data = {
                    "expense_id": generate_id(),
                    "vehicle_id": vehicle_id,
                    "user_id": user_id,
                    "date": str(svc_date),
                    "odo_reading_km": str(svc_odo),
                    "service_type": svc_type,
                    "total_service_cost": str(svc_cost),
                    "parts_details": svc_parts.strip(),
                    "comments": svc_comments.strip(),
                    "created_at": now_ist(),
                    "is_deleted": "FALSE",
                    "updated_at": "",
                }
                append_record(TAB_SERVICE, data)
                st.toast("✅ Service record saved!")
                st.rerun()

    st.write("")
    st.markdown("### 📋 Service History")

    df_svc = get_records_by_vehicle(TAB_SERVICE, vehicle_id)
    if not df_svc.empty:
        df_svc["_sort_date"] = pd.to_datetime(df_svc["date"], errors="coerce")
        df_svc = df_svc.sort_values("_sort_date", ascending=False).reset_index(drop=True)

        for idx, row in df_svc.iterrows():
            odo_val = _safe_float(row.get("odo_reading_km"))
            cost_val = _safe_float(row.get("total_service_cost"))
            parts = _safe_str(row.get("parts_details"))
            comment = _safe_str(row.get("comments"))
            eid = row.get("expense_id", str(idx))

            with st.container(border=True):
                c_main, c_act1, c_act2 = st.columns([7, 1.2, 1.2])
                with c_main:
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div>
                                <span style="font-weight: 700; color: #0F172A; font-size: 1.05rem;">{row.get('date', '')}</span>
                                &nbsp; <span class="badge badge-amber">🔧 {row.get('service_type', '')}</span>
                                <div style="font-size: 0.88rem; color: #475569; margin-top: 4px;">
                                    ODO at service: <b>{fmt_number(odo_val, 1)} km</b>
                                </div>
                                {f'<div style="font-size: 0.82rem; color: #64748B; margin-top: 3px;">🔩 <b>Parts:</b> {parts}</div>' if parts else ''}
                                {f'<div style="font-size: 0.82rem; color: #64748B; margin-top: 2px;">💬 {comment}</div>' if comment else ''}
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.25rem; font-weight: 800; color: #D97706;">{fmt_currency(cost_val)}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c_act1:
                    if st.button("✏️ Edit", key=f"s_edit_{eid}", use_container_width=True):
                        st.session_state["editing_service"] = row.to_dict()
                        st.rerun()
                with c_act2:
                    confirm_key = f"del_confirm_svc_{eid}"
                    if st.session_state.get(confirm_key):
                        if st.button("Confirm", key=f"s_del_yes_{eid}", type="primary", use_container_width=True):
                            soft_delete_record(TAB_SERVICE, "expense_id", eid)
                            st.session_state.pop(confirm_key, None)
                            st.toast("🗑️ Service entry deleted.")
                            st.rerun()
                    else:
                        if st.button("🗑️ Del", key=f"s_del_{eid}", use_container_width=True):
                            st.session_state[confirm_key] = True
                            st.rerun()
    else:
        render_empty_state("🔧", "No Service Records", "Maintenance and repairs for this vehicle will appear here.")


# ═══════════════════════════════════════════════════════════════════════════════
#  📦 MISCELLANEOUS TAB
# ═══════════════════════════════════════════════════════════════════════════════
with misc_tab:
    editing_misc = st.session_state.get("editing_misc")
    is_editing_misc = editing_misc is not None

    if is_editing_misc:
        st.markdown(
            """
            <div style="background: #FEF3C7; border: 1px solid #FDE68A; border-radius: 12px; padding: 12px 18px; margin-bottom: 16px;">
                <span style="font-weight: 600; color: #92400E;">✏️ Editing Miscellaneous Expense</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("❌ Cancel Edit", key="misc_cancel_edit"):
            st.session_state.pop("editing_misc", None)
            st.rerun()

    misc_defaults = {
        "date": today_date(),
        "category": MISC_CATEGORIES[0] if MISC_CATEGORIES else "Toll",
        "amount": 0.0,
        "comments": "",
    }
    if is_editing_misc:
        misc_defaults.update(
            {
                "date": _resolve_date(editing_misc.get("date")),
                "category": _safe_str(editing_misc.get("category"), MISC_CATEGORIES[0]),
                "amount": _safe_float(editing_misc.get("amount")),
                "comments": _safe_str(editing_misc.get("comments")),
            }
        )

    misc_prefix = "misc_edit_" if is_editing_misc else "misc_"

    with st.form(key=f"{misc_prefix}form", clear_on_submit=not is_editing_misc):
        st.markdown("#### 📦 Log Miscellaneous Expense")
        st.caption("Record FASTag recharges, parking tickets, car washes, fines, or accessories.")
        st.write("")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            misc_date = st.date_input("Date", value=misc_defaults["date"], key=f"{misc_prefix}date")
            cat_default = misc_defaults["category"]
            cat_idx = MISC_CATEGORIES.index(cat_default) if cat_default in MISC_CATEGORIES else 0
            misc_category = st.selectbox("Expense Category", MISC_CATEGORIES, index=cat_idx, key=f"{misc_prefix}category")
        with col_m2:
            misc_amount = st.number_input(
                "Expense Amount (₹)",
                min_value=0.0,
                step=50.0,
                format="%.2f",
                value=misc_defaults["amount"],
                key=f"{misc_prefix}amount",
            )

        misc_comments = st.text_input(
            "Expense Description / Notes *",
            value=misc_defaults["comments"],
            placeholder="e.g. Bandra-Worli Sea Link toll, Airport valet parking, 3M ceramic wash",
            key=f"{misc_prefix}comments",
        )

        st.write("")
        submitted_misc = st.form_submit_button(
            "💾 Update Entry" if is_editing_misc else "💾 Save Miscellaneous Expense",
            type="primary",
            use_container_width=True,
        )

    if submitted_misc:
        if misc_amount <= 0 and not misc_comments.strip():
            st.error("Please enter an amount or comments for this expense.")
        else:
            if is_editing_misc:
                eid = editing_misc["expense_id"]
                updates = {
                    "date": str(misc_date),
                    "category": misc_category,
                    "amount": str(misc_amount),
                    "comments": misc_comments.strip(),
                    "updated_at": now_ist(),
                }
                update_record(TAB_MISC, "expense_id", eid, updates)
                st.session_state.pop("editing_misc", None)
                st.toast("✅ Miscellaneous entry updated!")
                st.rerun()
            else:
                data = {
                    "expense_id": generate_id(),
                    "vehicle_id": vehicle_id,
                    "user_id": user_id,
                    "date": str(misc_date),
                    "category": misc_category,
                    "amount": str(misc_amount),
                    "comments": misc_comments.strip(),
                    "created_at": now_ist(),
                    "is_deleted": "FALSE",
                    "updated_at": "",
                }
                append_record(TAB_MISC, data)
                st.toast("✅ Miscellaneous expense saved!")
                st.rerun()

    st.write("")
    st.markdown("### 📋 Miscellaneous Expenses Stream")

    df_misc = get_records_by_vehicle(TAB_MISC, vehicle_id)
    if not df_misc.empty:
        df_misc["_sort_date"] = pd.to_datetime(df_misc["date"], errors="coerce")
        df_misc = df_misc.sort_values("_sort_date", ascending=False).reset_index(drop=True)

        for idx, row in df_misc.iterrows():
            amt_val = _safe_float(row.get("amount"))
            comment = _safe_str(row.get("comments"))
            eid = row.get("expense_id", str(idx))

            with st.container(border=True):
                c_main, c_act1, c_act2 = st.columns([7, 1.2, 1.2])
                with c_main:
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div>
                                <span style="font-weight: 700; color: #0F172A; font-size: 1.05rem;">{row.get('date', '')}</span>
                                &nbsp; <span class="badge badge-green">📦 {row.get('category', '')}</span>
                                {f'<div style="font-size: 0.88rem; color: #475569; margin-top: 4px;">💬 {comment}</div>' if comment else ''}
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.25rem; font-weight: 800; color: #059669;">{fmt_currency(amt_val)}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c_act1:
                    if st.button("✏️ Edit", key=f"m_edit_{eid}", use_container_width=True):
                        st.session_state["editing_misc"] = row.to_dict()
                        st.rerun()
                with c_act2:
                    confirm_key = f"del_confirm_misc_{eid}"
                    if st.session_state.get(confirm_key):
                        if st.button("Confirm", key=f"m_del_yes_{eid}", type="primary", use_container_width=True):
                            soft_delete_record(TAB_MISC, "expense_id", eid)
                            st.session_state.pop(confirm_key, None)
                            st.toast("🗑️ Entry deleted.")
                            st.rerun()
                    else:
                        if st.button("🗑️ Del", key=f"m_del_{eid}", use_container_width=True):
                            st.session_state[confirm_key] = True
                            st.rerun()
    else:
        render_empty_state("📦", "No Miscellaneous Expenses", "Tolls, parking, and miscellaneous expenses will appear here.")
