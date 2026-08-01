import streamlit as st
import pandas as pd
from utils import require_role, clinical_disclaimer, inject_custom_css, load_users, add_user

st.set_page_config(page_title="User Management", page_icon="👥", layout="wide")
inject_custom_css()

# Only admins may manage users
require_role("admin")

st.title("👥 User Management")
st.write("Add new portal accounts and assign their role.")
st.caption(
    "Accounts are stored server-side and persist for the life of this app's "
    "session/container. This is a prototype user store, not a production "
    "database — a real deployment would use hashed passwords in a proper "
    "database rather than a flat file."
)

users = load_users()

st.subheader("Current Users")
users_df = pd.DataFrame([
    {"Username": username, "Role": info["role"]}
    for username, info in users.items()
])
st.dataframe(users_df, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Add New User")

with st.form("add_user_form"):
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    new_role = st.selectbox("Role", options=["clinician", "analyst", "admin"])
    submitted = st.form_submit_button("Add User", type="primary", use_container_width=True)

    if submitted:
        if not new_username or not new_password:
            st.error("Username and password are required.")
        elif new_username in users:
            st.error(f"Username '{new_username}' already exists.")
        else:
            add_user(new_username, new_password, new_role)
            st.success(f"User '{new_username}' added with role '{new_role}'.")
            st.rerun()

clinical_disclaimer()