import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import execute_statement, run_query

st.set_page_config(page_title="Solar Cell Pixel", page_icon="🔳")

st.header("Manage Solar Cell Pixels")

# Fetch devices for dropdown
devices_df = run_query("SELECT name FROM solar_cell_device ORDER BY name")
device_options = devices_df['name'].tolist() if devices_df is not None else []

# Form to add a new pixel
st.subheader("Add New Pixel")
with st.form("add_pixel_form", enter_to_submit=False):
    solar_cell_id = st.selectbox("Solar Cell Device", options=device_options)
    pixel = st.text_input("Pixel Identifier")
    active_area = st.number_input("Active Area", min_value=0.0, format="%.4f")
    
    submitted = st.form_submit_button("Add Pixel")
    
    if submitted:
        if solar_cell_id and pixel:
            query = """
                INSERT INTO solar_cell_pixel (solar_cell_id, pixel, active_area)
                VALUES (%s, %s, %s)
            """
            if execute_statement(query, (solar_cell_id, pixel, active_area)):
                st.success(f"Pixel '{pixel}' for device '{solar_cell_id}' added successfully!")
            else:
                st.error("Failed to add pixel. Combination might already exist.")
        else:
            st.warning("Please select a device and enter a pixel identifier.")

# List existing pixels
st.subheader("Existing Pixels")
df = run_query("SELECT * FROM solar_cell_pixel ORDER BY solar_cell_id, pixel")
if df is not None:
    st.dataframe(df)
else:
    st.error("Failed to load pixels.")
