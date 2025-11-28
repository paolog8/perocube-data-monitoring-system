import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import execute_statement, run_query
from src.app.ui_utils import get_delete_warning_html

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

st.markdown("---")
st.subheader("Delete Pixel")

# Prepare options for delete
pixel_options_del = [f"{row['solar_cell_id']} - {row['pixel']}" for index, row in df.iterrows()] if df is not None else []

with st.form("delete_pixel_form", enter_to_submit=False):
    delete_selection = st.selectbox("Select Pixel to Delete", options=[""] + pixel_options_del)
    delete_submitted = st.form_submit_button("Delete Pixel")

if delete_submitted and delete_selection:
    st.session_state['delete_pixel_selection'] = delete_selection
    st.session_state['confirm_delete_pixel'] = True

if st.session_state.get('confirm_delete_pixel'):
    st.markdown(get_delete_warning_html(st.session_state['delete_pixel_selection']), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete Pixel"):
            solar_cell_id, pixel = st.session_state['delete_pixel_selection'].split(" - ", 1)
            query = "DELETE FROM solar_cell_pixel WHERE solar_cell_id = %s AND pixel = %s"
            if execute_statement(query, (solar_cell_id, pixel)):
                st.success(f"Pixel '{st.session_state['delete_pixel_selection']}' deleted successfully!")
                # Clear state
                del st.session_state['confirm_delete_pixel']
                del st.session_state['delete_pixel_selection']
                st.rerun()
            else:
                st.error("Failed to delete pixel. It might be referenced by other records.")
    with col2:
        if st.button("Cancel Delete"):
            del st.session_state['confirm_delete_pixel']
            if 'delete_pixel_selection' in st.session_state: del st.session_state['delete_pixel_selection']
            st.rerun()
