import streamlit as st
import joblib

FEATURE_COLUMNS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal",
]

import json
import os

USERS_FILE = "users.json"

DEFAULT_USERS = {
    "admin": {"password": "password123", "role": "admin"},
    "clinician": {"password": "clin123", "role": "clinician"},
    "analyst": {"password": "analyst123", "role": "analyst"},
}


def load_users():
    """Load the current user store, seeding it with defaults on first run."""
    if not os.path.exists(USERS_FILE):
        save_users(DEFAULT_USERS)
        return DEFAULT_USERS.copy()
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users: dict):
    """Persist the full user store back to users.json."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def add_user(username: str, password: str, role: str):
    """Add a single new user and persist the updated store."""
    users = load_users()
    users[username] = {"password": password, "role": role}
    save_users(users)


@st.cache_resource
def load_artifacts():
    """Load the trained Random Forest model and fitted scaler."""
    # 1. Get the absolute path to the directory where utils.py lives
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Try to load from the current directory first
    try:
        model_path = os.path.join(current_dir, "rf_model.joblib")
        scaler_path = os.path.join(current_dir, "scaler.joblib")
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        return model, scaler
        
    except FileNotFoundError:
        # 3. Fallback: If the files aren't in this folder, check the parent directory (repo root)
        parent_dir = os.path.dirname(current_dir)
        model_path_root = os.path.join(parent_dir, "rf_model.joblib")
        scaler_path_root = os.path.join(parent_dir, "scaler.joblib")
        
        model = joblib.load(model_path_root)
        scaler = joblib.load(scaler_path_root)
        return model, scaler


def require_login():
    """
    Gatekeeper for every page in pages/. If the user hasn't logged in
    via app.py, stop rendering the rest of the page.
    """
    if not st.session_state.get("authenticated", False):
        st.error("🔒 Please log in from the main page first.")
        st.stop()


def require_role(*allowed_roles):
    """
    Gatekeeper for role-restricted pages (e.g. admin-only). Checks login
    first, then checks the logged-in user's role against allowed_roles.
    Usage: require_role("admin")  or  require_role("admin", "analyst")
    """
    require_login()
    if st.session_state.get("role") not in allowed_roles:
        st.error(
            f"🚫 Access Denied — this page is restricted to: {', '.join(allowed_roles)}. "
            f"Your role: {st.session_state.get('role', 'unknown')}."
        )
        st.stop()


def inject_custom_css():
    """
    Global styling applied on every page. Call once, right after
    st.set_page_config(), at the top of every page file (and app.py).
    Matches the neon login page: Inter font, pill-shaped controls, one
    fixed neon-blue accent color used consistently across the whole app.
    """
    ACCENT = "#00d2ff"

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif !important;
        }}

        /* Metric cards: dark card background, neon-accented border, rounded corners */
        div[data-testid="stMetric"] {{
            background-color: #12161f;
            border: 1px solid {ACCENT}55;
            padding: 16px 18px;
            border-radius: 14px;
            box-shadow: 0 2px 10px rgba(0,210,255,0.08);
        }}
        div[data-testid="stMetric"] label {{
            color: #9BA8BC !important;
        }}
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
            color: {ACCENT} !important;
        }}

        /* Pill-shaped text inputs, matching the login page */
        div[data-baseweb="input"], div[data-baseweb="select"] {{
            border-radius: 50px !important;
            border: 2px solid {ACCENT}88 !important;
            background-color: transparent !important;
        }}
        div[data-baseweb="input"] > input {{
            color: white !important;
            letter-spacing: 0.5px;
        }}

        /* Primary action buttons (Predict CVD Risk, Log In, etc.) */
        button[kind="primary"] {{
            border-radius: 50px !important;
            border: 2px solid {ACCENT} !important;
            color: {ACCENT} !important;
            background: transparent !important;
            font-weight: 800 !important;
            letter-spacing: 1.5px;
            transition: all 0.25s ease;
        }}
        button[kind="primary"]:hover {{
            background-color: {ACCENT} !important;
            color: #0a0e14 !important;
            box-shadow: 0 0 16px {ACCENT}66;
        }}

        /* Secondary buttons (demo presets, downloads, etc.) */
        button[kind="secondary"], .stDownloadButton > button {{
            border-radius: 50px !important;
            border: 1px solid #444 !important;
            background: transparent !important;
            color: #ccc !important;
            font-weight: 600 !important;
            transition: 0.25s;
        }}
        button[kind="secondary"]:hover, .stDownloadButton > button:hover {{
            border-color: {ACCENT} !important;
            color: {ACCENT} !important;
        }}

        /* Tabs — rounded top corners, neon accent on the active tab */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px;
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 10px 10px 0 0;
            padding: 10px 18px;
            background-color: #12161f;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {ACCENT}22 !important;
            color: {ACCENT} !important;
            border-bottom: 2px solid {ACCENT} !important;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: #0a0e14;
            border-right: 1px solid {ACCENT}33;
        }}

        /* Dataframes / tables: rounded corners */
        div[data-testid="stDataFrame"] {{
            border-radius: 10px;
            overflow: hidden;
        }}

        /* Cards used for the risk banner and similar custom containers */
        .risk-card {{
            border-radius: 14px;
            padding: 22px;
            text-align: center;
            margin: 14px 0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def clinical_disclaimer():
    """No-op — disclaimer removed. Kept as a function so existing calls
    to clinical_disclaimer() across app.py and pages/*.py don't break."""
    pass