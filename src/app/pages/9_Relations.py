import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import execute_statement, run_query

st.set_page_config(page_title="Relations", page_icon="🔗")

st.header("Manage Relations")

# Fetch data
scientists_df = run_query("SELECT scientist_id, name FROM scientist ORDER BY name")
experiments_df = run_query("SELECT experiment_id, name FROM experiment ORDER BY name")
projects_df = run_query("SELECT project_id, name FROM project ORDER BY name")

scientist_options = {row['name']: row['scientist_id'] for index, row in scientists_df.iterrows()} if scientists_df is not None else {}
experiment_options = {row['name']: row['experiment_id'] for index, row in experiments_df.iterrows()} if experiments_df is not None else {}
project_options = {row['name']: row['project_id'] for index, row in projects_df.iterrows()} if projects_df is not None else {}

tab1, tab2, tab3 = st.tabs(["Scientist-Experiment", "Experiment-Project", "Scientist-Project"])

with tab1:
    st.subheader("Scientist Performed Experiment")
    with st.form("sci_exp_form"):
        sci_name = st.selectbox("Scientist", options=list(scientist_options.keys()), key="se_s")
        exp_name = st.selectbox("Experiment", options=list(experiment_options.keys()), key="se_e")
        submitted = st.form_submit_button("Link Scientist to Experiment")
        
        if submitted:
            if sci_name and exp_name:
                query = "INSERT INTO scientist_performed_experiment (scientist_id, experiment_id) VALUES (%s, %s)"
                if execute_statement(query, (scientist_options[sci_name], experiment_options[exp_name])):
                    st.success("Linked successfully!")
                else:
                    st.error("Failed to link. Relation might already exist.")

    st.subheader("Existing Links")
    df = run_query("""
        SELECT s.name as scientist, e.name as experiment 
        FROM scientist_performed_experiment spe
        JOIN scientist s ON spe.scientist_id = s.scientist_id
        JOIN experiment e ON spe.experiment_id = e.experiment_id
    """)
    if df is not None:
        st.dataframe(df)

with tab2:
    st.subheader("Experiment Contributed to Project")
    with st.form("exp_proj_form"):
        exp_name = st.selectbox("Experiment", options=list(experiment_options.keys()), key="ep_e")
        proj_name = st.selectbox("Project", options=list(project_options.keys()), key="ep_p")
        submitted = st.form_submit_button("Link Experiment to Project")
        
        if submitted:
            if exp_name and proj_name:
                query = "INSERT INTO experiment_contributed_project (experiment_id, project_id) VALUES (%s, %s)"
                if execute_statement(query, (experiment_options[exp_name], project_options[proj_name])):
                    st.success("Linked successfully!")
                else:
                    st.error("Failed to link. Relation might already exist.")

    st.subheader("Existing Links")
    df = run_query("""
        SELECT e.name as experiment, p.name as project
        FROM experiment_contributed_project ecp
        JOIN experiment e ON ecp.experiment_id = e.experiment_id
        JOIN project p ON ecp.project_id = p.project_id
    """)
    if df is not None:
        st.dataframe(df)

with tab3:
    st.subheader("Scientist Member of Project")
    with st.form("sci_proj_form"):
        sci_name = st.selectbox("Scientist", options=list(scientist_options.keys()), key="sp_s")
        proj_name = st.selectbox("Project", options=list(project_options.keys()), key="sp_p")
        submitted = st.form_submit_button("Link Scientist to Project")
        
        if submitted:
            if sci_name and proj_name:
                query = "INSERT INTO scientist_member_project (scientist_id, project_id) VALUES (%s, %s)"
                if execute_statement(query, (scientist_options[sci_name], project_options[proj_name])):
                    st.success("Linked successfully!")
                else:
                    st.error("Failed to link. Relation might already exist.")

    st.subheader("Existing Links")
    df = run_query("""
        SELECT s.name as scientist, p.name as project
        FROM scientist_member_project smp
        JOIN scientist s ON smp.scientist_id = s.scientist_id
        JOIN project p ON smp.project_id = p.project_id
    """)
    if df is not None:
        st.dataframe(df)
