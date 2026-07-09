"""
HARS: Household Adaptive Risk-Scoring Framework
Core logic module — no ML dependency, rule-based scoring.

Implements Part A Sections 5-7:
- Nine-category device taxonomy
- Five-factor weighted risk-scoring model
- Plain-language output layer
- Evidence-traceability mapping
- Non-linear (RMS) household aggregation with weakest-link floor
"""

import math
from typing import Dict, List

# ---------------------------------------------------------------------------
# 1. Device Taxonomy (9 categories) — Section 5
# ---------------------------------------------------------------------------
DEVICE_TAXONOMY: Dict[str, Dict] = {
    "Entertainment & Media": {"baseline_dv": 5, "baseline_ds": 4,
        "examples": "Smart TVs, streaming devices"},
    "Voice Assistants & Smart Speakers": {"baseline_dv": 6, "baseline_ds": 7,
        "examples": "Amazon Echo, Google Nest"},
    "Home Security & Surveillance": {"baseline_dv": 7, "baseline_ds": 9,
        "examples": "Cameras, smart locks, alarms"},
    "Environmental Controls": {"baseline_dv": 5, "baseline_ds": 3,
        "examples": "Thermostats, HVAC controllers"},
    "Lighting Systems": {"baseline_dv": 4, "baseline_ds": 2,
        "examples": "Smart bulbs, switches"},
    "Kitchen & Appliances": {"baseline_dv": 5, "baseline_ds": 3,
        "examples": "Smart fridges, ovens"},
    "Health & Wellness Devices": {"baseline_dv": 6, "baseline_ds": 9,
        "examples": "Wearables, medical monitors"},
    "Networking Infrastructure": {"baseline_dv": 8, "baseline_ds": 6,
        "examples": "Routers, hubs, range extenders"},
    "Children's IoT & Toys": {"baseline_dv": 7, "baseline_ds": 8,
        "examples": "Smart toys, baby monitors"},
}

# ---------------------------------------------------------------------------
# 2. Factor Weights — Table 6 (fixed, evidence-derived, not user-tunable)
# ---------------------------------------------------------------------------
FACTOR_WEIGHTS: Dict[str, float] = {
    "DV": 0.30,  # Device Vulnerability
    "DS": 0.25,  # Data Sensitivity
    "NE": 0.20,  # Network Exposure
    "UB": 0.15,  # User Behaviour
    "CS": 0.10,  # Compliance Status
}
assert abs(sum(FACTOR_WEIGHTS.values()) - 1.0) < 1e-9

# ---------------------------------------------------------------------------
# 3. Evidence Traceability — Table 5 / Table 6
# ---------------------------------------------------------------------------
TRACEABILITY: Dict[str, str] = {
    "DV": "Ali & Awad (2018) — device-tier vulnerabilities most prevalent across household IoT categories",
    "DS": "Aldahmani et al. (2023); Emami-Naeini et al. (2021) — sensitivity determines breach impact severity",
    "NE": "Aldahmani et al. (2023); Mahmoud et al. (2015) — encrypted traffic still leaks metadata; cloud connectivity compounds exposure",
    "UB": "Emami-Naeini et al. (2021, 2019) — default credential retention and update non-compliance are primary risk amplifiers",
    "CS": "Heartfield et al. (2018); Nurse et al. (2017) — ETSI EN 303 645 compliance correlates with baseline security posture",
    "Aggregation": "Nguyen et al. (2026a), Table 5 — aggregation amplifies risk non-linearly (weakest-link effect)",
}

# ---------------------------------------------------------------------------
# 4. Per-Factor Assessment Rubrics — Section 7.1
# ---------------------------------------------------------------------------
def assess_device_vulnerability(category: str, firmware_updated: bool,
                                 default_credentials: bool, device_age_years: float) -> int:
    """DV score (1-10). Higher = more vulnerable."""
    score = DEVICE_TAXONOMY[category]["baseline_dv"]
    if not firmware_updated:
        score += 2
    if default_credentials:
        score += 2
    if device_age_years > 3:
        score += 1
    return max(1, min(10, round(score)))


def assess_data_sensitivity(category: str, handles_biometric_or_health: bool,
                             handles_financial: bool) -> int:
    """DS score (1-10)."""
    score = DEVICE_TAXONOMY[category]["baseline_ds"]
    if handles_biometric_or_health:
        score += 2
    if handles_financial:
        score += 2
    return max(1, min(10, round(score)))


def assess_network_exposure(cloud_connected: bool, exposed_port_forwarding: bool,
                             uses_vpn_or_segmented_network: bool) -> int:
    """NE score (1-10)."""
    score = 3
    if cloud_connected:
        score += 3
    if exposed_port_forwarding:
        score += 3
    if uses_vpn_or_segmented_network:
        score -= 2
    return max(1, min(10, round(score)))


def assess_user_behaviour(changed_default_password: bool, updates_enabled: bool,
                           reuses_passwords: bool) -> int:
    """UB score (1-10). Higher = riskier behaviour."""
    score = 2
    if not changed_default_password:
        score += 4
    if not updates_enabled:
        score += 3
    if reuses_passwords:
        score += 2
    return max(1, min(10, round(score)))


def assess_compliance_status(etsi_303645_certified: bool,
                              vendor_discloses_vulnerabilities: bool) -> int:
    """CS score (1-10). Higher = worse compliance (riskier)."""
    score = 8
    if etsi_303645_certified:
        score -= 5
    if vendor_discloses_vulnerabilities:
        score -= 2
    return max(1, min(10, round(score)))


# ---------------------------------------------------------------------------
# 5. Scoring Engine — Section 7.1
# ---------------------------------------------------------------------------
def calculate_hars_score(dv: int, ds: int, ne: int, ub: int, cs: int) -> float:
    """HARS Score = (DV*0.30)+(DS*0.25)+(NE*0.20)+(UB*0.15)+(CS*0.10)"""
    return round(
        dv * FACTOR_WEIGHTS["DV"] + ds * FACTOR_WEIGHTS["DS"] +
        ne * FACTOR_WEIGHTS["NE"] + ub * FACTOR_WEIGHTS["UB"] +
        cs * FACTOR_WEIGHTS["CS"], 2
    )


def get_risk_tier(score: float) -> str:
    if score <= 3:
        return "Low"
    elif score <= 6:
        return "Moderate"
    elif score <= 8:
        return "High"
    return "Critical"


# ---------------------------------------------------------------------------
# 6. Output Layer — plain-language guidance
# ---------------------------------------------------------------------------
TIER_GUIDANCE: Dict[str, str] = {
    "Low": "Your household's smart devices show minimal risk. Continue routine "
           "practices: keep firmware updated and review device settings periodically.",
    "Moderate": "Some devices carry moderate risk. Change any default passwords, "
                "enable automatic updates, and review which devices connect to the internet directly.",
    "High": "Multiple devices show significant risk. Prioritise changing default "
            "credentials immediately, disable unnecessary remote/cloud access, and "
            "check for firmware updates on all flagged devices.",
    "Critical": "Immediate action recommended. One or more devices combine weak "
                "credentials, outdated firmware, and sensitive data handling. Isolate "
                "these devices on a separate network if possible and update or replace them.",
}


def get_guidance(tier: str) -> str:
    return TIER_GUIDANCE[tier]


# ---------------------------------------------------------------------------
# 7. Non-linear household aggregation — Week 2 refinement
# ---------------------------------------------------------------------------
def aggregate_scores(device_scores: List[float]) -> float:
    """Quadratic mean (RMS) — weights high-risk devices more than a simple mean."""
    return round(math.sqrt(sum(s ** 2 for s in device_scores) / len(device_scores)), 2)


def assess_device(d: Dict) -> Dict:
    """Run all five rubrics for a single device dict and return full result."""
    dv = assess_device_vulnerability(d["category"], d["firmware_updated"],
                                      d["default_credentials"], d["device_age_years"])
    ds = assess_data_sensitivity(d["category"], d["handles_biometric_or_health"],
                                  d["handles_financial"])
    ne = assess_network_exposure(d["cloud_connected"], d["exposed_port_forwarding"],
                                  d["uses_vpn_or_segmented_network"])
    ub = assess_user_behaviour(d["changed_default_password"], d["updates_enabled"],
                                d["reuses_passwords"])
    cs = assess_compliance_status(d["etsi_303645_certified"],
                                   d["vendor_discloses_vulnerabilities"])
    score = calculate_hars_score(dv, ds, ne, ub, cs)
    tier = get_risk_tier(score)
    return {"device": d["name"], "category": d["category"],
            "DV": dv, "DS": ds, "NE": ne, "UB": ub, "CS": cs,
            "score": score, "tier": tier}


def run_household_assessment(devices: List[Dict]) -> Dict:
    """Constellation-level scoring across all enrolled devices, using
    non-linear (RMS) aggregation with a weakest-link floor."""
    if not devices:
        raise ValueError("At least one device is required.")

    results = [assess_device(d) for d in devices]
    device_scores = [r["score"] for r in results]

    household_score = aggregate_scores(device_scores)
    household_tier = get_risk_tier(household_score)

    tier_order = ["Low", "Moderate", "High", "Critical"]
    has_critical_device = any(r["tier"] == "Critical" for r in results)
    floor_applied = False
    if has_critical_device and tier_order.index(household_tier) < tier_order.index("High"):
        household_tier = "High"
        floor_applied = True

    linear_mean_score = round(sum(device_scores) / len(device_scores), 2)

    return {
        "per_device": results,
        "household_score": household_score,
        "household_tier": household_tier,
        "guidance": get_guidance(household_tier),
        "linear_mean_score_for_comparison": linear_mean_score,
        "weakest_link_floor_applied": floor_applied,
    }
