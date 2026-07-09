"""
HARS: Household Adaptive Risk-Scoring Framework — Browser App (Streamlit)

Run locally with:
    streamlit run app.py

Or deploy free on Streamlit Community Cloud (streamlit.io/cloud) or
Hugging Face Spaces by pushing this file + hars_core.py to a repo.
"""

import streamlit as st
import pandas as pd
import hars_core as hars

st.set_page_config(page_title="HARS — Household Risk Scoring", page_icon="🏠", layout="wide")

if "devices" not in st.session_state:
    st.session_state.devices = []

st.title("🏠 HARS: Household Adaptive Risk-Scoring")
st.caption(
    "Evidence-based, rule-based (no ML) household IoT risk assessment. "
    "Add every smart device in your home, then calculate your household risk score."
)

# ---------------------------------------------------------------------------
# Sidebar: Add a device
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("➕ Add a Device")

    name = st.text_input("Device name", placeholder="e.g. Front Door Camera")
    category = st.selectbox("Device category", list(hars.DEVICE_TAXONOMY.keys()))
    st.caption(f"Examples: {hars.DEVICE_TAXONOMY[category]['examples']}")

    st.markdown("**Device Vulnerability**")
    firmware_updated = st.checkbox("Firmware is up to date", value=True)
    default_credentials = st.checkbox("Still using default login credentials")
    device_age_years = st.number_input("Device age (years)", min_value=0.0, max_value=20.0,
                                        value=1.0, step=0.5)

    st.markdown("**Data Sensitivity**")
    handles_health = st.checkbox("Handles biometric / health data")
    handles_financial = st.checkbox("Handles financial data")

    st.markdown("**Network Exposure**")
    cloud_connected = st.checkbox("Connects to a cloud service", value=True)
    port_forwarding = st.checkbox("Uses port forwarding / remote access")
    uses_vpn = st.checkbox("On a VPN or segmented (isolated) network")

    st.markdown("**User Behaviour**")
    changed_password = st.checkbox("Default password has been changed", value=True)
    updates_enabled = st.checkbox("Automatic updates enabled", value=True)
    reuses_passwords = st.checkbox("Password is reused from another account")

    st.markdown("**Compliance**")
    etsi_certified = st.checkbox("ETSI EN 303 645 certified")
    vendor_discloses = st.checkbox("Vendor publishes a vulnerability disclosure policy")

    if st.button("Add Device", type="primary", use_container_width=True):
        if not name.strip():
            st.error("Please enter a device name.")
        else:
            st.session_state.devices.append({
                "name": name.strip(), "category": category,
                "firmware_updated": firmware_updated, "default_credentials": default_credentials,
                "device_age_years": device_age_years,
                "handles_biometric_or_health": handles_health, "handles_financial": handles_financial,
                "cloud_connected": cloud_connected, "exposed_port_forwarding": port_forwarding,
                "uses_vpn_or_segmented_network": uses_vpn,
                "changed_default_password": changed_password, "updates_enabled": updates_enabled,
                "reuses_passwords": reuses_passwords,
                "etsi_303645_certified": etsi_certified,
                "vendor_discloses_vulnerabilities": vendor_discloses,
            })
            st.success(f"Added {name}")

# ---------------------------------------------------------------------------
# Main: device list + assessment
# ---------------------------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📋 Enrolled Devices ({len(st.session_state.devices)})")

    if not st.session_state.devices:
        st.info("No devices added yet. Use the sidebar to add your household's smart devices.")
    else:
        for i, d in enumerate(st.session_state.devices):
            c1, c2 = st.columns([5, 1])
            c1.write(f"**{d['name']}** — {d['category']}")
            if c2.button("Remove", key=f"remove_{i}"):
                st.session_state.devices.pop(i)
                st.rerun()

with col2:
    st.subheader("⚙️ Actions")
    if st.button("Calculate Household HARS Score", type="primary",
                  disabled=not st.session_state.devices, use_container_width=True):
        st.session_state.results = hars.run_household_assessment(st.session_state.devices)
    if st.button("Clear All Devices", use_container_width=True):
        st.session_state.devices = []
        st.session_state.pop("results", None)
        st.rerun()

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
if "results" in st.session_state and st.session_state.devices:
    r = st.session_state.results
    st.divider()
    st.subheader("📊 Household Risk Assessment")

    tier_colors = {"Low": "🟢", "Moderate": "🟡", "High": "🟠", "Critical": "🔴"}

    m1, m2, m3 = st.columns(3)
    m1.metric("Household HARS Score", f"{r['household_score']} / 10")
    m2.metric("Risk Tier", f"{tier_colors[r['household_tier']]} {r['household_tier']}")
    m3.metric("Linear-mean score (reference)", f"{r['linear_mean_score_for_comparison']} / 10")

    if r["weakest_link_floor_applied"]:
        st.warning(
            "⚠️ Weakest-link floor applied: a Critical device raised the household "
            "tier above what the raw aggregate score would suggest."
        )

    st.markdown(f"**Guidance:** {r['guidance']}")

    st.markdown("#### Per-Device Breakdown")
    df = pd.DataFrame(r["per_device"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander("📚 Evidence Traceability (why these weights?)"):
        st.markdown(f"""
| Factor | Weight | Literature Basis |
|---|---|---|
| Device Vulnerability | 30% | {hars.TRACEABILITY['DV']} |
| Data Sensitivity | 25% | {hars.TRACEABILITY['DS']} |
| Network Exposure | 20% | {hars.TRACEABILITY['NE']} |
| User Behaviour | 15% | {hars.TRACEABILITY['UB']} |
| Compliance Status | 10% | {hars.TRACEABILITY['CS']} |

**Aggregation method:** {hars.TRACEABILITY['Aggregation']}
""")

st.divider()
st.caption(
    "HARS is a conceptual, rule-based framework validated on synthetic test scenarios. "
    "It has not yet been empirically validated with real households (see Table 7, "
    "Part A). No data leaves this browser session — all processing is local."
)
