import streamlit as st
import uuid
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import execute_statement, run_query

st.set_page_config(page_title="Project", page_icon="📁")

st.header("Manage Projects")

# Form to add a new project
st.subheader("Add New Project")
with st.form("add_project_form"):
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
