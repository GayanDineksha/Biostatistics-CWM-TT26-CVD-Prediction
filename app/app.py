import streamlit as st
import time
from utils import inject_custom_css, load_users

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="CVD Clinical Portal", page_icon="🩺", layout="wide")

# --- SESSION STATE INITIALIZATION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "active_role" not in st.session_state:
    st.session_state.active_role = "Clinician"


def login_page():
    inject_custom_css()

    theme_colors = {
        "Clinician": "#00d2ff",
        "Analyst": "#00e676",
        "Admin": "#ff1744",
    }
    active_color = theme_colors[st.session_state.active_role]

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}

        div[data-baseweb="input"] {{
            border-radius: 50px !important;
            border: 2px solid {active_color} !important;
            background-color: transparent !important;
            margin-bottom: 12px;
        }}
        div[data-baseweb="input"] > input {{
            text-align: center !important;
            color: white !important;
            font-size: 16px !important;
            font-weight: 400 !important;
            letter-spacing: 1px;
        }}

        button[kind="primary"] {{
            border-radius: 50px !important;
            border: 2px solid {active_color} !important;
            color: {active_color} !important;
            background: transparent !important;
            font-weight: 800 !important;
            font-size: 18px !important;
            letter-spacing: 2px;
            transition: all 0.3s ease;
        }}
        button[kind="primary"]:hover {{
            background-color: {active_color} !important;
            color: #111 !important;
        }}

        button[kind="secondary"] {{
            border-radius: 50px !important;
            border: 1px solid #444 !important;
            background: transparent !important;
            color: #ccc !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            transition: 0.3s;
        }}
        button[kind="secondary"]:hover {{
            border-color: white !important;
            color: white !important;
        }}

        .login-title {{
            text-align: center;
            letter-spacing: 6px;
            font-weight: 800;
            font-size: 46px;
            margin-bottom: 5px;
            color: white;
        }}
        .auth-subtitle {{
            text-align: center;
            color: {active_color};
            font-weight: 600;
            font-size: 18px;
            letter-spacing: 1px;
            margin-top: 30px;
            margin-bottom: 25px;
        }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    col_left, col_center, col_right = st.columns([1, 1.2, 1])

    with col_center:
        st.markdown("<div class='login-title'>LOGIN</div>", unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align: center; color: #666; font-size: 14px; margin-bottom: 25px;'>"
            "Select a role theme, then enter your credentials</p>",
            unsafe_allow_html=True,
        )

        role_col1, role_col2, role_col3 = st.columns(3)
        with role_col1:
            if st.button("🩺 Clinician", use_container_width=True):
                st.session_state.active_role = "Clinician"
                st.rerun()
        with role_col2:
            if st.button("📊 Analyst", use_container_width=True):
                st.session_state.active_role = "Analyst"
                st.rerun()
        with role_col3:
            if st.button("🛡️ Admin", use_container_width=True):
                st.session_state.active_role = "Admin"
                st.rerun()

        st.markdown(
            f"<div class='auth-subtitle'>{st.session_state.active_role} Authentication</div>",
            unsafe_allow_html=True,
        )

        username = st.text_input("Username", placeholder="Username", label_visibility="collapsed")
        password = st.text_input("Password", placeholder="Password", type="password", label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)

        col_btn_l, col_btn_c, col_btn_r = st.columns([1, 2, 1])
        with col_btn_c:
            if st.button("Login", type="primary", use_container_width=True):
                if not username or not password:
                    st.error("Please enter credentials.")
                else:
                    users = load_users()
                    user_record = users.get(username)
                    if user_record and user_record["password"] == password:
                        with st.spinner("Authenticating..."):
                            time.sleep(0.6)
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.role = user_record["role"]
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")


# ---------------------------------------------------------------
# ROUTING
# ---------------------------------------------------------------
if not st.session_state.authenticated:
    # No sidebar at all while logged out — position="hidden" removes the
    # nav widget entirely rather than just hiding it with CSS.
    pg = st.navigation([st.Page(login_page, title="Login")], position="hidden")
    pg.run()
else:
    dashboard = st.Page("pages/Dashboard.py", title="Dashboard", icon="🏠", default=True)
    screening = st.Page("pages/Single_Patient_Screening.py", title="Single Patient Screening", icon="🩺")
    batch = st.Page("pages/Batch_Processing.py", title="Batch Processing", icon="📁")
    analytics = st.Page("pages/Model_Analytics.py", title="Model Analytics", icon="📊")
    audit = st.Page("pages/System_Audit.py", title="System Audit", icon="🛡️")
    user_mgmt = st.Page("pages/User_Management.py", title="User Management", icon="👥")
    logout = st.Page("pages/Logout.py", title="Log out", icon="🚪")

    # Sidebar order is exactly the order of this list — role-filtered so
    # clinicians/analysts never even see admin-only links.
    pages = [dashboard, screening, batch, analytics]
    if st.session_state.get("role") == "admin":
        pages += [audit, user_mgmt]
    pages.append(logout)

    pg = st.navigation(pages)
    pg.run()