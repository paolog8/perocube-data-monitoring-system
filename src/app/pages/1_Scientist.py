import streamlit as st
import uuid
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import execute_statement, run_query
from src.app.ui_utils import get_delete_warning_html

st.set_page_config(page_title="Scientist", page_icon="🧑‍🔬")

st.header("Manage Scientists")

# Form to add a new scientist
st.subheader("Add New Scientist")
with st.form("add_scientist_form", enter_to_submit=False):
    name = st.text_input("Name")
    submitted = st.form_submit_button("Add Scientist")
    
    if submitted:
        if name:
            scientist_id = str(uuid.uuid4())
            query = "INSERT INTO scientist (scientist_id, name) VALUES (%s, %s)"
            if execute_statement(query, (scientist_id, name)):
                st.success(f"Scientist '{name}' added successfully!")
            else:
                st.error("Failed to add scientist. Name might already exist.")
        else:
            st.warning("Please enter a name.")

# List existing scientists
st.subheader("Existing Scientists")
df = run_query("SELECT * FROM scientist ORDER BY name")
if df is not None:
    st.dataframe(df)
else:
    st.error("Failed to load scientists.")

st.markdown("---")
st.subheader("Delete Scientist")

# Prepare options for delete
scientist_options_del = {row['name']: row['scientist_id'] for index, row in df.iterrows()} if df is not None else {}

with st.form("delete_scientist_form", enter_to_submit=False):
    delete_name = st.selectbox("Select Scientist to Delete", options=[""] + list(scientist_options_del.keys()))
    delete_submitted = st.form_submit_button("Delete Scientist")

if delete_submitted and delete_name:
    st.session_state['delete_scientist_name'] = delete_name
    st.session_state['delete_scientist_id'] = scientist_options_del[delete_name]
    st.session_state['confirm_delete_scientist'] = True

if st.session_state.get('confirm_delete_scientist'):
    st.markdown(get_delete_warning_html(st.session_state['delete_scientist_name']), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete Scientist"):
            query = "DELETE FROM scientist WHERE scientist_id = %s"
            if execute_statement(query, (st.session_state['delete_scientist_id'],)):
                st.success(f"Scientist '{st.session_state['delete_scientist_name']}' deleted successfully!")
                # Clear state
                del st.session_state['confirm_delete_scientist']
                del st.session_state['delete_scientist_name']
                del st.session_state['delete_scientist_id']
                st.rerun()
            else:
                st.error("Failed to delete scientist. It might be referenced by other records (e.g., experiments, projects).")
    with col2:
        if st.button("Cancel Delete"):
            del st.session_state['confirm_delete_scientist']
            if 'delete_scientist_name' in st.session_state: del st.session_state['delete_scientist_name']
            if 'delete_scientist_id' in st.session_state: del st.session_state['delete_scientist_id']
            st.rerun()
