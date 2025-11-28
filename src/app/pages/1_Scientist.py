import streamlit as st
import uuid
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import execute_statement, run_query

st.set_page_config(page_title="Scientist", page_icon="🧑‍🔬")

st.header("Manage Scientists")

# Form to add a new scientist
st.subheader("Add New Scientist")
with st.form("add_scientist_form"):
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
