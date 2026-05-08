import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import uuid
import hashlib
import time
from datetime import datetime, timedelta
import random
import copy

st.set_page_config(
    page_title="Decision Provenance & Replay Management",
    layout="wide",
    initial_sidebar_state="collapsed"
)

STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* { font-family: 'Inter', sans-serif; box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    background-color: #0a0e1a !important;
    color: #e8e8e8 !important;
}

.stApp { background: linear-gradient(135deg, #080c18 0%, #0d1226 50%, #080c18 100%) !important; }

section[data-testid="stSidebar"] { display: none !important; }

div[data-testid="stToolbar"] { display: none !important; }

header[data-testid="stHeader"] { display: none !important; }

.block-container { padding: 0 !important; max-width: 100% !important; }

.top-nav {
    background: linear-gradient(90deg, #0d1226 0%, #111827 50%, #0d1226 100%);
    border-bottom: 2px solid #c9a84c;
    padding: 0 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
    position: sticky;
    top: 0;
    z-index: 999;
    box-shadow: 0 4px 20px rgba(201,168,76,0.15);
}

.nav-brand {
    font-size: 1.1rem;
    font-weight: 800;
    color: #c9a84c;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.nav-subtitle {
    font-size: 0.65rem;
    color: #7a8099;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.nav-links { display: flex; gap: 0.25rem; }

.nav-user {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: #c9a84c;
    font-size: 0.85rem;
    font-weight: 600;
}

.page-hero {
    background: linear-gradient(135deg, #0d1226 0%, #141b2d 100%);
    border-bottom: 1px solid #1e2a3d;
    padding: 2rem 2.5rem;
}

.hero-title {
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
}

.hero-title span { color: #c9a84c; }

.hero-sub {
    color: #7a8099;
    font-size: 0.9rem;
    margin-top: 0.25rem;
}

.content-area { padding: 1.5rem 2.5rem; }

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.kpi-card {
    background: linear-gradient(135deg, #111827 0%, #141b2d 100%);
    border: 1px solid #1e2a3d;
    border-top: 3px solid #c9a84c;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
}

.kpi-card::after {
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 80px; height: 80px;
    background: radial-gradient(circle, rgba(201,168,76,0.08) 0%, transparent 70%);
    border-radius: 50%;
}

.kpi-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #7a8099;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
}

.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1;
}

.kpi-delta {
    font-size: 0.75rem;
    color: #22c55e;
    margin-top: 0.25rem;
    font-weight: 500;
}

.kpi-delta.neg { color: #ef4444; }

.card {
    background: linear-gradient(135deg, #111827 0%, #141b2d 100%);
    border: 1px solid #1e2a3d;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.25rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #1e2a3d;
}

.card-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.card-badge {
    background: rgba(201,168,76,0.15);
    color: #c9a84c;
    border: 1px solid rgba(201,168,76,0.3);
    border-radius: 4px;
    padding: 0.2rem 0.6rem;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.section-grid { display: grid; gap: 1rem; }

.two-col { grid-template-columns: 1fr 1fr; }
.three-col { grid-template-columns: 1fr 1fr 1fr; }
.six-four { grid-template-columns: 6fr 4fr; }
.four-six { grid-template-columns: 4fr 6fr; }
.seven-three { grid-template-columns: 7fr 3fr; }

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.status-approved { background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
.status-rejected { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
.status-pending { background: rgba(234,179,8,0.15); color: #eab308; border: 1px solid rgba(234,179,8,0.3); }
.status-review { background: rgba(59,130,246,0.15); color: #3b82f6; border: 1px solid rgba(59,130,246,0.3); }
.status-active { background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
.status-inactive { background: rgba(107,114,128,0.15); color: #6b7280; border: 1px solid rgba(107,114,128,0.3); }
.status-published { background: rgba(168,85,247,0.15); color: #a855f7; border: 1px solid rgba(168,85,247,0.3); }

.rule-card {
    background: #0d1226;
    border: 1px solid #1e2a3d;
    border-left: 3px solid #c9a84c;
    border-radius: 6px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}

.rule-name {
    font-weight: 700;
    color: #ffffff;
    font-size: 0.9rem;
}

.rule-meta {
    color: #7a8099;
    font-size: 0.75rem;
    margin-top: 0.25rem;
}

.timeline-item {
    display: flex;
    gap: 1rem;
    padding: 0.75rem 0;
    border-bottom: 1px solid #1e2a3d;
}

.timeline-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #c9a84c;
    margin-top: 5px;
    flex-shrink: 0;
    box-shadow: 0 0 8px rgba(201,168,76,0.5);
}

.timeline-content { flex: 1; }

.timeline-title {
    font-size: 0.82rem;
    font-weight: 600;
    color: #e8e8e8;
}

.timeline-time {
    font-size: 0.7rem;
    color: #7a8099;
    margin-top: 0.1rem;
}

.exec-step {
    background: #0d1226;
    border: 1px solid #1e2a3d;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.step-name { font-size: 0.82rem; font-weight: 600; color: #ffffff; }
.step-result-pass { color: #22c55e; font-size: 0.75rem; font-weight: 700; }
.step-result-fail { color: #ef4444; font-size: 0.75rem; font-weight: 700; }

.audit-row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
    align-items: center;
    padding: 0.7rem 0;
    border-bottom: 1px solid #1a2236;
    font-size: 0.8rem;
}

.audit-head {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #c9a84c;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #c9a84c;
    margin-bottom: 0.25rem;
}

.stButton button {
    background: linear-gradient(135deg, #c9a84c 0%, #a8873c 100%) !important;
    color: #0a0e1a !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    border-radius: 4px !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 12px rgba(201,168,76,0.25) !important;
}

.stButton button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(201,168,76,0.35) !important;
}

.stSelectbox > div > div {
    background: #0d1226 !important;
    border-color: #1e2a3d !important;
    color: #e8e8e8 !important;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #0d1226 !important;
    border-color: #1e2a3d !important;
    color: #e8e8e8 !important;
    border-radius: 4px !important;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #c9a84c !important;
    box-shadow: 0 0 0 1px #c9a84c !important;
}

.stSlider > div > div > div > div { background: #c9a84c !important; }

label { color: #9aa0b4 !important; font-size: 0.8rem !important; font-weight: 500 !important; }

.stDataFrame { border-radius: 6px; overflow: hidden; }

.stDataFrame > div { background: #0d1226 !important; }

.stTabs [data-baseweb="tab-list"] {
    background: #0d1226 !important;
    border-bottom: 2px solid #1e2a3d !important;
    gap: 0 !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #7a8099 !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    border-bottom: 2px solid transparent !important;
    padding: 0.75rem 1.5rem !important;
    transition: all 0.2s !important;
}

.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #c9a84c !important;
    border-bottom: 2px solid #c9a84c !important;
}

div[data-testid="stMetric"] {
    background: #111827 !important;
    border: 1px solid #1e2a3d !important;
    border-radius: 8px !important;
    padding: 1rem !important;
}

div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.8rem !important; }
div[data-testid="stMetricLabel"] { color: #7a8099 !important; }
div[data-testid="stMetricDelta"] { color: #22c55e !important; }

.stAlert { border-radius: 6px !important; }

div[data-testid="column"] { padding: 0 0.5rem !important; }

.stRadio > div { gap: 0.5rem !important; }

.stRadio label {
    background: #111827 !important;
    border: 1px solid #1e2a3d !important;
    border-radius: 4px !important;
    padding: 0.5rem 1rem !important;
    cursor: pointer !important;
    color: #9aa0b4 !important;
    font-size: 0.8rem !important;
}

.progress-bar-bg {
    background: #1e2a3d;
    border-radius: 4px;
    height: 8px;
    overflow: hidden;
}

.progress-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, #c9a84c, #e8c97a);
}

.risk-meter {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

.risk-segment {
    flex: 1;
    height: 6px;
    border-radius: 3px;
}

.login-wrapper {
    min-height: 100vh;
    background: linear-gradient(135deg, #080c18 0%, #0d1226 50%, #080c18 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.login-card {
    background: linear-gradient(135deg, #111827 0%, #141b2d 100%);
    border: 1px solid #c9a84c;
    border-top: 4px solid #c9a84c;
    border-radius: 12px;
    padding: 3rem 2.5rem;
    width: 100%;
    max-width: 440px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(201,168,76,0.1);
}

.login-brand {
    text-align: center;
    margin-bottom: 2rem;
}

.login-logo-text {
    font-size: 2rem;
    font-weight: 900;
    color: #c9a84c;
    letter-spacing: 3px;
    text-transform: uppercase;
}

.login-tagline {
    font-size: 0.7rem;
    color: #7a8099;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 0.25rem;
}

.login-divider {
    border: none;
    border-top: 1px solid #1e2a3d;
    margin: 1.5rem 0;
}

.field-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #7a8099;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.35rem;
}

.reg-card {
    background: linear-gradient(135deg, #111827 0%, #141b2d 100%);
    border: 1px solid #1e2a3d;
    border-top: 4px solid #c9a84c;
    border-radius: 12px;
    padding: 2.5rem 2.5rem;
    width: 100%;
    max-width: 520px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}

.nav-btn {
    background: transparent;
    border: 1px solid #1e2a3d;
    color: #9aa0b4;
    padding: 0.4rem 1rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: all 0.2s;
    margin: 0 0.15rem;
}

.nav-btn.active {
    background: rgba(201,168,76,0.15);
    border-color: #c9a84c;
    color: #c9a84c;
}

.comparison-diff {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.2);
    border-radius: 4px;
    padding: 0.5rem 0.75rem;
    font-size: 0.78rem;
    color: #ef4444;
    margin-bottom: 0.4rem;
}

.comparison-same {
    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.2);
    border-radius: 4px;
    padding: 0.5rem 0.75rem;
    font-size: 0.78rem;
    color: #22c55e;
    margin-bottom: 0.4rem;
}

.metric-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.6rem 0;
    border-bottom: 1px solid #1a2236;
    font-size: 0.8rem;
}

.metric-row:last-child { border-bottom: none; }
.metric-row-key { color: #9aa0b4; }
.metric-row-val { color: #ffffff; font-weight: 600; }

.stCheckbox label { color: #9aa0b4 !important; }
.stCheckbox { margin-bottom: 0.25rem; }

div[data-testid="stExpander"] {
    background: #111827 !important;
    border: 1px solid #1e2a3d !important;
    border-radius: 6px !important;
}

summary { color: #c9a84c !important; font-weight: 600 !important; font-size: 0.85rem !important; }

.score-ring-label {
    text-align: center;
    font-size: 0.7rem;
    color: #7a8099;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.25rem;
}

hr { border-color: #1e2a3d !important; }

.sparkline-mini { height: 40px; }

.action-bar {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    flex-wrap: wrap;
    padding: 0.75rem 0;
}

.replay-badge {
    background: rgba(168,85,247,0.15);
    border: 1px solid rgba(168,85,247,0.3);
    color: #a855f7;
    border-radius: 4px;
    padding: 0.2rem 0.5rem;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.tag {
    background: rgba(59,130,246,0.15);
    border: 1px solid rgba(59,130,246,0.3);
    color: #3b82f6;
    border-radius: 3px;
    padding: 0.15rem 0.4rem;
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-left: 0.3rem;
}

.stForm { background: transparent !important; }
.stForm > div { background: transparent !important; }

[data-testid="stFormSubmitButton"] button {
    width: 100%;
    background: linear-gradient(135deg, #c9a84c 0%, #a8873c 100%) !important;
    color: #0a0e1a !important;
    font-weight: 800 !important;
    font-size: 0.85rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 0.75rem !important;
    border-radius: 4px !important;
}
</style>
"""

def init_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "dashboard"
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "users" not in st.session_state:
        st.session_state.users = {
            "analyst@dprs.com": {"name": "Divyasri Burugula", "role": "Decision Analyst", "password": hashlib.sha256("analyst123".encode()).hexdigest(), "active": True, "id": "U001", "permissions": ["create_rule","publish_workflow","execute","audit","admin"]},
            "auditor@dprs.com": {"name": "Alex Monroe", "role": "Auditor", "password": hashlib.sha256("auditor123".encode()).hexdigest(), "active": True, "id": "U002", "permissions": ["audit","replay","compare","export"]},
            "business@dprs.com": {"name": "Jordan Lee", "role": "Business User", "password": hashlib.sha256("business123".encode()).hexdigest(), "active": True, "id": "U003", "permissions": ["execute","view"]},
            "admin@dprs.com": {"name": "System Admin", "role": "Administrator", "password": hashlib.sha256("admin123".encode()).hexdigest(), "active": True, "id": "U004", "permissions": ["create_rule","publish_workflow","execute","audit","replay","compare","export","admin","manage_users"]},
        }
    if "rules" not in st.session_state:
        st.session_state.rules = _seed_rules()
    if "workflows" not in st.session_state:
        st.session_state.workflows = _seed_workflows()
    if "executions" not in st.session_state:
        st.session_state.executions = _seed_executions()
    if "audit_log" not in st.session_state:
        st.session_state.audit_log = _seed_audit_log()

def _seed_rules():
    categories = ["Credit", "Income", "Employment", "Risk", "Compliance", "Identity"]
    rules = []
    rule_defs = [
        ("Minimum Credit Score", "Credit", "credit_score", ">=", 650, "Applicant credit score must meet minimum threshold"),
        ("Maximum Debt-to-Income Ratio", "Income", "debt_to_income", "<=", 0.43, "DTI ratio must not exceed 43%"),
        ("Employment Stability Check", "Employment", "employment_years", ">=", 2, "Minimum 2 years continuous employment"),
        ("Annual Income Threshold", "Income", "annual_income", ">=", 35000, "Annual gross income minimum requirement"),
        ("Loan-to-Income Ratio", "Income", "loan_to_income", "<=", 4.0, "Loan amount must not exceed 4x annual income"),
        ("No Recent Bankruptcies", "Credit", "bankruptcies_last_5yr", "==", 0, "No bankruptcies within last 5 years"),
        ("Active Account Count", "Credit", "active_accounts", ">=", 2, "Minimum 2 active credit accounts required"),
        ("Income Verification Status", "Compliance", "income_verified", "==", True, "Income must be formally verified"),
        ("Age of Credit History", "Credit", "credit_history_years", ">=", 3, "Minimum 3 years credit history required"),
        ("Late Payment Check", "Credit", "late_payments_12mo", "<=", 1, "No more than 1 late payment in last 12 months"),
        ("Property Appraisal", "Compliance", "appraisal_complete", "==", True, "Property appraisal must be completed"),
        ("Identity Verification", "Identity", "identity_verified", "==", True, "Applicant identity must be verified"),
        ("Risk Category Assessment", "Risk", "risk_score", "<=", 70, "Internal risk score must be below 70"),
        ("Collateral Coverage", "Risk", "collateral_ratio", ">=", 1.2, "Collateral must cover at least 120% of loan"),
        ("Geographic Compliance", "Compliance", "region_approved", "==", True, "Applicant must be in approved region"),
        ("Prior Loan Performance", "Credit", "prior_default", "==", False, "No prior loan defaults on record"),
        ("Monthly Payment Feasibility", "Income", "monthly_payment_ratio", "<=", 0.35, "Monthly payment must be under 35% of monthly income"),
        ("Employment Type Check", "Employment", "employment_type", "in", ["fulltime","contract"], "Employment type must be fulltime or contract"),
    ]
    for i, (name, cat, field, op, threshold, desc) in enumerate(rule_defs):
        version_history = []
        n_versions = random.randint(1, 3)
        for v in range(1, n_versions + 1):
            version_history.append({
                "version": f"v{v}.0",
                "threshold": threshold if v == n_versions else (threshold * random.uniform(0.85, 0.95) if isinstance(threshold, (int, float)) else threshold),
                "created_at": (datetime.now() - timedelta(days=random.randint(30, 400))).strftime("%Y-%m-%d %H:%M"),
                "created_by": "analyst@dprs.com",
                "change_notes": f"Version {v} adjustment" if v > 1 else "Initial version"
            })
        rules.append({
            "id": f"R{str(i+1).zfill(3)}",
            "name": name,
            "category": cat,
            "field": field,
            "operator": op,
            "threshold": threshold,
            "description": desc,
            "active": True,
            "current_version": f"v{n_versions}.0",
            "version_history": version_history,
            "created_at": (datetime.now() - timedelta(days=random.randint(30, 400))).strftime("%Y-%m-%d %H:%M"),
            "created_by": "analyst@dprs.com",
            "pass_count": random.randint(50, 300),
            "fail_count": random.randint(10, 80),
        })
    return rules

def _seed_workflows():
    base_rules = ["R001","R002","R003","R004","R005","R006","R007","R008","R009","R010"]
    workflows = [
        {
            "id": "WF001",
            "name": "Standard Loan Eligibility",
            "description": "Primary credit decision workflow for standard loan applications",
            "status": "published",
            "current_version": "v3.0",
            "rule_ids": ["R001","R002","R003","R004","R005","R006","R007","R008","R009","R010","R011","R012"],
            "created_at": (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d %H:%M"),
            "published_at": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M"),
            "created_by": "analyst@dprs.com",
            "approval_required": True,
            "approved_by": "admin@dprs.com",
            "executions": random.randint(80, 200),
            "version_history": [
                {"version": "v1.0", "date": (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"), "notes": "Initial release"},
                {"version": "v2.0", "date": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"), "notes": "Added income verification"},
                {"version": "v3.0", "date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"), "notes": "Updated credit thresholds"},
            ]
        },
        {
            "id": "WF002",
            "name": "Fast Track Credit Assessment",
            "description": "Expedited workflow for pre-qualified applicants",
            "status": "published",
            "current_version": "v2.0",
            "rule_ids": ["R001","R003","R004","R008","R012","R013"],
            "created_at": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d %H:%M"),
            "published_at": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M"),
            "created_by": "analyst@dprs.com",
            "approval_required": False,
            "approved_by": None,
            "executions": random.randint(30, 100),
            "version_history": [
                {"version": "v1.0", "date": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"), "notes": "Initial fast-track workflow"},
                {"version": "v2.0", "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"), "notes": "Streamlined rule set"},
            ]
        },
        {
            "id": "WF003",
            "name": "High-Risk Applicant Review",
            "description": "Enhanced due-diligence workflow for flagged applicants",
            "status": "draft",
            "current_version": "v1.0",
            "rule_ids": ["R001","R002","R003","R004","R005","R006","R007","R008","R009","R010","R011","R012","R013","R014","R015","R016","R017","R018"],
            "created_at": (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d %H:%M"),
            "published_at": None,
            "created_by": "analyst@dprs.com",
            "approval_required": True,
            "approved_by": None,
            "executions": 0,
            "version_history": [
                {"version": "v1.0", "date": (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d"), "notes": "Draft - pending review"},
            ]
        },
        {
            "id": "WF004",
            "name": "Commercial Loan Eligibility",
            "description": "Workflow for commercial and business loan applications",
            "status": "published",
            "current_version": "v1.5",
            "rule_ids": ["R001","R002","R004","R008","R009","R012","R013","R014"],
            "created_at": (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d %H:%M"),
            "published_at": (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d %H:%M"),
            "created_by": "analyst@dprs.com",
            "approval_required": True,
            "approved_by": "admin@dprs.com",
            "executions": random.randint(20, 60),
            "version_history": [
                {"version": "v1.0", "date": (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d"), "notes": "Initial commercial workflow"},
                {"version": "v1.5", "date": (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"), "notes": "Adjusted collateral rules"},
            ]
        },
    ]
    return workflows

def _make_applicant():
    credit_score = random.randint(580, 800)
    annual_income = random.randint(28000, 120000)
    loan_amount = random.randint(10000, 500000)
    return {
        "credit_score": credit_score,
        "debt_to_income": round(random.uniform(0.15, 0.55), 2),
        "employment_years": random.randint(0, 15),
        "annual_income": annual_income,
        "loan_to_income": round(loan_amount / max(annual_income, 1), 2),
        "bankruptcies_last_5yr": random.choices([0, 1, 2], weights=[80, 15, 5])[0],
        "active_accounts": random.randint(0, 8),
        "income_verified": random.choices([True, False], weights=[85, 15])[0],
        "credit_history_years": random.randint(0, 20),
        "late_payments_12mo": random.choices([0, 1, 2, 3], weights=[60, 25, 10, 5])[0],
        "appraisal_complete": random.choices([True, False], weights=[80, 20])[0],
        "identity_verified": random.choices([True, False], weights=[90, 10])[0],
        "risk_score": random.randint(20, 95),
        "collateral_ratio": round(random.uniform(0.8, 2.5), 2),
        "region_approved": random.choices([True, False], weights=[88, 12])[0],
        "prior_default": random.choices([False, True], weights=[85, 15])[0],
        "monthly_payment_ratio": round(random.uniform(0.15, 0.55), 2),
        "employment_type": random.choice(["fulltime", "parttime", "contract", "self-employed"]),
    }

def _evaluate_rule(rule, data):
    field = rule["field"]
    op = rule["operator"]
    threshold = rule["threshold"]
    value = data.get(field)
    if value is None:
        return False, "Field not found"
    try:
        if op == ">=":
            passed = value >= threshold
        elif op == "<=":
            passed = value <= threshold
        elif op == "==":
            passed = value == threshold
        elif op == "!=":
            passed = value != threshold
        elif op == ">":
            passed = value > threshold
        elif op == "<":
            passed = value < threshold
        elif op == "in":
            passed = value in threshold
        else:
            passed = False
        reason = f"{field}={value} {op} {threshold}"
        return passed, reason
    except:
        return False, "Evaluation error"

def _execute_workflow(workflow, applicant_data):
    rule_results = []
    rules_map = {r["id"]: r for r in st.session_state.rules}
    all_pass = True
    for rid in workflow["rule_ids"]:
        rule = rules_map.get(rid)
        if not rule or not rule["active"]:
            continue
        passed, reason = _evaluate_rule(rule, applicant_data)
        if not passed:
            all_pass = False
        rule_results.append({
            "rule_id": rid,
            "rule_name": rule["name"],
            "category": rule["category"],
            "version": rule["current_version"],
            "passed": passed,
            "reason": reason,
            "field": rule["field"],
            "operator": rule["operator"],
            "threshold": rule["threshold"],
            "actual_value": applicant_data.get(rule["field"]),
        })
    overall = "APPROVED" if all_pass else "REJECTED"
    passed_count = sum(1 for r in rule_results if r["passed"])
    approval_score = round((passed_count / max(len(rule_results), 1)) * 100, 1)
    return overall, rule_results, approval_score

def _seed_executions():
    executions = []
    names = ["Alex Carter","Maria Santos","James Wu","Priya Patel","Kevin Nguyen","Sarah Johnson","David Kim","Linda Chen","Robert Taylor","Aisha Williams","Michael Brown","Emma Davis","Carlos Rivera","Fatima Al-Rashid","Liam Patel","Zoe Hernandez","Noah Smith","Isabella Jones","Oliver Martin","Sophia White"]
    for i in range(40):
        app_data = _make_applicant()
        wf = random.choice(["WF001","WF002","WF004"])
        wf_obj = next((w for w in _seed_workflows() if w["id"] == wf), _seed_workflows()[0])
        rules_map = {r["id"]: r for r in _seed_rules()}
        rule_results = []
        all_pass = True
        for rid in wf_obj["rule_ids"]:
            rule = rules_map.get(rid)
            if not rule:
                continue
            passed, reason = _evaluate_rule(rule, app_data)
            if not passed:
                all_pass = False
            rule_results.append({
                "rule_id": rid,
                "rule_name": rule["name"],
                "category": rule["category"],
                "version": rule["current_version"],
                "passed": passed,
                "reason": reason,
                "field": rule["field"],
                "operator": rule["operator"],
                "threshold": rule["threshold"],
                "actual_value": app_data.get(rule["field"]),
            })
        overall = "APPROVED" if all_pass else "REJECTED"
        passed_count = sum(1 for r in rule_results if r["passed"])
        approval_score = round((passed_count / max(len(rule_results), 1)) * 100, 1)
        scenario = random.choice(["production","test","exception"])
        dt = datetime.now() - timedelta(days=random.randint(0, 90), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        executions.append({
            "id": f"EX{str(i+1).zfill(4)}",
            "applicant_name": random.choice(names),
            "workflow_id": wf,
            "workflow_version": wf_obj["current_version"],
            "outcome": overall,
            "approval_score": approval_score,
            "applicant_data": app_data,
            "rule_results": rule_results,
            "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "executed_by": random.choice(["analyst@dprs.com","business@dprs.com"]),
            "scenario_type": scenario,
            "replayed": random.choice([True, False, False]),
            "immutable": True,
        })
    executions.sort(key=lambda x: x["timestamp"], reverse=True)
    return executions

def _seed_audit_log():
    logs = []
    actions = [
        ("Rule Created", "R005", "analyst@dprs.com"),
        ("Rule Versioned", "R001", "analyst@dprs.com"),
        ("Workflow Published", "WF001", "analyst@dprs.com"),
        ("Decision Executed", "EX0001", "business@dprs.com"),
        ("Audit Query", "EX0012", "auditor@dprs.com"),
        ("Replay Executed", "EX0008", "auditor@dprs.com"),
        ("User Created", "U003", "admin@dprs.com"),
        ("Permission Modified", "U002", "admin@dprs.com"),
        ("Workflow Cloned", "WF002", "analyst@dprs.com"),
        ("Rule Deactivated", "R006", "analyst@dprs.com"),
        ("Export Generated", "EX0015-EX0030", "auditor@dprs.com"),
        ("Comparison Run", "EX0005 vs EX0021", "auditor@dprs.com"),
    ]
    for i, (action, target, user) in enumerate(actions * 3):
        dt = datetime.now() - timedelta(hours=random.randint(1, 720))
        logs.append({
            "id": f"LOG{str(i+1).zfill(4)}",
            "action": action,
            "target": target,
            "user": user,
            "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "ip": f"192.168.{random.randint(1,10)}.{random.randint(1,254)}",
        })
    logs.sort(key=lambda x: x["timestamp"], reverse=True)
    return logs[:30]

def make_gauge(value, title, max_val=100, color="#c9a84c"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": title, "font": {"size": 12, "color": "#9aa0b4"}},
        number={"font": {"size": 28, "color": "#ffffff"}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": "#1e2a3d", "tickfont": {"size": 9, "color": "#7a8099"}},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "#0d1226",
            "borderwidth": 1,
            "bordercolor": "#1e2a3d",
            "steps": [
                {"range": [0, max_val * 0.33], "color": "#1a0e0e"},
                {"range": [max_val * 0.33, max_val * 0.66], "color": "#1a1a0e"},
                {"range": [max_val * 0.66, max_val], "color": "#0e1a0e"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.8, "value": value},
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=200,
        margin=dict(l=20, r=20, t=30, b=10),
        font={"family": "Inter"},
    )
    return fig

def make_donut(labels, values, title=""):
    colors = ["#c9a84c", "#22c55e", "#ef4444", "#3b82f6", "#a855f7", "#f97316"]
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.6,
        marker={"colors": colors[:len(values)], "line": {"color": "#0d1226", "width": 2}},
        textfont={"size": 10, "color": "#ffffff"},
        hovertemplate="<b>%{label}</b><br>%{value} (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=220,
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=True,
        legend={"font": {"color": "#9aa0b4", "size": 9}, "bgcolor": "rgba(0,0,0,0)"},
        annotations=[{"text": title, "font": {"size": 11, "color": "#c9a84c"}, "showarrow": False}],
        font={"family": "Inter"},
    )
    return fig

def make_bar(x, y, title="", color="#c9a84c", horizontal=False):
    if horizontal:
        fig = go.Figure(go.Bar(x=y, y=x, orientation="h", marker_color=color, marker_line_width=0))
    else:
        fig = go.Figure(go.Bar(x=x, y=y, marker_color=color, marker_line_width=0))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=220,
        margin=dict(l=10, r=10, t=30, b=30),
        title={"text": title, "font": {"size": 11, "color": "#9aa0b4"}, "x": 0},
        xaxis={"gridcolor": "#1e2a3d", "tickfont": {"color": "#7a8099", "size": 9}},
        yaxis={"gridcolor": "#1e2a3d", "tickfont": {"color": "#7a8099", "size": 9}},
        font={"family": "Inter"},
    )
    return fig

def make_line(x, y_dict, title=""):
    colors_list = ["#c9a84c", "#22c55e", "#3b82f6", "#ef4444", "#a855f7"]
    fig = go.Figure()
    for i, (name, vals) in enumerate(y_dict.items()):
        fig.add_trace(go.Scatter(x=x, y=vals, name=name, mode="lines+markers",
                                  line={"color": colors_list[i % len(colors_list)], "width": 2},
                                  marker={"size": 4}, hovertemplate=f"<b>{name}</b><br>%{{y}}<extra></extra>"))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=240,
        margin=dict(l=10, r=10, t=30, b=30),
        title={"text": title, "font": {"size": 11, "color": "#9aa0b4"}, "x": 0},
        xaxis={"gridcolor": "#1e2a3d", "tickfont": {"color": "#7a8099", "size": 9}},
        yaxis={"gridcolor": "#1e2a3d", "tickfont": {"color": "#7a8099", "size": 9}},
        legend={"font": {"color": "#9aa0b4", "size": 9}, "bgcolor": "rgba(0,0,0,0)"},
        font={"family": "Inter"},
    )
    return fig

def make_scatter_3d(executions):
    data = executions[:80]
    xs = [e["applicant_data"].get("credit_score", 650) for e in data]
    ys = [e["applicant_data"].get("annual_income", 50000) / 1000 for e in data]
    zs = [e["approval_score"] for e in data]
    colors = ["#22c55e" if e["outcome"] == "APPROVED" else "#ef4444" for e in data]
    fig = go.Figure(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="markers",
        marker=dict(size=5, color=colors, opacity=0.8, line=dict(width=0)),
        hovertemplate="Credit: %{x}<br>Income: %{y}K<br>Score: %{z}%<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=380,
        margin=dict(l=0, r=0, t=30, b=0),
        scene=dict(
            bgcolor="rgba(13,18,38,0.8)",
            xaxis=dict(title="Credit Score", gridcolor="#1e2a3d", tickfont=dict(color="#7a8099", size=8)),
            yaxis=dict(title="Income (K)", gridcolor="#1e2a3d", tickfont=dict(color="#7a8099", size=8)),
            zaxis=dict(title="Approval %", gridcolor="#1e2a3d", tickfont=dict(color="#7a8099", size=8)),
        ),
        title={"text": "3D Decision Space — Credit / Income / Approval Score", "font": {"size": 11, "color": "#9aa0b4"}},
        font={"family": "Inter"},
    )
    return fig

def make_heatmap(executions):
    cats = ["Credit","Income","Employment","Risk","Compliance","Identity"]
    rules_map = {r["id"]: r for r in st.session_state.rules}
    pass_rates = {}
    for c in cats:
        total = fail = 0
        for ex in executions:
            for rr in ex["rule_results"]:
                rid = rr["rule_id"]
                rule = rules_map.get(rid)
                if rule and rule["category"] == c:
                    total += 1
                    if not rr["passed"]:
                        fail += 1
        pass_rates[c] = round(100 - (fail / max(total, 1)) * 100, 1)
    weeks = [f"Wk{i}" for i in range(1, 9)]
    z = [[pass_rates.get(c, 70) + random.uniform(-10, 10) for _ in weeks] for c in cats]
    fig = go.Figure(go.Heatmap(
        z=z, x=weeks, y=cats,
        colorscale=[[0, "#1a0e0e"], [0.5, "#c9a84c"], [1, "#22c55e"]],
        zmin=50, zmax=100,
        hovertemplate="Category: %{y}<br>Week: %{x}<br>Pass Rate: %{z:.1f}%<extra></extra>",
        colorbar=dict(tickfont=dict(color="#9aa0b4", size=9), thickness=12, len=0.8),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=250,
        margin=dict(l=10, r=60, t=20, b=30),
        xaxis={"tickfont": {"color": "#7a8099", "size": 9}},
        yaxis={"tickfont": {"color": "#7a8099", "size": 9}},
        font={"family": "Inter"},
    )
    return fig

def make_waterfall(rule_results):
    names = [r["rule_name"][:22] for r in rule_results]
    values = [1 if r["passed"] else -1 for r in rule_results]
    colors = ["#22c55e" if v > 0 else "#ef4444" for v in values]
    running = 0
    bases = []
    for v in values:
        bases.append(running)
        running += v
    fig = go.Figure(go.Bar(
        x=names, y=values, base=bases,
        marker_color=colors, marker_line_width=0,
        hovertemplate="%{x}<br>%{customdata}<extra></extra>",
        customdata=["PASS" if v > 0 else "FAIL" for v in values],
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=220,
        margin=dict(l=10, r=10, t=10, b=80),
        xaxis={"gridcolor": "#1e2a3d", "tickfont": {"color": "#7a8099", "size": 8}, "tickangle": -35},
        yaxis={"gridcolor": "#1e2a3d", "tickfont": {"color": "#7a8099", "size": 9}},
        font={"family": "Inter"},
    )
    return fig

def make_radar(rule_results):
    cats = ["Credit","Income","Employment","Risk","Compliance","Identity"]
    scores = {}
    for c in cats:
        matching = [r for r in rule_results if True]
        scores[c] = random.uniform(0.5, 1.0)
    for rr in rule_results:
        pass

    category_scores = {c: [] for c in cats}
    for rr in rule_results:
        for c in cats:
            pass
    cs = {c: random.uniform(40, 100) for c in cats}
    vals = list(cs.values()) + [list(cs.values())[0]]
    labels = cats + [cats[0]]
    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=labels,
        fill="toself",
        fillcolor="rgba(201,168,76,0.15)",
        line=dict(color="#c9a84c", width=2),
        marker=dict(color="#c9a84c", size=5),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            bgcolor="rgba(13,18,38,0.6)",
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=8, color="#7a8099"), gridcolor="#1e2a3d"),
            angularaxis=dict(tickfont=dict(size=9, color="#9aa0b4"), gridcolor="#1e2a3d"),
        ),
        height=220,
        margin=dict(l=30, r=30, t=20, b=20),
        font={"family": "Inter"},
    )
    return fig

def render_nav():
    tabs = [
        ("dashboard", "Dashboard"),
        ("rules", "Rule Management"),
        ("workflows", "Workflows"),
        ("execute", "Execute Decision"),
        ("history", "Decision History"),
        ("replay", "Replay & Compare"),
        ("audit", "Audit Trail"),
        ("admin", "Administration"),
    ]
    user = st.session_state.current_user
    role = user.get("role", "") if user else ""
    st.markdown(f"""
    <div class="top-nav">
        <div>
            <div class="nav-brand">DPRS</div>
            <div class="nav-subtitle">Decision Provenance & Replay</div>
        </div>
        <div class="nav-links" id="navlinks"></div>
        <div class="nav-user">
            <div style="text-align:right">
                <div style="font-size:0.82rem;color:#e8e8e8">{user['name'] if user else ''}</div>
                <div style="font-size:0.68rem;color:#c9a84c;text-transform:uppercase;letter-spacing:1px">{role}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    cols = st.columns(len(tabs))
    for i, (key, label) in enumerate(tabs):
        with cols[i]:
            active = st.session_state.active_tab == key
            btn_style = "background:rgba(201,168,76,0.15);border:1px solid #c9a84c;color:#c9a84c;" if active else "background:transparent;border:1px solid #1e2a3d;color:#7a8099;"
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.active_tab = key
                st.rerun()

def page_dashboard():
    executions = st.session_state.executions
    rules = st.session_state.rules
    workflows = st.session_state.workflows
    approved = [e for e in executions if e["outcome"] == "APPROVED"]
    rejected = [e for e in executions if e["outcome"] == "REJECTED"]
    approval_rate = round(len(approved) / max(len(executions), 1) * 100, 1)
    avg_score = round(sum(e["approval_score"] for e in executions) / max(len(executions), 1), 1)

    st.markdown('<div class="page-hero">', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Decision Intelligence <span>Dashboard</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Real-time overview of decision provenance, rule performance, and workflow analytics</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="content-area">', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Total Executions</div>
            <div class="kpi-value">{len(executions)}</div>
            <div class="kpi-delta">+12 this week</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Approval Rate</div>
            <div class="kpi-value">{approval_rate}%</div>
            <div class="kpi-delta">+2.3% vs last month</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Active Rules</div>
            <div class="kpi-value">{sum(1 for r in rules if r['active'])}</div>
            <div class="kpi-delta">{len(rules)} total rules</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Published Workflows</div>
            <div class="kpi-value">{sum(1 for w in workflows if w['status']=='published')}</div>
            <div class="kpi-delta">{len(workflows)} total workflows</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([4, 3, 3])
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Decision Trends — 12 Weeks</div><span class="card-badge">Live</span></div>', unsafe_allow_html=True)
        weeks = [f"W{i}" for i in range(1, 13)]
        approved_vals = [random.randint(8, 20) for _ in weeks]
        rejected_vals = [random.randint(2, 8) for _ in weeks]
        st.plotly_chart(make_line(weeks, {"Approved": approved_vals, "Rejected": rejected_vals}, ""), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Outcome Distribution</div></div>', unsafe_allow_html=True)
        st.plotly_chart(make_donut(["Approved", "Rejected"], [len(approved), len(rejected)], f"{approval_rate}%"), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Scenario Types</div></div>', unsafe_allow_html=True)
        sc = {}
        for e in executions:
            sc[e["scenario_type"]] = sc.get(e["scenario_type"], 0) + 1
        st.plotly_chart(make_donut(list(sc.keys()), list(sc.values()), "Type"), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    c4, c5 = st.columns([5, 5])
    with c4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Rule Category Pass Rates — Heatmap</div></div>', unsafe_allow_html=True)
        st.plotly_chart(make_heatmap(executions), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c5:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Rule Failure Frequency</div></div>', unsafe_allow_html=True)
        rule_fails = {}
        for ex in executions:
            for rr in ex["rule_results"]:
                if not rr["passed"]:
                    rule_fails[rr["rule_name"][:20]] = rule_fails.get(rr["rule_name"][:20], 0) + 1
        sorted_fails = sorted(rule_fails.items(), key=lambda x: x[1], reverse=True)[:8]
        if sorted_fails:
            names_f, counts_f = zip(*sorted_fails)
            st.plotly_chart(make_bar(list(names_f), list(counts_f), color="#ef4444", horizontal=True), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header"><div class="card-title">3D Decision Space Visualization</div><span class="card-badge">Interactive</span></div>', unsafe_allow_html=True)
    st.plotly_chart(make_scatter_3d(executions), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    c6, c7 = st.columns([5, 5])
    with c6:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Approval Score Distribution</div></div>', unsafe_allow_html=True)
        scores = [e["approval_score"] for e in executions]
        bins = list(range(0, 110, 10))
        hist_vals = [sum(1 for s in scores if bins[i] <= s < bins[i+1]) for i in range(len(bins)-1)]
        st.plotly_chart(make_bar([f"{bins[i]}-{bins[i+1]}" for i in range(len(bins)-1)], hist_vals, color="#c9a84c"), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c7:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Workflow Execution Volume</div></div>', unsafe_allow_html=True)
        wf_names = [w["name"][:25] for w in st.session_state.workflows]
        wf_counts = [w["executions"] for w in st.session_state.workflows]
        st.plotly_chart(make_bar(wf_names, wf_counts, color="#3b82f6"), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    c8, c9 = st.columns([4, 6])
    with c8:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Average Approval Score</div></div>', unsafe_allow_html=True)
        st.plotly_chart(make_gauge(avg_score, "Avg Approval Score", 100, "#c9a84c"), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c9:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Recent Executions</div><span class="card-badge">Latest 8</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="audit-row audit-head"><span>Applicant</span><span>Workflow</span><span>Outcome</span><span>Score</span><span>Time</span></div>', unsafe_allow_html=True)
        for ex in executions[:8]:
            wf = next((w for w in workflows if w["id"] == ex["workflow_id"]), None)
            wf_name = wf["name"][:22] if wf else ex["workflow_id"]
            badge_cls = "status-approved" if ex["outcome"] == "APPROVED" else "status-rejected"
            st.markdown(f"""
            <div class="audit-row">
                <span style="color:#e8e8e8;font-weight:600">{ex['applicant_name']}</span>
                <span style="color:#9aa0b4">{wf_name}</span>
                <span><span class="status-badge {badge_cls}">{ex['outcome']}</span></span>
                <span style="color:#c9a84c;font-weight:700">{ex['approval_score']}%</span>
                <span style="color:#7a8099">{ex['timestamp'][11:16]}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def page_rules():
    rules = st.session_state.rules
    st.markdown('<div class="page-hero"><div class="hero-title">Rule <span>Management</span></div><div class="hero-sub">Define, version, and manage decision business rules</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="content-area">', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Rule Library", "Create New Rule", "Rule Analytics"])

    with tab1:
        categories = ["All"] + list(set(r["category"] for r in rules))
        fc1, fc2, fc3 = st.columns([3, 2, 2])
        with fc1:
            search = st.text_input("Search rules", placeholder="Search by name or description...")
        with fc2:
            cat_filter = st.selectbox("Category", categories)
        with fc3:
            status_filter = st.selectbox("Status", ["All", "Active", "Inactive"])

        filtered = rules
        if search:
            filtered = [r for r in filtered if search.lower() in r["name"].lower() or search.lower() in r["description"].lower()]
        if cat_filter != "All":
            filtered = [r for r in filtered if r["category"] == cat_filter]
        if status_filter == "Active":
            filtered = [r for r in filtered if r["active"]]
        elif status_filter == "Inactive":
            filtered = [r for r in filtered if not r["active"]]

        st.markdown(f"<div style='color:#7a8099;font-size:0.78rem;margin-bottom:0.75rem'>{len(filtered)} rules found</div>", unsafe_allow_html=True)

        for rule in filtered:
            status_cls = "status-active" if rule["active"] else "status-inactive"
            pass_rate = round(rule["pass_count"] / max(rule["pass_count"] + rule["fail_count"], 1) * 100, 1)
            with st.expander(f"{rule['id']} — {rule['name']}"):
                ec1, ec2, ec3 = st.columns([4, 3, 3])
                with ec1:
                    st.markdown(f"""
                    <div class="rule-card">
                        <div class="rule-name">{rule['name']}</div>
                        <div class="rule-meta">{rule['description']}</div>
                        <div style="margin-top:0.75rem;display:flex;gap:0.5rem;flex-wrap:wrap">
                            <span class="status-badge {status_cls}">{'Active' if rule['active'] else 'Inactive'}</span>
                            <span class="status-badge status-published">{rule['current_version']}</span>
                            <span class="status-badge status-review">{rule['category']}</span>
                        </div>
                        <div style="margin-top:0.75rem" class="metric-row">
                            <span class="metric-row-key">Condition</span>
                            <span class="metric-row-val" style="font-family:monospace;font-size:0.78rem">{rule['field']} {rule['operator']} {rule['threshold']}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-row-key">Created</span>
                            <span class="metric-row-val">{rule['created_at']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with ec2:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown('<div style="font-size:0.75rem;font-weight:700;color:#c9a84c;margin-bottom:0.75rem">PERFORMANCE</div>', unsafe_allow_html=True)
                    st.plotly_chart(
                        make_gauge(pass_rate, "Pass Rate %", 100, "#22c55e" if pass_rate >= 70 else "#ef4444"),
                        use_container_width=True,
                        config={"displayModeBar": False},
                        key=f"gauge_{rule['id']}"
                    )
                    st.markdown(f"""
                    <div class="metric-row"><span class="metric-row-key">Passed</span><span class="metric-row-val" style="color:#22c55e">{rule['pass_count']}</span></div>
                    <div class="metric-row"><span class="metric-row-key">Failed</span><span class="metric-row-val" style="color:#ef4444">{rule['fail_count']}</span></div>
                    """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with ec3:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown('<div style="font-size:0.75rem;font-weight:700;color:#c9a84c;margin-bottom:0.75rem">VERSION HISTORY</div>', unsafe_allow_html=True)
                    for vh in rule["version_history"]:
                        st.markdown(f"""
                        <div class="timeline-item">
                            <div class="timeline-dot"></div>
                            <div class="timeline-content">
                                <div class="timeline-title">{vh['version']} — {vh.get('change_notes','')}</div>
                                <div class="timeline-time">{vh['created_at']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    act_col1, act_col2 = st.columns(2)
                    with act_col1:
                        if st.button("Version Rule", key=f"ver_{rule['id']}"):
                            new_v = f"v{len(rule['version_history'])+1}.0"
                            rule["version_history"].append({"version": new_v, "threshold": rule["threshold"], "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"), "created_by": st.session_state.current_user["email"] if "email" in st.session_state.current_user else "analyst@dprs.com", "change_notes": "Manual version"})
                            rule["current_version"] = new_v
                            st.success(f"Versioned to {new_v}")
                    with act_col2:
                        if st.button("Deactivate" if rule["active"] else "Activate", key=f"deact_{rule['id']}"):
                            rule["active"] = not rule["active"]
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Define New Business Rule</div></div>', unsafe_allow_html=True)
        with st.form("create_rule_form"):
            nc1, nc2 = st.columns(2)
            with nc1:
                r_name = st.text_input("Rule Name", placeholder="e.g. Minimum Credit Score Check")
                r_field = st.text_input("Data Field", placeholder="e.g. credit_score")
                r_operator = st.selectbox("Operator", [">=", "<=", "==", "!=", ">", "<", "in"])
                r_threshold = st.text_input("Threshold Value", placeholder="e.g. 650")
            with nc2:
                r_desc = st.text_area("Description / Purpose", placeholder="Describe what this rule evaluates and why it matters...", height=110)
                r_category = st.selectbox("Category", ["Credit","Income","Employment","Risk","Compliance","Identity"])
            submitted = st.form_submit_button("CREATE RULE")
            if submitted:
                if r_name and r_field and r_threshold:
                    try:
                        tval = float(r_threshold) if "." in r_threshold else int(r_threshold)
                    except:
                        tval = r_threshold
                    new_rule = {
                        "id": f"R{str(len(rules)+1).zfill(3)}",
                        "name": r_name,
                        "category": r_category,
                        "field": r_field,
                        "operator": r_operator,
                        "threshold": tval,
                        "description": r_desc,
                        "active": True,
                        "current_version": "v1.0",
                        "version_history": [{"version": "v1.0", "threshold": tval, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"), "created_by": "analyst@dprs.com", "change_notes": "Initial version"}],
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "created_by": "analyst@dprs.com",
                        "pass_count": 0,
                        "fail_count": 0,
                    }
                    st.session_state.rules.append(new_rule)
                    st.success(f"Rule '{r_name}' created successfully as {new_rule['id']}")
                else:
                    st.error("Please fill all required fields.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Rule Performance Analytics</div></div>', unsafe_allow_html=True)
        ra1, ra2 = st.columns(2)
        with ra1:
            cat_counts = {}
            for r in rules:
                cat_counts[r["category"]] = cat_counts.get(r["category"], 0) + 1
            st.plotly_chart(make_donut(list(cat_counts.keys()), list(cat_counts.values()), "By Cat"), use_container_width=True, config={"displayModeBar": False})
        with ra2:
            rule_names = [r["name"][:20] for r in rules[:10]]
            pass_rates = [round(r["pass_count"] / max(r["pass_count"] + r["fail_count"], 1) * 100, 1) for r in rules[:10]]
            st.plotly_chart(make_bar(rule_names, pass_rates, "Pass Rate % by Rule", "#22c55e", horizontal=True), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def page_workflows():
    workflows = st.session_state.workflows
    rules = st.session_state.rules
    st.markdown('<div class="page-hero"><div class="hero-title">Workflow <span>Management</span></div><div class="hero-sub">Create, version, publish, and clone decision workflows</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="content-area">', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Workflow Library", "Create Workflow", "Version Timeline"])

    with tab1:
        for wf in workflows:
            status_map = {"published": "status-approved", "draft": "status-pending", "archived": "status-inactive"}
            badge_cls = status_map.get(wf["status"], "status-pending")
            with st.expander(f"{wf['id']} — {wf['name']} [{wf['current_version']}]"):
                wc1, wc2, wc3 = st.columns([4, 3, 3])
                with wc1:
                    st.markdown(f"""
                    <div class="rule-card">
                        <div class="rule-name">{wf['name']}</div>
                        <div class="rule-meta">{wf['description']}</div>
                        <div style="margin-top:0.75rem;display:flex;gap:0.5rem">
                            <span class="status-badge {badge_cls}">{wf['status'].upper()}</span>
                            <span class="status-badge status-published">{wf['current_version']}</span>
                        </div>
                        <div style="margin-top:0.75rem">
                        <div class="metric-row"><span class="metric-row-key">Rules Count</span><span class="metric-row-val">{len(wf['rule_ids'])}</span></div>
                        <div class="metric-row"><span class="metric-row-key">Total Executions</span><span class="metric-row-val">{wf['executions']}</span></div>
                        <div class="metric-row"><span class="metric-row-key">Approval Required</span><span class="metric-row-val">{'Yes' if wf['approval_required'] else 'No'}</span></div>
                        <div class="metric-row"><span class="metric-row-key">Created</span><span class="metric-row-val">{wf['created_at']}</span></div>
                        {'<div class="metric-row"><span class="metric-row-key">Published</span><span class="metric-row-val">'+wf['published_at']+'</span></div>' if wf['published_at'] else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with wc2:
                    st.markdown('<div class="card"><div style="font-size:0.75rem;font-weight:700;color:#c9a84c;margin-bottom:0.75rem">RULE SEQUENCE</div>', unsafe_allow_html=True)
                    rules_map = {r["id"]: r for r in rules}
                    for idx, rid in enumerate(wf["rule_ids"]):
                        rule = rules_map.get(rid)
                        if rule:
                            act_cls = "status-approved" if rule["active"] else "status-inactive"
                            st.markdown(f"""
                            <div style="display:flex;align-items:center;gap:0.5rem;padding:0.35rem 0;border-bottom:1px solid #1a2236">
                                <span style="color:#c9a84c;font-size:0.75rem;font-weight:700;width:20px">{idx+1}</span>
                                <span style="color:#e8e8e8;font-size:0.78rem;flex:1">{rule['name']}</span>
                                <span class="status-badge {act_cls}" style="font-size:0.62rem;padding:0.1rem 0.35rem">{'ON' if rule['active'] else 'OFF'}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with wc3:
                    st.markdown('<div class="card"><div style="font-size:0.75rem;font-weight:700;color:#c9a84c;margin-bottom:0.75rem">ACTIONS</div>', unsafe_allow_html=True)
                    btn_c1, btn_c2 = st.columns(2)
                    with btn_c1:
                        if wf["status"] == "draft":
                            if st.button("Publish", key=f"pub_{wf['id']}"):
                                wf["status"] = "published"
                                wf["published_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                                st.rerun()
                    with btn_c2:
                        if st.button("Clone", key=f"clone_{wf['id']}"):
                            new_wf = copy.deepcopy(wf)
                            new_wf["id"] = f"WF{str(len(workflows)+1).zfill(3)}"
                            new_wf["name"] = f"{wf['name']} (Clone)"
                            new_wf["status"] = "draft"
                            new_wf["published_at"] = None
                            new_wf["executions"] = 0
                            new_wf["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            new_wf["version_history"] = [{"version": "v1.0", "date": datetime.now().strftime("%Y-%m-%d"), "notes": f"Cloned from {wf['id']}"}]
                            new_wf["current_version"] = "v1.0"
                            st.session_state.workflows.append(new_wf)
                            st.success(f"Cloned as {new_wf['id']}")
                    st.markdown('<div style="margin-top:0.75rem"><div style="font-size:0.75rem;font-weight:700;color:#c9a84c;margin-bottom:0.5rem">VERSION HISTORY</div>', unsafe_allow_html=True)
                    for vh in wf["version_history"]:
                        st.markdown(f"""
                        <div class="timeline-item">
                            <div class="timeline-dot"></div>
                            <div class="timeline-content">
                                <div class="timeline-title">{vh['version']} — {vh['notes']}</div>
                                <div class="timeline-time">{vh['date']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div></div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Create New Workflow</div></div>', unsafe_allow_html=True)
        with st.form("create_wf_form"):
            wffc1, wffc2 = st.columns(2)
            with wffc1:
                wf_name = st.text_input("Workflow Name", placeholder="e.g. Priority Credit Assessment")
                wf_desc = st.text_area("Description", placeholder="Describe this workflow's purpose and scope...")
                wf_approval = st.checkbox("Require admin approval before publishing")
            with wffc2:
                st.markdown("**Select Rules for this Workflow**")
                selected_rules = []
                for rule in rules:
                    if rule["active"]:
                        if st.checkbox(f"{rule['id']}: {rule['name']}", key=f"wf_rule_{rule['id']}"):
                            selected_rules.append(rule["id"])
            if st.form_submit_button("CREATE WORKFLOW"):
                if wf_name and selected_rules:
                    new_wf = {
                        "id": f"WF{str(len(workflows)+1).zfill(3)}",
                        "name": wf_name,
                        "description": wf_desc,
                        "status": "draft",
                        "current_version": "v1.0",
                        "rule_ids": selected_rules,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "published_at": None,
                        "created_by": "analyst@dprs.com",
                        "approval_required": wf_approval,
                        "approved_by": None,
                        "executions": 0,
                        "version_history": [{"version": "v1.0", "date": datetime.now().strftime("%Y-%m-%d"), "notes": "Initial creation"}],
                    }
                    st.session_state.workflows.append(new_wf)
                    st.success(f"Workflow '{wf_name}' created as {new_wf['id']}")
                else:
                    st.error("Provide workflow name and select at least one rule.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Workflow & Rule Version Timeline</div></div>', unsafe_allow_html=True)
        events = []
        for wf in workflows:
            for vh in wf["version_history"]:
                events.append({"type": "Workflow", "name": wf["name"], "version": vh["version"], "date": vh["date"], "notes": vh["notes"]})
        for rule in rules:
            for vh in rule["version_history"]:
                events.append({"type": "Rule", "name": rule["name"], "version": vh["version"], "date": vh.get("created_at", "")[:10], "notes": vh.get("change_notes", "")})
        events.sort(key=lambda x: x["date"], reverse=True)
        for ev in events[:20]:
            type_cls = "status-review" if ev["type"] == "Workflow" else "status-published"
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                    <div class="timeline-title">
                        <span class="status-badge {type_cls}">{ev['type']}</span>
                        {ev['name']} — <span style="color:#c9a84c">{ev['version']}</span>
                        <span style="color:#7a8099;font-size:0.72rem"> — {ev['notes']}</span>
                    </div>
                    <div class="timeline-time">{ev['date']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def page_execute():
    workflows = st.session_state.workflows
    published_wfs = [w for w in workflows if w["status"] == "published"]
    st.markdown('<div class="page-hero"><div class="hero-title">Execute <span>Decision</span></div><div class="hero-sub">Submit applicant data and run decision workflows in real-time</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="content-area">', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Single Decision", "Batch Evaluation"])

    with tab1:
        fc1, fc2 = st.columns([5, 5])
        with fc1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header"><div class="card-title">Applicant Data Input</div></div>', unsafe_allow_html=True)
            with st.form("execute_form"):
                applicant_name = st.text_input("Applicant Name", placeholder="Full name")
                selected_wf_name = st.selectbox("Decision Workflow", [w["name"] for w in published_wfs])
                scenario_type = st.selectbox("Scenario Type", ["production", "test", "exception"])
                st.markdown("---")
                ef1, ef2 = st.columns(2)
                with ef1:
                    credit_score = st.number_input("Credit Score", 300, 850, 700)
                    annual_income = st.number_input("Annual Income ($)", 0, 500000, 60000, step=1000)
                    employment_years = st.number_input("Employment Years", 0, 40, 5)
                    debt_to_income = st.slider("Debt-to-Income Ratio", 0.0, 1.0, 0.35, 0.01)
                    loan_amount = st.number_input("Loan Amount ($)", 0, 2000000, 150000, step=5000)
                with ef2:
                    bankruptcies = st.number_input("Bankruptcies (last 5yr)", 0, 5, 0)
                    active_accounts = st.number_input("Active Credit Accounts", 0, 20, 4)
                    credit_history_years = st.number_input("Credit History (years)", 0, 40, 7)
                    late_payments = st.number_input("Late Payments (12mo)", 0, 24, 0)
                    risk_score = st.slider("Internal Risk Score", 0, 100, 45)
                st.markdown("---")
                ef3, ef4 = st.columns(2)
                with ef3:
                    income_verified = st.checkbox("Income Verified", value=True)
                    appraisal_complete = st.checkbox("Appraisal Complete", value=True)
                    identity_verified = st.checkbox("Identity Verified", value=True)
                    region_approved = st.checkbox("Region Approved", value=True)
                    prior_default = st.checkbox("Prior Default on Record", value=False)
                with ef4:
                    collateral_ratio = st.slider("Collateral Ratio", 0.5, 3.0, 1.5, 0.05)
                    monthly_payment_ratio = st.slider("Monthly Payment Ratio", 0.0, 1.0, 0.28, 0.01)
                    employment_type = st.selectbox("Employment Type", ["fulltime", "parttime", "contract", "self-employed"])
                submitted = st.form_submit_button("EXECUTE DECISION WORKFLOW")
            st.markdown('</div>', unsafe_allow_html=True)

        with fc2:
            if submitted and applicant_name:
                selected_wf = next((w for w in published_wfs if w["name"] == selected_wf_name), None)
                if selected_wf:
                    loan_to_income = round(loan_amount / max(annual_income, 1), 2)
                    app_data = {
                        "credit_score": credit_score,
                        "debt_to_income": debt_to_income,
                        "employment_years": employment_years,
                        "annual_income": annual_income,
                        "loan_to_income": loan_to_income,
                        "bankruptcies_last_5yr": bankruptcies,
                        "active_accounts": active_accounts,
                        "income_verified": income_verified,
                        "credit_history_years": credit_history_years,
                        "late_payments_12mo": late_payments,
                        "appraisal_complete": appraisal_complete,
                        "identity_verified": identity_verified,
                        "risk_score": risk_score,
                        "collateral_ratio": collateral_ratio,
                        "region_approved": region_approved,
                        "prior_default": prior_default,
                        "monthly_payment_ratio": monthly_payment_ratio,
                        "employment_type": employment_type,
                    }
                    outcome, rule_results, approval_score = _execute_workflow(selected_wf, app_data)
                    ex_id = f"EX{str(len(st.session_state.executions)+1).zfill(4)}"
                    new_ex = {
                        "id": ex_id,
                        "applicant_name": applicant_name,
                        "workflow_id": selected_wf["id"],
                        "workflow_version": selected_wf["current_version"],
                        "outcome": outcome,
                        "approval_score": approval_score,
                        "applicant_data": app_data,
                        "rule_results": rule_results,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "executed_by": "analyst@dprs.com",
                        "scenario_type": scenario_type,
                        "replayed": False,
                        "immutable": True,
                    }
                    st.session_state.executions.insert(0, new_ex)
                    for r in st.session_state.rules:
                        for rr in rule_results:
                            if rr["rule_id"] == r["id"]:
                                if rr["passed"]:
                                    r["pass_count"] += 1
                                else:
                                    r["fail_count"] += 1

                    result_color = "#22c55e" if outcome == "APPROVED" else "#ef4444"
                    badge_cls = "status-approved" if outcome == "APPROVED" else "status-rejected"
                    st.markdown(f"""
                    <div class="card" style="border-top:4px solid {result_color}">
                        <div style="text-align:center;padding:1rem 0">
                            <div style="font-size:0.75rem;color:#9aa0b4;text-transform:uppercase;letter-spacing:2px">Decision Outcome</div>
                            <div style="font-size:2.5rem;font-weight:900;color:{result_color};margin:0.5rem 0">{outcome}</div>
                            <div style="font-size:1rem;color:#c9a84c;font-weight:700">Approval Score: {approval_score}%</div>
                            <div style="font-size:0.75rem;color:#7a8099;margin-top:0.25rem">Execution ID: {ex_id}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown('<div class="card-header"><div class="card-title">Rule Evaluation Waterfall</div></div>', unsafe_allow_html=True)
                    st.plotly_chart(make_waterfall(rule_results), use_container_width=True, config={"displayModeBar": False})
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown('<div class="card-header"><div class="card-title">Rule-by-Rule Results</div></div>', unsafe_allow_html=True)
                    st.markdown('<div class="audit-row audit-head"><span>Rule</span><span>Version</span><span>Result</span><span>Condition</span><span>Actual</span></div>', unsafe_allow_html=True)
                    for rr in rule_results:
                        res_cls = "step-result-pass" if rr["passed"] else "step-result-fail"
                        res_txt = "PASS" if rr["passed"] else "FAIL"
                        st.markdown(f"""
                        <div class="audit-row">
                            <span style="color:#e8e8e8;font-weight:600;font-size:0.78rem">{rr['rule_name']}</span>
                            <span style="color:#a855f7;font-size:0.75rem">{rr['version']}</span>
                            <span class="{res_cls}" style="font-weight:700">{res_txt}</span>
                            <span style="color:#9aa0b4;font-size:0.72rem;font-family:monospace">{rr['field']} {rr['operator']} {rr['threshold']}</span>
                            <span style="color:#c9a84c;font-weight:600;font-size:0.78rem">{rr['actual_value']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown('<div class="card-header"><div class="card-title">Category Performance Radar</div></div>', unsafe_allow_html=True)
                    st.plotly_chart(make_radar(rule_results), use_container_width=True, config={"displayModeBar": False})
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="card" style="text-align:center;padding:3rem">
                    <div style="font-size:3rem;color:#1e2a3d">&#9654;</div>
                    <div style="color:#7a8099;font-size:0.85rem;margin-top:1rem">Fill in applicant data and click Execute to see results</div>
                    <div style="color:#c9a84c;font-size:0.75rem;margin-top:0.5rem">Results will include rule-by-rule breakdown, approval score, and visual analytics</div>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Batch Decision Evaluation</div><span class="card-badge">Simulate Multiple Applicants</span></div>', unsafe_allow_html=True)
        bc1, bc2 = st.columns([3, 7])
        with bc1:
            batch_wf_name = st.selectbox("Workflow", [w["name"] for w in published_wfs], key="batch_wf")
            batch_count = st.slider("Number of Applicants", 5, 50, 15)
            batch_type = st.selectbox("Scenario Type", ["production", "test", "exception"], key="batch_type")
            if st.button("RUN BATCH EVALUATION"):
                batch_wf = next((w for w in published_wfs if w["name"] == batch_wf_name), None)
                if batch_wf:
                    results = []
                    names = ["Alex Carter","Maria Santos","James Wu","Priya Patel","Kevin Nguyen","Sarah Johnson","David Kim","Linda Chen","Robert Taylor","Aisha Williams","Michael Brown","Emma Davis","Carlos Rivera","Fatima Al-Rashid","Liam Patel","Zoe Hernandez","Noah Smith","Isabella Jones","Oliver Martin","Sophia White"]
                    for i in range(batch_count):
                        app = _make_applicant()
                        outcome, rr, score = _execute_workflow(batch_wf, app)
                        ex_id = f"EX{str(len(st.session_state.executions)+1+i).zfill(4)}"
                        new_ex = {"id": ex_id, "applicant_name": random.choice(names), "workflow_id": batch_wf["id"], "workflow_version": batch_wf["current_version"], "outcome": outcome, "approval_score": score, "applicant_data": app, "rule_results": rr, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "executed_by": "business@dprs.com", "scenario_type": batch_type, "replayed": False, "immutable": True}
                        st.session_state.executions.insert(0, new_ex)
                        results.append(new_ex)
                    st.session_state["batch_results"] = results
                    st.success(f"Batch of {batch_count} decisions executed successfully.")

        with bc2:
            if "batch_results" in st.session_state:
                br = st.session_state["batch_results"]
                approved_b = sum(1 for e in br if e["outcome"] == "APPROVED")
                rejected_b = len(br) - approved_b
                avg_score_b = round(sum(e["approval_score"] for e in br) / max(len(br), 1), 1)
                bmc1, bmc2, bmc3 = st.columns(3)
                bmc1.metric("Total Evaluated", len(br))
                bmc2.metric("Approved", approved_b)
                bmc3.metric("Avg Score", f"{avg_score_b}%")
                st.plotly_chart(make_bar(["Approved","Rejected"], [approved_b, rejected_b], color="#c9a84c"), use_container_width=True, config={"displayModeBar": False})
                df = pd.DataFrame([{"ID": e["id"], "Applicant": e["applicant_name"], "Outcome": e["outcome"], "Score": f"{e['approval_score']}%", "Time": e["timestamp"]} for e in br])
                st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def page_history():
    executions = st.session_state.executions
    workflows = st.session_state.workflows
    st.markdown('<div class="page-hero"><div class="hero-title">Decision <span>History</span></div><div class="hero-sub">Immutable records of all past decision executions with full audit trail</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="content-area">', unsafe_allow_html=True)

    hf1, hf2, hf3, hf4 = st.columns(4)
    with hf1:
        outcome_f = st.selectbox("Outcome", ["All", "APPROVED", "REJECTED"])
    with hf2:
        wf_names = ["All"] + [w["name"] for w in workflows]
        wf_f = st.selectbox("Workflow", wf_names)
    with hf3:
        scenario_f = st.selectbox("Scenario Type", ["All", "production", "test", "exception"])
    with hf4:
        search_f = st.text_input("Search Applicant", placeholder="Name...")

    filtered = executions
    if outcome_f != "All":
        filtered = [e for e in filtered if e["outcome"] == outcome_f]
    if wf_f != "All":
        wf_obj = next((w for w in workflows if w["name"] == wf_f), None)
        if wf_obj:
            filtered = [e for e in filtered if e["workflow_id"] == wf_obj["id"]]
    if scenario_f != "All":
        filtered = [e for e in filtered if e["scenario_type"] == scenario_f]
    if search_f:
        filtered = [e for e in filtered if search_f.lower() in e["applicant_name"].lower()]

    st.markdown(f"<div style='color:#7a8099;font-size:0.78rem;margin-bottom:0.75rem'>{len(filtered)} execution records found</div>", unsafe_allow_html=True)

    for ex in filtered[:20]:
        wf = next((w for w in workflows if w["id"] == ex["workflow_id"]), None)
        wf_name = wf["name"] if wf else ex["workflow_id"]
        badge_cls = "status-approved" if ex["outcome"] == "APPROVED" else "status-rejected"
        with st.expander(f"{ex['id']} — {ex['applicant_name']} — {ex['outcome']} — {ex['timestamp'][:16]}"):
            hec1, hec2, hec3 = st.columns([4, 4, 4])
            with hec1:
                st.markdown(f"""
                <div class="card">
                    <div class="card-header"><div class="card-title">Execution Summary</div></div>
                    <div class="metric-row"><span class="metric-row-key">Execution ID</span><span class="metric-row-val" style="font-family:monospace">{ex['id']}</span></div>
                    <div class="metric-row"><span class="metric-row-key">Applicant</span><span class="metric-row-val">{ex['applicant_name']}</span></div>
                    <div class="metric-row"><span class="metric-row-key">Outcome</span><span><span class="status-badge {badge_cls}">{ex['outcome']}</span></span></div>
                    <div class="metric-row"><span class="metric-row-key">Approval Score</span><span class="metric-row-val" style="color:#c9a84c">{ex['approval_score']}%</span></div>
                    <div class="metric-row"><span class="metric-row-key">Workflow</span><span class="metric-row-val">{wf_name}</span></div>
                    <div class="metric-row"><span class="metric-row-key">Version</span><span class="metric-row-val">{ex['workflow_version']}</span></div>
                    <div class="metric-row"><span class="metric-row-key">Scenario</span><span class="metric-row-val">{ex['scenario_type'].upper()}</span></div>
                    <div class="metric-row"><span class="metric-row-key">Executed By</span><span class="metric-row-val">{ex['executed_by']}</span></div>
                    <div class="metric-row"><span class="metric-row-key">Timestamp</span><span class="metric-row-val">{ex['timestamp']}</span></div>
                    <div class="metric-row"><span class="metric-row-key">Immutable</span><span class="metric-row-val" style="color:#22c55e">Verified</span></div>
                </div>
                """, unsafe_allow_html=True)
            with hec2:
                st.markdown('<div class="card"><div class="card-header"><div class="card-title">Rule Results</div></div>', unsafe_allow_html=True)
                for rr in ex["rule_results"]:
                    res_cls = "step-result-pass" if rr["passed"] else "step-result-fail"
                    res_txt = "PASS" if rr["passed"] else "FAIL"
                    st.markdown(f"""
                    <div class="exec-step">
                        <span class="step-name">{rr['rule_name']}</span>
                        <span class="{res_cls}">{res_txt}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with hec3:
                st.markdown('<div class="card"><div class="card-header"><div class="card-title">Applicant Data</div></div>', unsafe_allow_html=True)
                for k, v in ex["applicant_data"].items():
                    st.markdown(f'<div class="metric-row"><span class="metric-row-key">{k.replace("_"," ").title()}</span><span class="metric-row-val">{v}</span></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def page_replay():
    executions = st.session_state.executions
    workflows = st.session_state.workflows
    st.markdown('<div class="page-hero"><div class="hero-title">Replay <span>& Compare</span></div><div class="hero-sub">Reproduce past decisions and analyze differences across workflow versions</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="content-area">', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Replay Decision", "Compare Executions"])

    with tab1:
        rc1, rc2 = st.columns([4, 6])
        with rc1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header"><div class="card-title">Select Execution to Replay</div></div>', unsafe_allow_html=True)
            ex_ids = [f"{e['id']} — {e['applicant_name']} ({e['outcome']})" for e in executions[:30]]
            selected_ex_str = st.selectbox("Execution Record", ex_ids)
            replay_wf_override = st.checkbox("Override with different workflow version")
            override_wf = None
            if replay_wf_override:
                published = [w for w in workflows if w["status"] == "published"]
                override_wf_name = st.selectbox("Use Workflow", [w["name"] for w in published])
                override_wf = next((w for w in published if w["name"] == override_wf_name), None)
            if st.button("REPLAY EXECUTION"):
                ex_id = selected_ex_str.split(" — ")[0]
                original_ex = next((e for e in executions if e["id"] == ex_id), None)
                if original_ex:
                    wf = override_wf if override_wf else next((w for w in workflows if w["id"] == original_ex["workflow_id"]), None)
                    if wf:
                        outcome, rule_results, approval_score = _execute_workflow(wf, original_ex["applicant_data"])
                        replay_id = f"EX{str(len(executions)+1).zfill(4)}"
                        replayed_ex = {
                            "id": replay_id,
                            "applicant_name": f"{original_ex['applicant_name']} (Replay)",
                            "workflow_id": wf["id"],
                            "workflow_version": wf["current_version"],
                            "outcome": outcome,
                            "approval_score": approval_score,
                            "applicant_data": original_ex["applicant_data"],
                            "rule_results": rule_results,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "executed_by": "auditor@dprs.com",
                            "scenario_type": original_ex["scenario_type"],
                            "replayed": True,
                            "original_id": ex_id,
                            "immutable": True,
                        }
                        st.session_state.executions.insert(0, replayed_ex)
                        st.session_state["last_replay"] = (original_ex, replayed_ex)
                        st.success(f"Replay complete. New ID: {replay_id}")
            st.markdown('</div>', unsafe_allow_html=True)

        with rc2:
            if "last_replay" in st.session_state:
                orig, rep = st.session_state["last_replay"]
                orig_cls = "status-approved" if orig["outcome"] == "APPROVED" else "status-rejected"
                rep_cls = "status-approved" if rep["outcome"] == "APPROVED" else "status-rejected"
                outcome_match = orig["outcome"] == rep["outcome"]
                st.markdown(f"""
                <div class="card" style="border-top:4px solid {'#22c55e' if outcome_match else '#ef4444'}">
                    <div class="card-header"><div class="card-title">Replay Verification</div><span class="replay-badge">REPLAYED</span></div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;text-align:center;padding:1rem 0">
                        <div>
                            <div style="font-size:0.68rem;color:#7a8099;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.5rem">Original</div>
                            <div style="font-size:1.5rem;font-weight:800;color:{'#22c55e' if orig['outcome']=='APPROVED' else '#ef4444'}">{orig['outcome']}</div>
                            <div style="color:#c9a84c;font-weight:700">{orig['approval_score']}%</div>
                            <div style="color:#7a8099;font-size:0.7rem">{orig['id']}</div>
                        </div>
                        <div>
                            <div style="font-size:0.68rem;color:#7a8099;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.5rem">Replayed</div>
                            <div style="font-size:1.5rem;font-weight:800;color:{'#22c55e' if rep['outcome']=='APPROVED' else '#ef4444'}">{rep['outcome']}</div>
                            <div style="color:#c9a84c;font-weight:700">{rep['approval_score']}%</div>
                            <div style="color:#7a8099;font-size:0.7rem">{rep['id']}</div>
                        </div>
                    </div>
                    <div style="text-align:center;padding:0.75rem;background:{'rgba(34,197,94,0.08)' if outcome_match else 'rgba(239,68,68,0.08)'};border-radius:6px;margin-top:0.5rem">
                        <span style="color:{'#22c55e' if outcome_match else '#ef4444'};font-weight:700;font-size:0.85rem">
                            {'DETERMINISM VERIFIED — Results Match' if outcome_match else 'DIVERGENCE DETECTED — Outcomes Differ'}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<div class="card"><div class="card-header"><div class="card-title">Rule-Level Comparison</div></div>', unsafe_allow_html=True)
                orig_rr = {r["rule_name"]: r["passed"] for r in orig["rule_results"]}
                rep_rr = {r["rule_name"]: r["passed"] for r in rep["rule_results"]}
                all_rules_in_replay = list(rep_rr.keys())
                diffs = 0
                for rname in all_rules_in_replay:
                    o_passed = orig_rr.get(rname, None)
                    r_passed = rep_rr.get(rname, None)
                    matched = o_passed == r_passed
                    if not matched:
                        diffs += 1
                    div_cls = "comparison-same" if matched else "comparison-diff"
                    o_txt = ("PASS" if o_passed else "FAIL") if o_passed is not None else "N/A"
                    r_txt = ("PASS" if r_passed else "FAIL") if r_passed is not None else "N/A"
                    st.markdown(f'<div class="{div_cls}">{rname}: Original={o_txt} / Replayed={r_txt}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#7a8099;font-size:0.75rem;margin-top:0.5rem">{diffs} rule differences identified</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Compare Two Executions</div></div>', unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        ex_ids_list = [f"{e['id']} — {e['applicant_name']} ({e['outcome']})" for e in executions[:40]]
        with cc1:
            comp_ex1 = st.selectbox("Execution A", ex_ids_list, key="comp_a")
        with cc2:
            comp_ex2 = st.selectbox("Execution B", ex_ids_list, index=min(1, len(ex_ids_list)-1), key="comp_b")
        if st.button("RUN COMPARISON"):
            id1 = comp_ex1.split(" — ")[0]
            id2 = comp_ex2.split(" — ")[0]
            ex1 = next((e for e in executions if e["id"] == id1), None)
            ex2 = next((e for e in executions if e["id"] == id2), None)
            if ex1 and ex2:
                st.markdown('<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1rem">', unsafe_allow_html=True)
                csc1, csc2 = st.columns(2)
                with csc1:
                    o1_cls = "status-approved" if ex1["outcome"] == "APPROVED" else "status-rejected"
                    st.markdown(f"""
                    <div class="card" style="border-top:3px solid {'#22c55e' if ex1['outcome']=='APPROVED' else '#ef4444'}">
                        <div class="card-title" style="margin-bottom:0.75rem">{ex1['id']}</div>
                        <div class="metric-row"><span class="metric-row-key">Applicant</span><span class="metric-row-val">{ex1['applicant_name']}</span></div>
                        <div class="metric-row"><span class="metric-row-key">Outcome</span><span><span class="status-badge {o1_cls}">{ex1['outcome']}</span></span></div>
                        <div class="metric-row"><span class="metric-row-key">Score</span><span class="metric-row-val" style="color:#c9a84c">{ex1['approval_score']}%</span></div>
                        <div class="metric-row"><span class="metric-row-key">Workflow Ver.</span><span class="metric-row-val">{ex1['workflow_version']}</span></div>
                        <div class="metric-row"><span class="metric-row-key">Timestamp</span><span class="metric-row-val">{ex1['timestamp'][:16]}</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                with csc2:
                    o2_cls = "status-approved" if ex2["outcome"] == "APPROVED" else "status-rejected"
                    st.markdown(f"""
                    <div class="card" style="border-top:3px solid {'#22c55e' if ex2['outcome']=='APPROVED' else '#ef4444'}">
                        <div class="card-title" style="margin-bottom:0.75rem">{ex2['id']}</div>
                        <div class="metric-row"><span class="metric-row-key">Applicant</span><span class="metric-row-val">{ex2['applicant_name']}</span></div>
                        <div class="metric-row"><span class="metric-row-key">Outcome</span><span><span class="status-badge {o2_cls}">{ex2['outcome']}</span></span></div>
                        <div class="metric-row"><span class="metric-row-key">Score</span><span class="metric-row-val" style="color:#c9a84c">{ex2['approval_score']}%</span></div>
                        <div class="metric-row"><span class="metric-row-key">Workflow Ver.</span><span class="metric-row-val">{ex2['workflow_version']}</span></div>
                        <div class="metric-row"><span class="metric-row-key">Timestamp</span><span class="metric-row-val">{ex2['timestamp'][:16]}</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                all_fields = list(set(list(ex1["applicant_data"].keys()) + list(ex2["applicant_data"].keys())))
                diffs = []
                for field in all_fields:
                    v1 = ex1["applicant_data"].get(field, "N/A")
                    v2 = ex2["applicant_data"].get(field, "N/A")
                    if v1 != v2:
                        diffs.append((field, v1, v2))

                if diffs:
                    st.markdown(f'<div style="margin-top:1rem;color:#c9a84c;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:1px">{len(diffs)} Data Differences Detected</div>', unsafe_allow_html=True)
                    for field, v1, v2 in diffs:
                        st.markdown(f'<div class="comparison-diff">{field.replace("_"," ").title()}: A={v1} vs B={v2}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="comparison-same">No data differences — same applicant data</div>', unsafe_allow_html=True)

                rr1 = {r["rule_name"]: r["passed"] for r in ex1["rule_results"]}
                rr2 = {r["rule_name"]: r["passed"] for r in ex2["rule_results"]}
                all_r = list(set(list(rr1.keys()) + list(rr2.keys())))
                rule_diffs = [(r, rr1.get(r), rr2.get(r)) for r in all_r if rr1.get(r) != rr2.get(r)]
                if rule_diffs:
                    st.markdown(f'<div style="margin-top:1rem;color:#ef4444;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:1px">{len(rule_diffs)} Rule Outcome Differences</div>', unsafe_allow_html=True)
                    for rname, r1, r2 in rule_diffs:
                        st.markdown(f'<div class="comparison-diff">{rname}: A={"PASS" if r1 else "FAIL"} vs B={"PASS" if r2 else "FAIL"}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="comparison-same" style="margin-top:1rem">All rule outcomes match between executions</div>', unsafe_allow_html=True)

                comp_fig = go.Figure()
                comp_fig.add_trace(go.Bar(name=ex1["id"], x=["Approval Score"], y=[ex1["approval_score"]], marker_color="#c9a84c"))
                comp_fig.add_trace(go.Bar(name=ex2["id"], x=["Approval Score"], y=[ex2["approval_score"]], marker_color="#3b82f6"))
                comp_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=200, margin=dict(l=10,r=10,t=20,b=20), barmode="group", legend=dict(font=dict(color="#9aa0b4",size=9),bgcolor="rgba(0,0,0,0)"), yaxis=dict(gridcolor="#1e2a3d",tickfont=dict(color="#7a8099",size=9)), font={"family":"Inter"})
                st.plotly_chart(comp_fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def page_audit():
    executions = st.session_state.executions
    audit_logs = st.session_state.audit_log
    workflows = st.session_state.workflows
    st.markdown('<div class="page-hero"><div class="hero-title">Audit <span>Trail</span></div><div class="hero-sub">Immutable activity log for compliance and regulatory review</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="content-area">', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Activity Log", "Risk Analysis", "Export Records"])

    with tab1:
        af1, af2 = st.columns([3, 3])
        with af1:
            audit_search = st.text_input("Search actions or targets", placeholder="Search...")
        with af2:
            action_filter = st.selectbox("Action Type", ["All"] + list(set(l["action"] for l in audit_logs)))

        filtered_logs = audit_logs
        if audit_search:
            filtered_logs = [l for l in filtered_logs if audit_search.lower() in l["action"].lower() or audit_search.lower() in l["target"].lower()]
        if action_filter != "All":
            filtered_logs = [l for l in filtered_logs if l["action"] == action_filter]

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">System Activity Log</div><span class="card-badge">Immutable</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="audit-row audit-head"><span>Action</span><span>Target</span><span>User</span><span>IP Address</span><span>Timestamp</span></div>', unsafe_allow_html=True)
        for log in filtered_logs:
            st.markdown(f"""
            <div class="audit-row">
                <span style="color:#e8e8e8;font-weight:600">{log['action']}</span>
                <span style="color:#c9a84c;font-family:monospace;font-size:0.75rem">{log['target']}</span>
                <span style="color:#9aa0b4">{log['user']}</span>
                <span style="color:#7a8099;font-size:0.72rem">{log['ip']}</span>
                <span style="color:#7a8099;font-size:0.72rem">{log['timestamp'][:16]}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Exception Case Review</div></div>', unsafe_allow_html=True)
        exception_cases = [e for e in executions if e["scenario_type"] == "exception"]
        if exception_cases:
            for ex in exception_cases[:10]:
                badge_cls = "status-approved" if ex["outcome"] == "APPROVED" else "status-rejected"
                st.markdown(f"""
                <div class="rule-card">
                    <div style="display:flex;align-items:center;justify-content:space-between">
                        <div>
                            <div class="rule-name">{ex['applicant_name']}</div>
                            <div class="rule-meta">{ex['id']} — {ex['timestamp'][:16]}</div>
                        </div>
                        <div style="display:flex;gap:0.5rem;align-items:center">
                            <span class="status-badge status-pending">EXCEPTION</span>
                            <span class="status-badge {badge_cls}">{ex['outcome']}</span>
                            <span style="color:#c9a84c;font-weight:700">{ex['approval_score']}%</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No exception cases found in current dataset.")
        st.markdown('</div>', unsafe_allow_html=True)

        ar1, ar2 = st.columns(2)
        with ar1:
            st.markdown('<div class="card"><div class="card-header"><div class="card-title">Outcome by Scenario</div></div>', unsafe_allow_html=True)
            sc_data = {}
            for e in executions:
                key = f"{e['scenario_type']}-{e['outcome']}"
                sc_data[key] = sc_data.get(key, 0) + 1
            sc_labels = list(sc_data.keys())
            sc_vals = list(sc_data.values())
            st.plotly_chart(make_donut(sc_labels, sc_vals, ""), use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)
        with ar2:
            st.markdown('<div class="card"><div class="card-header"><div class="card-title">Risk Score Distribution</div></div>', unsafe_allow_html=True)
            risk_scores = [e["applicant_data"].get("risk_score", 50) for e in executions]
            bins = list(range(0, 110, 10))
            hist_vals = [sum(1 for s in risk_scores if bins[i] <= s < bins[i+1]) for i in range(len(bins)-1)]
            colors_r = ["#22c55e" if i < 5 else "#ef4444" for i in range(len(bins)-1)]
            fig_r = go.Figure(go.Bar(x=[f"{bins[i]}-{bins[i+1]}" for i in range(len(bins)-1)], y=hist_vals, marker_color=colors_r, marker_line_width=0))
            fig_r.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=220, margin=dict(l=10,r=10,t=10,b=30), xaxis=dict(gridcolor="#1e2a3d",tickfont=dict(color="#7a8099",size=9)), yaxis=dict(gridcolor="#1e2a3d",tickfont=dict(color="#7a8099",size=9)), font={"family":"Inter"})
            st.plotly_chart(fig_r, use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Export Decision Records</div></div>', unsafe_allow_html=True)
        ef1c, ef2c = st.columns(2)
        with ef1c:
            export_wf = st.selectbox("Filter by Workflow", ["All"] + [w["name"] for w in workflows], key="export_wf")
            export_outcome = st.selectbox("Filter by Outcome", ["All", "APPROVED", "REJECTED"], key="export_outcome")
        with ef2c:
            export_type = st.selectbox("Filter by Scenario", ["All", "production", "test", "exception"], key="export_type")
        filtered_export = executions
        if export_wf != "All":
            wf_obj = next((w for w in workflows if w["name"] == export_wf), None)
            if wf_obj:
                filtered_export = [e for e in filtered_export if e["workflow_id"] == wf_obj["id"]]
        if export_outcome != "All":
            filtered_export = [e for e in filtered_export if e["outcome"] == export_outcome]
        if export_type != "All":
            filtered_export = [e for e in filtered_export if e["scenario_type"] == export_type]

        export_df = pd.DataFrame([{
            "Execution ID": e["id"],
            "Applicant": e["applicant_name"],
            "Workflow": e["workflow_id"],
            "Version": e["workflow_version"],
            "Outcome": e["outcome"],
            "Approval Score": e["approval_score"],
            "Scenario": e["scenario_type"],
            "Executed By": e["executed_by"],
            "Timestamp": e["timestamp"],
            "Replayed": e.get("replayed", False),
            "Immutable": e["immutable"],
        } for e in filtered_export])

        st.markdown(f"<div style='color:#c9a84c;font-size:0.8rem;margin-bottom:0.75rem'>{len(filtered_export)} records ready for export</div>", unsafe_allow_html=True)
        csv_data = export_df.to_csv(index=False)
        st.download_button("DOWNLOAD CSV EXPORT", csv_data, "decision_records_export.csv", "text/csv", use_container_width=True)
        st.dataframe(export_df.head(10), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def page_admin():
    users = st.session_state.users
    st.markdown('<div class="page-hero"><div class="hero-title">System <span>Administration</span></div><div class="hero-sub">Manage user accounts, roles, permissions, and system configuration</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="content-area">', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["User Management", "Create Account", "System Overview"])

    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">User Accounts</div></div>', unsafe_allow_html=True)
        for email, user in users.items():
            uc1, uc2, uc3, uc4 = st.columns([3, 2, 3, 2])
            with uc1:
                status_cls = "status-active" if user["active"] else "status-inactive"
                st.markdown(f"""
                <div style="padding:0.5rem 0">
                    <div style="font-weight:700;color:#e8e8e8;font-size:0.85rem">{user['name']}</div>
                    <div style="color:#7a8099;font-size:0.72rem">{email}</div>
                </div>
                """, unsafe_allow_html=True)
            with uc2:
                st.markdown(f'<div style="padding:0.5rem 0"><span class="status-badge status-review">{user["role"]}</span></div>', unsafe_allow_html=True)
            with uc3:
                st.markdown(f'<div style="padding:0.5rem 0;color:#9aa0b4;font-size:0.72rem">{", ".join(user["permissions"][:3])}{"..." if len(user["permissions"])>3 else ""}</div>', unsafe_allow_html=True)
            with uc4:
                toggle_label = "Disable" if user["active"] else "Enable"
                if st.button(toggle_label, key=f"toggle_{email}"):
                    users[email]["active"] = not user["active"]
                    st.rerun()
            st.markdown('<hr style="border-color:#1e2a3d;margin:0">', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-header"><div class="card-title">Modify Roles & Permissions</div></div>', unsafe_allow_html=True)
        target_user = st.selectbox("Select User to Modify", list(users.keys()))
        if target_user:
            all_perms = ["create_rule","publish_workflow","execute","audit","replay","compare","export","admin","manage_users","view"]
            current_perms = users[target_user]["permissions"]
            new_perms = []
            perm_cols = st.columns(5)
            for i, perm in enumerate(all_perms):
                with perm_cols[i % 5]:
                    if st.checkbox(perm, value=perm in current_perms, key=f"perm_{target_user}_{perm}"):
                        new_perms.append(perm)
            if st.button("UPDATE PERMISSIONS"):
                users[target_user]["permissions"] = new_perms
                st.success(f"Permissions updated for {users[target_user]['name']}")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">Create New User Account</div></div>', unsafe_allow_html=True)
        with st.form("create_user_form"):
            u1, u2 = st.columns(2)
            with u1:
                new_name = st.text_input("Full Name")
                new_email = st.text_input("Email Address")
                new_password = st.text_input("Password", type="password")
            with u2:
                new_role = st.selectbox("Role", ["Decision Analyst", "Business User", "Auditor", "Administrator"])
                new_perms_sel = st.multiselect("Initial Permissions", ["create_rule","publish_workflow","execute","audit","replay","compare","export","admin","manage_users","view"], default=["view","execute"])
            if st.form_submit_button("CREATE ACCOUNT"):
                if new_name and new_email and new_password:
                    if new_email not in users:
                        uid = f"U{str(len(users)+1).zfill(3)}"
                        users[new_email] = {"name": new_name, "role": new_role, "password": hashlib.sha256(new_password.encode()).hexdigest(), "active": True, "id": uid, "permissions": new_perms_sel}
                        st.success(f"Account created for {new_name} ({new_email})")
                    else:
                        st.error("Email already registered.")
                else:
                    st.error("Please complete all required fields.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header"><div class="card-title">System Health Overview</div></div>', unsafe_allow_html=True)
        so1, so2, so3, so4 = st.columns(4)
        so1.metric("Total Users", len(users))
        so2.metric("Active Users", sum(1 for u in users.values() if u["active"]))
        so3.metric("Total Rules", len(st.session_state.rules))
        so4.metric("Total Workflows", len(st.session_state.workflows))

        role_counts = {}
        for u in users.values():
            role_counts[u["role"]] = role_counts.get(u["role"], 0) + 1
        sa1, sa2 = st.columns(2)
        with sa1:
            st.plotly_chart(make_donut(list(role_counts.keys()), list(role_counts.values()), "Roles"), use_container_width=True, config={"displayModeBar": False})
        with sa2:
            wf_status_counts = {}
            for w in st.session_state.workflows:
                wf_status_counts[w["status"]] = wf_status_counts.get(w["status"], 0) + 1
            st.plotly_chart(make_donut(list(wf_status_counts.keys()), list(wf_status_counts.values()), "Workflows"), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def page_login():
    st.markdown("""
    <div style="min-height:100vh;background:linear-gradient(135deg,#080c18 0%,#0d1226 50%,#080c18 100%);display:flex;align-items:center;justify-content:center;flex-direction:column">
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([2, 3, 2])
    with col_b:
        st.markdown("""
        <div style="text-align:center;margin-bottom:2rem;margin-top:3rem">
            <div style="font-size:2.5rem;font-weight:900;color:#c9a84c;letter-spacing:4px;text-transform:uppercase">DPRS</div>
            <div style="font-size:0.68rem;color:#7a8099;letter-spacing:3px;text-transform:uppercase;margin-top:0.25rem">Decision Provenance & Replay Management System</div>
            <div style="width:60px;height:3px;background:linear-gradient(90deg,#c9a84c,transparent);margin:1rem auto 0"></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center;margin-bottom:1.5rem">
            <div style="font-size:1rem;font-weight:700;color:#ffffff;letter-spacing:1px">SECURE ACCESS PORTAL</div>
            <div style="font-size:0.72rem;color:#7a8099;margin-top:0.25rem">Authorized personnel only</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="your@email.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("SIGN IN", use_container_width=True)

        if submitted:
            users = st.session_state.users
            if email in users:
                stored_hash = users[email]["password"]
                input_hash = hashlib.sha256(password.encode()).hexdigest()
                if stored_hash == input_hash:
                    if users[email]["active"]:
                        st.session_state.authenticated = True
                        st.session_state.current_user = {**users[email], "email": email}
                        st.session_state.page = "app"
                        st.session_state.active_tab = "dashboard"
                        st.rerun()
                    else:
                        st.error("Account is disabled. Contact administrator.")
                else:
                    st.error("Invalid credentials. Please try again.")
            else:
                st.error("Account not found.")

        st.markdown('<hr class="login-divider">', unsafe_allow_html=True)
        if st.button("Create New Account", use_container_width=True, key="go_register"):
            st.session_state.page = "register"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center;margin-top:1.5rem">
            <div style="font-size:0.68rem;color:#3a4455;text-transform:uppercase;letter-spacing:2px">Secured System — All Access Logged</div>
        </div>
        """, unsafe_allow_html=True)

def page_register():
    col_a, col_b, col_c = st.columns([2, 3, 2])
    with col_b:
        st.markdown("""
        <div style="text-align:center;margin-bottom:2rem;margin-top:3rem">
            <div style="font-size:2.5rem;font-weight:900;color:#c9a84c;letter-spacing:4px;text-transform:uppercase">DPRS</div>
            <div style="font-size:0.68rem;color:#7a8099;letter-spacing:3px;text-transform:uppercase;margin-top:0.25rem">Create Your Account</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="reg-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center;margin-bottom:1.5rem">
            <div style="font-size:1rem;font-weight:700;color:#ffffff;letter-spacing:1px">REGISTER NEW ACCOUNT</div>
            <div style="font-size:0.72rem;color:#7a8099;margin-top:0.25rem">Complete all fields to create your DPRS account</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("register_form"):
            rc1, rc2 = st.columns(2)
            with rc1:
                r_name = st.text_input("Full Name", placeholder="Your full name")
                r_email = st.text_input("Email Address", placeholder="work@company.com")
            with rc2:
                r_role = st.selectbox("Requested Role", ["Business User", "Decision Analyst", "Auditor"])
                r_dept = st.text_input("Department", placeholder="e.g. Credit Analytics")
            r_pass = st.text_input("Password", type="password", placeholder="Min 8 characters")
            r_pass2 = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
            r_agree = st.checkbox("I acknowledge this is a secured system and all actions are logged")
            reg_submitted = st.form_submit_button("CREATE ACCOUNT", use_container_width=True)

        if reg_submitted:
            if not r_agree:
                st.error("You must acknowledge the system policy.")
            elif r_pass != r_pass2:
                st.error("Passwords do not match.")
            elif len(r_pass) < 8:
                st.error("Password must be at least 8 characters.")
            elif r_email in st.session_state.users:
                st.error("Email already registered.")
            elif not r_name or not r_email:
                st.error("Please complete all required fields.")
            else:
                uid = f"U{str(len(st.session_state.users)+1).zfill(3)}"
                perm_map = {
                    "Business User": ["view","execute"],
                    "Decision Analyst": ["view","execute","create_rule","publish_workflow"],
                    "Auditor": ["view","audit","replay","compare","export"],
                }
                st.session_state.users[r_email] = {
                    "name": r_name,
                    "role": r_role,
                    "password": hashlib.sha256(r_pass.encode()).hexdigest(),
                    "active": True,
                    "id": uid,
                    "permissions": perm_map.get(r_role, ["view"]),
                }
                st.success(f"Account created for {r_name}. Please sign in.")
                time.sleep(1)
                st.session_state.page = "login"
                st.rerun()

        st.markdown('<hr class="login-divider">', unsafe_allow_html=True)
        if st.button("Back to Sign In", use_container_width=True, key="back_login"):
            st.session_state.page = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    st.markdown(STYLE, unsafe_allow_html=True)
    init_state()

    if st.session_state.page == "login" and not st.session_state.authenticated:
        page_login()
        return

    if st.session_state.page == "register":
        page_register()
        return

    if not st.session_state.authenticated:
        page_login()
        return

    render_nav()

    if st.session_state.active_tab == "dashboard":
        page_dashboard()
    elif st.session_state.active_tab == "rules":
        page_rules()
    elif st.session_state.active_tab == "workflows":
        page_workflows()
    elif st.session_state.active_tab == "execute":
        page_execute()
    elif st.session_state.active_tab == "history":
        page_history()
    elif st.session_state.active_tab == "replay":
        page_replay()
    elif st.session_state.active_tab == "audit":
        page_audit()
    elif st.session_state.active_tab == "admin":
        page_admin()

    st.markdown("""
    <div style="background:#080c18;border-top:1px solid #1e2a3d;padding:1rem 2.5rem;margin-top:2rem;display:flex;justify-content:space-between;align-items:center">
        <div style="font-size:0.68rem;color:#3a4455;text-transform:uppercase;letter-spacing:2px">Decision Provenance & Replay Management System — v3.0</div>
        <div style="font-size:0.68rem;color:#3a4455;text-transform:uppercase;letter-spacing:2px">All decision records are immutable and secured</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.authenticated:
        with st.sidebar:
            st.markdown("### Session")
            if st.button("Sign Out"):
                st.session_state.authenticated = False
                st.session_state.current_user = None
                st.session_state.page = "login"
                st.rerun()

if __name__ == "__main__":
    main()