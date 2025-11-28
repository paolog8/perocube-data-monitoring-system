import streamlit as st
import uuid
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import execute_statement, run_query
from src.app.ui_utils import get_delete_warning_html

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

st.markdown("---")
st.subheader("Delete Experiment")

# Prepare options for delete
experiment_options_del = {row['name']: row['experiment_id'] for index, row in df.iterrows()} if df is not None else {}

with st.form("delete_experiment_form", enter_to_submit=False):
    delete_name = st.selectbox("Select Experiment to Delete", options=[""] + list(experiment_options_del.keys()))
    delete_submitted = st.form_submit_button("Delete Experiment")

if delete_submitted and delete_name:
    st.session_state['delete_experiment_name'] = delete_name
    st.session_state['delete_experiment_id'] = experiment_options_del[delete_name]
    st.session_state['confirm_delete_experiment'] = True

if st.session_state.get('confirm_delete_experiment'):
    st.markdown(get_delete_warning_html(st.session_state['delete_experiment_name']), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete Experiment"):
            query = "DELETE FROM experiment WHERE experiment_id = %s"
            if execute_statement(query, (st.session_state['delete_experiment_id'],)):
                st.success(f"Experiment '{st.session_state['delete_experiment_name']}' deleted successfully!")
                # Clear state
                del st.session_state['confirm_delete_experiment']
                del st.session_state['delete_experiment_name']
                del st.session_state['delete_experiment_id']
                st.rerun()
            else:
                st.error("Failed to delete experiment. It might be referenced by other records.")
    with col2:
        if st.button("Cancel Delete"):
            del st.session_state['confirm_delete_experiment']
            if 'delete_experiment_name' in st.session_state: del st.session_state['delete_experiment_name']
            if 'delete_experiment_id' in st.session_state: del st.session_state['delete_experiment_id']
            st.rerun()
