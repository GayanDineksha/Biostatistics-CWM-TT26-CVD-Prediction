import streamlit as st
from utils import require_login, clinical_disclaimer, inject_custom_css

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
inject_custom_css()
require_login()

# --- TYPOGRAPHY & CUSTOM CSS ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
        }

        .dash-title {
            font-size: 42px;
            font-weight: 800;
            color: white;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        .dash-subtitle {
            font-size: 18px;
            font-weight: 400;
            color: #00d2ff;
            margin-bottom: 35px;
            letter-spacing: 0.5px;
        }
        .section-header {
            font-size: 24px;
            font-weight: 700;
            color: #f8f9fa;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
            margin-top: 45px;
            margin-bottom: 25px;
        }
        .body-text {
            font-size: 17px;
            font-weight: 300;
            color: #e0e0e0;
            line-height: 1.6;
        }

        /* Unified Professional Static Cards */
        .feature-card {
            background-color: #1a1c23;
            border: 1px solid #333;
            border-radius: 12px;
            padding: 30px 25px;
            height: 100%;
            margin-bottom: 10px; /* Space between card and button */
        }
        .card-icon { font-size: 36px; margin-bottom: 15px; }
        .card-title { font-size: 22px; font-weight: 700; margin-bottom: 10px; }
        .color-blue { color: #00d2ff; }
        .color-yellow { color: #ffca28; }
        .color-purple { color: #b388ff; }
        .card-desc { font-size: 16px; font-weight: 400; color: #a0a0a0; line-height: 1.5; }
        
        /* Sleek Enterprise Navigation Buttons */
        div.stButton > button {
            background-color: transparent !important;
            border: 1px solid #444 !important;
            border-radius: 8px !important;
            color: #ccc !important;
            font-weight: 600 !important;
            padding: 12px 0px !important; 
            transition: all 0.3s ease !important;
        }
        div.stButton > button:hover {
            background-color: #1a1c23 !important;
            border-color: white !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(255,255,255,0.05) !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- WELCOME BANNER ---
username = st.session_state.get('username', 'Doctor').title()
st.markdown("<div class='dash-title'>🏠 System Dashboard</div>", unsafe_allow_html=True)
st.markdown(f"<div class='dash-subtitle'>Welcome to the portal, {username}.</div>", unsafe_allow_html=True)

# --- METRICS SECTION ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Random Forest Accuracy", "81.63%")
with col2:
    st.metric("Random Forest ROC-AUC", "0.888")
with col3:
    st.metric("Neural Network ROC-AUC", "0.899")

# --- ABOUT / NAVIGATION CARDS ---
st.markdown("<div class='section-header'>Clinical Portal Capabilities</div>", unsafe_allow_html=True)
st.markdown(
    "<p class='body-text'>This portal is powered by a <b>Random Forest Classifier</b> trained on the "
    "Cleveland Heart Disease dataset (242 patients, 13 clinical features) to estimate real-time cardiovascular disease risk.</p><br>",
    unsafe_allow_html=True
)

# --- CARDS & BULLETPROOF ROUTING ---
card_col1, card_col2, card_col3 = st.columns(3)

with card_col1:
    st.markdown("""
        <div class='feature-card'>
            <div class='card-icon'>🩺</div>
            <div class='card-title color-blue'>Single Patient Screening</div>
            <div class='card-desc'>Enter an individual patient's clinical vitals to receive an instant, probabilistic risk estimate.</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Single Patient Screening &rarr;", key="btn_single", use_container_width=True):
        st.switch_page("pages/Single_Patient_Screening.py")

with card_col2:
    st.markdown("""
        <div class='feature-card'>
            <div class='card-icon'>📁</div>
            <div class='card-title color-yellow'>Batch Processing</div>
            <div class='card-desc'>Upload a CSV containing multiple patients to execute high-throughput bulk risk screening.</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Batch Processin &rarr;", key="btn_batch", use_container_width=True):
        st.switch_page("pages/Batch_Processing.py")

with card_col3:
    st.markdown("""
        <div class='feature-card'>
            <div class='card-icon'>📊</div>
            <div class='card-title color-purple'>Model Analytics</div>
            <div class='card-desc'>Review exploratory data analysis, dataset distributions, and evaluation charts.</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Model Analytics &rarr;", key="btn_analytics", use_container_width=True):
        st.switch_page("pages/Model_Analytics.py")

# --- RECENT ACTIVITY SECTION ---
st.markdown("<div class='section-header'>Recent System Activity</div>", unsafe_allow_html=True)

log = st.session_state.get("screening_log", [])
if log:
    st.success(f"✅ **{len(log)} screening(s)** recorded during this active session.")
else:
    st.warning("⚠️ No screenings recorded yet this session. Launch the Single Patient Screening module to begin.")

st.markdown("<br><br>", unsafe_allow_html=True)

# --- FOOTER ---
clinical_disclaimer()