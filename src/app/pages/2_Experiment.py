import streamlit as st
import uuid
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import execute_statement, run_query

st.set_page_config(page_title="Experiment", page_icon="🧪")

st.header("Manage Experiments")

# Form to add a new experiment
st.subheader("Add New Experiment")
with st.form("add_experiment_form", enter_to_submit=False):
    name = st.text_input("Name")
    start_date = st.date_input("Start Date", value=None)
    end_date = st.date_input("End Date", value=None)
    submitted = st.form_submit_button("Add Experiment")
    
    if submitted:
        if name:
            experiment_id = str(uuid.uuid4())
            query = """
                INSERT INTO experiment (experiment_id, name, start_date, end_date) 
                VALUES (%s, %s, %s, %s)
            """
            if execute_statement(query, (experiment_id, name, start_date, end_date)):
                st.success(f"Experiment '{name}' added successfully!")
            else:
                st.error("Failed to add experiment. Name might already exist.")
        else:
            st.warning("Please enter a name.")

# List existing experiments
st.subheader("Existing Experiments")
df = run_query("SELECT * FROM experiment ORDER BY start_date DESC")
if df is not None:
    st.dataframe(df)
else:
    st.error("Failed to load experiments.")
