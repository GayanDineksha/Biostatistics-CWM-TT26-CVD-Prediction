import streamlit as st
import pandas as pd
from utils import require_login, clinical_disclaimer, load_artifacts, FEATURE_COLUMNS, inject_custom_css

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Batch Processing", page_icon="📁", layout="wide")
inject_custom_css()
require_login()

# --- TYPOGRAPHY & CUSTOM CSS ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
        }

        /* Page Headers */
        .page-title {
            font-size: 42px;
            font-weight: 800;
            color: white;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        .page-subtitle {
            font-size: 18px;
            font-weight: 400;
            color: #ffca28; /* Golden Yellow to match Dashboard card */
            margin-bottom: 30px;
            letter-spacing: 0.5px;
        }
        
        /* Custom KPI Cards */
        .kpi-container {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            margin-top: 10px;
        }
        .kpi-card {
            background-color: #1a1c23;
            border: 1px solid #333;
            border-radius: 12px;
            padding: 25px 20px;
            text-align: center;
            flex: 1;
            transition: transform 0.3s ease, border-color 0.3s ease;
        }
        .kpi-card:hover {
            border-color: #ffca28;
            transform: translateY(-3px);
        }
        .kpi-value {
            font-size: 42px;
            font-weight: 800;
            margin-bottom: 5px;
            line-height: 1;
        }
        .kpi-label {
            font-size: 14px;
            font-weight: 600;
            color: #aaa;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Specific KPI Colors */
        .val-total { color: #00d2ff; }   /* Neon Blue */
        .val-danger { color: #ff1744; }  /* Neon Red */
        .val-safe { color: #00e676; }    /* Neon Green */

        /* Styled Download Buttons */
        div.stDownloadButton > button {
            background-color: #1a1c23 !important;
            border: 1px solid #444 !important;
            border-radius: 8px !important;
            color: #e0e0e0 !important;
            font-weight: 600 !important;
            padding: 15px 0px !important; 
            transition: all 0.3s ease !important;
        }
        div.stDownloadButton > button:hover {
            border-color: #ffca28 !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(255, 202, 40, 0.1) !important;
        }
        
        /* Sub-headers */
        .section-header {
            font-size: 20px;
            font-weight: 700;
            color: #f8f9fa;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
            margin-top: 30px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- PAGE HEADER ---
st.markdown("<div class='page-title'>📁 Batch Patient Processing</div>", unsafe_allow_html=True)
st.markdown("<div class='page-subtitle'>High-Throughput Clinical Risk Screening Module</div>", unsafe_allow_html=True)

st.write("Upload a unified CSV file containing multiple patient records to execute bulk screening. The system will process the cohort and generate probabilistic cardiovascular risk assessments for all individuals simultaneously.")

# Clean up the required columns UI by placing it in an expander
with st.expander("View Required Clinical Feature Columns", expanded=False):
    st.code(", ".join(FEATURE_COLUMNS), language="text")

# --- MODEL LOADING & FILE UPLOAD ---
model, scaler = load_artifacts()

st.markdown("<br>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Select Patient CSV Data", type=["csv"])

# --- PROCESSING LOGIC ---
if uploaded_file is not None:
    try:
        with st.spinner("Processing patient cohort..."):
            batch_df = pd.read_csv(uploaded_file)
            missing_cols = [c for c in FEATURE_COLUMNS if c not in batch_df.columns]

            if missing_cols:
                st.error(f"**Validation Error:** Uploaded file is missing required columns: `{missing_cols}`")
            else:
                # Extract and scale features
                X_batch = batch_df[FEATURE_COLUMNS]
                X_batch_scaled = scaler.transform(X_batch)

                # Predictions
                probs = model.predict_proba(X_batch_scaled)[:, 1]
                preds = model.predict(X_batch_scaled)

                # Append results
                results = batch_df.copy()
                results["cvd_risk_probability"] = probs.round(4)
                results["cvd_prediction"] = preds
                
                total_patients = len(results)
                cvd_cases = int(preds.sum())
                healthy_cases = total_patients - cvd_cases

                # --- CUSTOM KPI DASHBOARD ---
                st.markdown(f"""
                    <div class="kpi-container">
                        <div class="kpi-card">
                            <div class="kpi-value val-total">{total_patients}</div>
                            <div class="kpi-label">Total Processed</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-value val-danger">{cvd_cases}</div>
                            <div class="kpi-label">Predicted CVD Risk</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-value val-safe">{healthy_cases}</div>
                            <div class="kpi-label">Predicted Healthy</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # --- DATA DISPLAY ---
                st.markdown("<div class='section-header'>Processed Cohort Data</div>", unsafe_allow_html=True)
                st.dataframe(results, use_container_width=True)

                # --- EXPORT PREPARATION ---
                csv_out = results.to_csv(index=False).encode("utf-8")

                # Kaggle-format export: Patient_ID + binary prediction
                if "id" in batch_df.columns:
                    patient_ids = batch_df["id"]
                else:
                    patient_ids = range(1, len(results) + 1)

                kaggle_df = pd.DataFrame({
                    "Patient_ID": patient_ids,
                    "target": preds,
                })
                kaggle_csv = kaggle_df.to_csv(index=False).encode("utf-8")

                st.markdown("<br>", unsafe_allow_html=True)
                
                # --- EXPORT BUTTONS ---
                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    st.download_button(
                        "⬇️ Download Full Results (CSV)",
                        data=csv_out,
                        file_name="batch_screening_results.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
                with col_dl2:
                    st.download_button(
                        "📥 Export Kaggle Submission (CSV)",
                        data=kaggle_csv,
                        file_name="kaggle_submission.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
                    
    except Exception as e:
        st.error(f"**System Error:** Failed to process file. ({e})")
else:
    st.info("Awaiting CSV upload. Please select a file to begin batch processing.")

st.markdown("<br><br>", unsafe_allow_html=True)

# --- FOOTER ---
clinical_disclaimer()