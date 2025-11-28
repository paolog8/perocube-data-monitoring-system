import streamlit as st
import uuid
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import execute_statement, run_query
from src.app.ui_utils import get_delete_warning_html

st.set_page_config(page_title="Project", page_icon="📁")

st.header("Manage Projects")

# Form to add a new project
st.subheader("Add New Project")
with st.form("add_project_form", enter_to_submit=False):
    name = st.text_input("Name")
    submitted = st.form_submit_button("Add Project")
    
    if submitted:
        if name:
            project_id = str(uuid.uuid4())
            query = "INSERT INTO project (project_id, name) VALUES (%s, %s)"
            if execute_statement(query, (project_id, name)):
                st.success(f"Project '{name}' added successfully!")
            else:
                st.error("Failed to add project. Name might already exist.")
        else:
            st.warning("Please enter a name.")

# List existing projects
st.subheader("Existing Projects")
df = run_query("SELECT * FROM project ORDER BY name")
if df is not None:
    st.dataframe(df)
else:
    st.error("Failed to load projects.")

st.markdown("---")
st.subheader("Delete Project")

# Prepare options for delete
project_options_del = {row['name']: row['project_id'] for index, row in df.iterrows()} if df is not None else {}

with st.form("delete_project_form", enter_to_submit=False):
    delete_name = st.selectbox("Select Project to Delete", options=[""] + list(project_options_del.keys()))
    delete_submitted = st.form_submit_button("Delete Project")

if delete_submitted and delete_name:
    st.session_state['delete_project_name'] = delete_name
    st.session_state['delete_project_id'] = project_options_del[delete_name]
    st.session_state['confirm_delete_project'] = True

if st.session_state.get('confirm_delete_project'):
    st.markdown(get_delete_warning_html(st.session_state['delete_project_name']), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete Project"):
            query = "DELETE FROM project WHERE project_id = %s"
            if execute_statement(query, (st.session_state['delete_project_id'],)):
                st.success(f"Project '{st.session_state['delete_project_name']}' deleted successfully!")
                # Clear state
                del st.session_state['confirm_delete_project']
                del st.session_state['delete_project_name']
                del st.session_state['delete_project_id']
                st.rerun()
            else:
                st.error("Failed to delete project. It might be referenced by other records.")
    with col2:
        if st.button("Cancel Delete"):
            del st.session_state['confirm_delete_project']
            if 'delete_project_name' in st.session_state: del st.session_state['delete_project_name']
            if 'delete_project_id' in st.session_state: del st.session_state['delete_project_id']
            st.rerun()
