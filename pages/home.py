"""
My Vehicles — Garage & Fleet Management
Modern SaaS layout with vehicle spec cards, authentic license plates, and quick stats.
"""

import streamlit as st
import pandas as pd

from utils.auth import require_auth, get_current_user, logout
from utils.sheets import (
    get_records_by_user_list,
    get_records_by_user,
    append_record,
    update_record,
    soft_delete_record,
)
from utils.constants import (
    TAB_VEHICLES,
    TAB_FUEL,
    TAB_SERVICE,
    TAB_MISC,
    VEHICLE_TYPES,
    FUEL_TYPES,
    CURRENCY,
)
from utils.helpers import generate_id, now_ist, fmt_currency, fmt_number
from utils.ui import apply_custom_css, render_empty_state, render_vehicle_badge

# ---------- Apply SaaS Theme ----------
apply_custom_css()

# ---------- Auth Guard ----------
require_auth()
user = get_current_user()
user_id = user["user_id"]
display_name = user.get("display_name", "User")

# ---------- Header Banner (High-contrast, clearly legible) ----------
st.markdown(
    f"""
    <div class="welcome-banner">
        <div class="welcome-eyebrow">Garage & Fleet Overview</div>
        <div class="welcome-title">Welcome, {display_name}! 👋</div>
        <div class="welcome-sub">Manage your registered vehicles, log expenses, and monitor fuel efficiency.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Top Bar with Logout & Add Vehicle Action
top_left, top_right = st.columns([7, 3])

if "show_add_vehicle" not in st.session_state:
    st.session_state.show_add_vehicle = False
if "editing_vehicle" not in st.session_state:
    st.session_state.editing_vehicle = None
if "confirm_delete_vehicle" not in st.session_state:
    st.session_state.confirm_delete_vehicle = None

with top_left:
    btn_label = "✖️ Close Form" if st.session_state.show_add_vehicle else "➕ Add New Vehicle"
    if st.button(btn_label, type="primary" if not st.session_state.show_add_vehicle else "secondary"):
        st.session_state.show_add_vehicle = not st.session_state.show_add_vehicle
        st.rerun()

with top_right:
    if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
        logout()
        st.rerun()

st.write("")

# ============================================================
# Add Vehicle Form (Modern Drawer)
# ============================================================
if st.session_state.show_add_vehicle:
    with st.form("add_vehicle_form", clear_on_submit=True):
        st.markdown("### 🚘 Add a Vehicle to Your Garage")
        st.caption("Provide your vehicle details. All information will be synced with your Google Sheet.")
        st.write("")

        col1, col2 = st.columns(2)
        with col1:
            vehicle_name = st.text_input("Vehicle Nickname *", placeholder='e.g. My Swift, Dad\'s Creta, Office Bike')
            make = st.text_input("Brand / Make", placeholder='e.g. Maruti Suzuki, Hyundai, Honda')
            year = st.number_input("Manufacturing Year", min_value=1990, max_value=2030, value=2024, step=1)
            fuel_type = st.selectbox("Primary Fuel Type", FUEL_TYPES)
        with col2:
            vehicle_type = st.selectbox("Vehicle Category", VEHICLE_TYPES)
            model = st.text_input("Model Variant", placeholder='e.g. Swift VXi, City ZX, Activa 6G')
            registration_no = st.text_input("Registration Plate Number", placeholder='e.g. MH-12-AB-1234')

        st.write("")
        submit_add = st.form_submit_button("💾 Save Vehicle to Garage", use_container_width=True, type="primary")

        if submit_add:
            if not vehicle_name.strip():
                st.error("Please enter a vehicle nickname.")
            else:
                record = {
                    "vehicle_id": generate_id(),
                    "user_id": user_id,
                    "vehicle_name": vehicle_name.strip(),
                    "vehicle_type": vehicle_type,
                    "make": make.strip(),
                    "model": model.strip(),
                    "year": str(int(year)),
                    "registration_no": registration_no.strip().upper(),
                    "fuel_type": fuel_type,
                    "is_deleted": "FALSE",
                    "created_at": now_ist(),
                    "updated_at": "",
                }
                append_record(TAB_VEHICLES, record)
                st.session_state.show_add_vehicle = False
                st.toast("✅ Vehicle added to your garage!")
                st.rerun()

    st.write("")


# ============================================================
# Load Vehicles & Fleet Statistics
# ============================================================
vehicles = get_records_by_user_list(TAB_VEHICLES, user_id)

# Fetch user expenses for mini-stats
fuel_df = get_records_by_user(TAB_FUEL, user_id)
service_df = get_records_by_user(TAB_SERVICE, user_id)
misc_df = get_records_by_user(TAB_MISC, user_id)

if not vehicles:
    render_empty_state(
        icon="🚗",
        title="Your Garage is Empty",
        description="You have not added any vehicles yet. Click '+ Add New Vehicle' above to register your car, motorcycle, or fleet vehicle.",
    )
else:
    # Fleet Summary Stats
    total_fleet_spend = 0.0
    if not fuel_df.empty and "total_fuel_cost" in fuel_df.columns:
        total_fleet_spend += pd.to_numeric(fuel_df["total_fuel_cost"], errors="coerce").fillna(0).sum()
    if not service_df.empty and "total_service_cost" in service_df.columns:
        total_fleet_spend += pd.to_numeric(service_df["total_service_cost"], errors="coerce").fillna(0).sum()
    if not misc_df.empty and "amount" in misc_df.columns:
        total_fleet_spend += pd.to_numeric(misc_df["amount"], errors="coerce").fillna(0).sum()

    st.markdown(
        f"""
        <div style="display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap;">
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 12px 20px; flex: 1; min-width: 160px;">
                <div style="font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Total Vehicles</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #0F172A;">{len(vehicles)}</div>
            </div>
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 12px 20px; flex: 1; min-width: 160px;">
                <div style="font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Fleet Lifetime Spend</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #2563EB;">{fmt_currency(total_fleet_spend)}</div>
            </div>
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 12px 20px; flex: 1; min-width: 160px;">
                <div style="font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Sync Status</div>
                <div style="font-size: 1rem; font-weight: 700; color: #059669; display: flex; align-items: center; gap: 6px; margin-top: 4px;">
                    <span style="display: inline-block; width: 8px; height: 8px; background: #059669; border-radius: 50%;"></span>
                    Google Sheets Connected
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- Edit Vehicle Form (if active) ----------
    if st.session_state.editing_vehicle is not None:
        ev = st.session_state.editing_vehicle
        with st.expander(f"✏️ Editing Vehicle: {ev.get('vehicle_name', 'Vehicle')}", expanded=True):
            with st.form("edit_vehicle_form"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    edit_name = st.text_input("Vehicle Nickname *", value=ev.get("vehicle_name", ""))
                    edit_make = st.text_input("Make / Brand", value=ev.get("make", ""))
                    try:
                        cur_year = int(ev.get("year", 2024))
                    except (ValueError, TypeError):
                        cur_year = 2024
                    edit_year = st.number_input("Manufacturing Year", min_value=1990, max_value=2030, value=cur_year, step=1)
                    fuel_val = ev.get("fuel_type", FUEL_TYPES[0])
                    fuel_idx = FUEL_TYPES.index(fuel_val) if fuel_val in FUEL_TYPES else 0
                    edit_fuel = st.selectbox("Fuel Type", FUEL_TYPES, index=fuel_idx)
                with ec2:
                    type_val = ev.get("vehicle_type", VEHICLE_TYPES[0])
                    type_idx = VEHICLE_TYPES.index(type_val) if type_val in VEHICLE_TYPES else 0
                    edit_type = st.selectbox("Vehicle Category", VEHICLE_TYPES, index=type_idx)
                    edit_model = st.text_input("Model Variant", value=ev.get("model", ""))
                    edit_reg = st.text_input("Registration Plate Number", value=ev.get("registration_no", ""))

                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    save_edit = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
                with btn_col2:
                    cancel_edit = st.form_submit_button("❌ Cancel", use_container_width=True)

                if save_edit:
                    if not edit_name.strip():
                        st.error("Vehicle name is required.")
                    else:
                        updates = {
                            "vehicle_name": edit_name.strip(),
                            "vehicle_type": edit_type,
                            "make": edit_make.strip(),
                            "model": edit_model.strip(),
                            "year": str(int(edit_year)),
                            "registration_no": edit_reg.strip().upper(),
                            "fuel_type": edit_fuel,
                            "updated_at": now_ist(),
                        }
                        update_record(TAB_VEHICLES, "vehicle_id", ev["vehicle_id"], updates)
                        st.session_state.editing_vehicle = None
                        st.toast("✅ Vehicle details updated!")
                        st.rerun()

                if cancel_edit:
                    st.session_state.editing_vehicle = None
                    st.rerun()

        st.write("")

    # ---------- Vehicle Cards (Grid) ----------
    VEHICLE_EMOJI = {"Car": "🚗", "Bike": "🏍️", "Truck": "🚛", "Bus": "🚌", "Auto": "🛺", "Other": "🚙"}

    cols = st.columns(2)
    for idx, v in enumerate(vehicles):
        vid = v.get("vehicle_id")
        v_name = v.get("vehicle_name", "Vehicle")
        v_type = v.get("vehicle_type", "Car")
        v_reg = v.get("registration_no", "").strip()
        v_fuel = v.get("fuel_type", "Petrol")
        emoji = VEHICLE_EMOJI.get(v_type, "🚗")

        # Compute per-vehicle stats
        v_spend = 0.0
        v_fills = 0
        v_max_odo = 0.0

        if not fuel_df.empty and "vehicle_id" in fuel_df.columns:
            vf = fuel_df[fuel_df["vehicle_id"].astype(str) == str(vid)]
            if not vf.empty:
                v_spend += pd.to_numeric(vf.get("total_fuel_cost", 0), errors="coerce").fillna(0).sum()
                v_fills = len(vf)
                odos = pd.to_numeric(vf.get("odo_reading_km", 0), errors="coerce").dropna()
                if not odos.empty:
                    v_max_odo = max(v_max_odo, odos.max())

        if not service_df.empty and "vehicle_id" in service_df.columns:
            vs = service_df[service_df["vehicle_id"].astype(str) == str(vid)]
            if not vs.empty:
                v_spend += pd.to_numeric(vs.get("total_service_cost", 0), errors="coerce").fillna(0).sum()
                odos = pd.to_numeric(vs.get("odo_reading_km", 0), errors="coerce").dropna()
                if not odos.empty:
                    v_max_odo = max(v_max_odo, odos.max())

        if not misc_df.empty and "vehicle_id" in misc_df.columns:
            vm = misc_df[misc_df["vehicle_id"].astype(str) == str(vid)]
            if not vm.empty:
                v_spend += pd.to_numeric(vm.get("amount", 0), errors="coerce").fillna(0).sum()

        with cols[idx % 2]:
            with st.container(border=True):
                # Header with icon and name
                badge_plate_html = render_vehicle_badge(v_reg) if v_reg else ""
                spec_str = " · ".join(filter(None, [v.get("make"), v.get("model"), str(v.get("year", ""))]))

                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="width: 48px; height: 48px; background: #F1F5F9; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.6rem;">
                                {emoji}
                            </div>
                            <div>
                                <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #0F172A;">{v_name}</h3>
                                <div style="font-size: 0.85rem; color: #64748B; margin-top: 2px;">{spec_str if spec_str else v_type}</div>
                            </div>
                        </div>
                        {badge_plate_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Badges row
                st.markdown(
                    f"""
                    <div style="display: flex; gap: 6px; margin-bottom: 16px;">
                        <span class="badge badge-blue">⛽ {v_fuel}</span>
                        <span class="badge badge-slate">🏷️ {v_type}</span>
                        <span class="badge badge-green">🛣️ {fmt_number(v_max_odo, 0) if v_max_odo > 0 else '0'} km ODO</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Quick Stats Strip
                st.markdown(
                    f"""
                    <div style="display: grid; grid-template-columns: 1fr 1fr; background: #F8FAFC; border-radius: 10px; padding: 10px 14px; margin-bottom: 16px; border: 1px solid #F1F5F9;">
                        <div>
                            <div style="font-size: 0.72rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Total Spent</div>
                            <div style="font-size: 1.1rem; font-weight: 800; color: #0F172A;">{fmt_currency(v_spend)}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.72rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Fill-up Logs</div>
                            <div style="font-size: 1.1rem; font-weight: 800; color: #0F172A;">{v_fills} times</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Action Buttons
                act_c1, act_c2 = st.columns(2)
                with act_c1:
                    if st.button("⛽ Log Expense", key=f"exp_{vid}", use_container_width=True, type="primary"):
                        st.session_state.selected_vehicle = v_name
                        st.switch_page("pages/expenses.py")
                with act_c2:
                    if st.button("📊 Analytics", key=f"dash_{vid}", use_container_width=True):
                        st.session_state.selected_vehicle = v_name
                        st.switch_page("pages/dashboard.py")

                # Secondary row for Edit & Delete
                sub_c1, sub_c2, _ = st.columns([1, 1, 2])
                with sub_c1:
                    if st.button("✏️ Edit", key=f"edit_{vid}", use_container_width=True):
                        st.session_state.editing_vehicle = v
                        st.rerun()
                with sub_c2:
                    if st.button("🗑️ Delete", key=f"del_{vid}", use_container_width=True):
                        st.session_state.confirm_delete_vehicle = vid
                        st.rerun()

                # Delete Confirmation Box
                if st.session_state.confirm_delete_vehicle == vid:
                    st.warning(f"Delete **{v_name}**? Historical records will stay safely archived in Google Sheets.")
                    c_col1, c_col2 = st.columns(2)
                    with c_col1:
                        if st.button("✅ Confirm Delete", key=f"confirm_del_{vid}", use_container_width=True, type="primary"):
                            soft_delete_record(TAB_VEHICLES, "vehicle_id", vid)
                            st.session_state.confirm_delete_vehicle = None
                            st.toast("🗑️ Vehicle removed.")
                            st.rerun()
                    with c_col2:
                        if st.button("❌ Cancel", key=f"cancel_del_{vid}", use_container_width=True):
                            st.session_state.confirm_delete_vehicle = None
                            st.rerun()
