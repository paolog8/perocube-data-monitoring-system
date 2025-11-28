import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import execute_statement, run_query
from src.app.ui_utils import get_delete_warning_html

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
    with st.form("sci_exp_form", enter_to_submit=False):
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
        SELECT s.name as scientist, e.name as experiment, s.scientist_id, e.experiment_id
        FROM scientist_performed_experiment spe
        JOIN scientist s ON spe.scientist_id = s.scientist_id
        JOIN experiment e ON spe.experiment_id = e.experiment_id
    """)
    if df is not None:
        st.dataframe(df[['scientist', 'experiment']])

    st.markdown("---")
    st.subheader("Delete Link")
    
    # Prepare options
    se_options_del = {f"{row['scientist']} - {row['experiment']}": (row['scientist_id'], row['experiment_id']) for index, row in df.iterrows()} if df is not None else {}
    
    with st.form("delete_se_form", enter_to_submit=False):
        delete_se_sel = st.selectbox("Select Link to Delete", options=[""] + list(se_options_del.keys()))
        delete_se_sub = st.form_submit_button("Delete Link")
        
    if delete_se_sub and delete_se_sel:
        st.session_state['delete_se_sel'] = delete_se_sel
        st.session_state['delete_se_ids'] = se_options_del[delete_se_sel]
        st.session_state['confirm_delete_se'] = True
        
    if st.session_state.get('confirm_delete_se'):
        st.markdown(get_delete_warning_html(st.session_state['delete_se_sel']), unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, Delete", key="del_se_yes"):
                sid, eid = st.session_state['delete_se_ids']
                if execute_statement("DELETE FROM scientist_performed_experiment WHERE scientist_id=%s AND experiment_id=%s", (sid, eid)):
                    st.success("Deleted!")
                    del st.session_state['confirm_delete_se']
                    del st.session_state['delete_se_sel']
                    del st.session_state['delete_se_ids']
                    st.rerun()
                else:
                    st.error("Failed.")
        with c2:
            if st.button("Cancel", key="del_se_no"):
                del st.session_state['confirm_delete_se']
                st.rerun()

with tab2:
    st.subheader("Experiment Contributed to Project")
    with st.form("exp_proj_form", enter_to_submit=False):
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
        SELECT e.name as experiment, p.name as project, e.experiment_id, p.project_id
        FROM experiment_contributed_project ecp
        JOIN experiment e ON ecp.experiment_id = e.experiment_id
        JOIN project p ON ecp.project_id = p.project_id
    """)
    if df is not None:
        st.dataframe(df[['experiment', 'project']])

    st.markdown("---")
    st.subheader("Delete Link")
    
    ep_options_del = {f"{row['experiment']} - {row['project']}": (row['experiment_id'], row['project_id']) for index, row in df.iterrows()} if df is not None else {}
    
    with st.form("delete_ep_form", enter_to_submit=False):
        delete_ep_sel = st.selectbox("Select Link to Delete", options=[""] + list(ep_options_del.keys()))
        delete_ep_sub = st.form_submit_button("Delete Link")
        
    if delete_ep_sub and delete_ep_sel:
        st.session_state['delete_ep_sel'] = delete_ep_sel
        st.session_state['delete_ep_ids'] = ep_options_del[delete_ep_sel]
        st.session_state['confirm_delete_ep'] = True
        
    if st.session_state.get('confirm_delete_ep'):
        st.markdown(get_delete_warning_html(st.session_state['delete_ep_sel']), unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, Delete", key="del_ep_yes"):
                eid, pid = st.session_state['delete_ep_ids']
                if execute_statement("DELETE FROM experiment_contributed_project WHERE experiment_id=%s AND project_id=%s", (eid, pid)):
                    st.success("Deleted!")
                    del st.session_state['confirm_delete_ep']
                    del st.session_state['delete_ep_sel']
                    del st.session_state['delete_ep_ids']
                    st.rerun()
                else:
                    st.error("Failed.")
        with c2:
            if st.button("Cancel", key="del_ep_no"):
                del st.session_state['confirm_delete_ep']
                st.rerun()

with tab3:
    st.subheader("Scientist Member of Project")
    with st.form("sci_proj_form", enter_to_submit=False):
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
        SELECT s.name as scientist, p.name as project, s.scientist_id, p.project_id
        FROM scientist_member_project smp
        JOIN scientist s ON smp.scientist_id = s.scientist_id
        JOIN project p ON smp.project_id = p.project_id
    """)
    if df is not None:
        st.dataframe(df[['scientist', 'project']])

    st.markdown("---")
    st.subheader("Delete Link")
    
    sp_options_del = {f"{row['scientist']} - {row['project']}": (row['scientist_id'], row['project_id']) for index, row in df.iterrows()} if df is not None else {}
    
    with st.form("delete_sp_form", enter_to_submit=False):
        delete_sp_sel = st.selectbox("Select Link to Delete", options=[""] + list(sp_options_del.keys()))
        delete_sp_sub = st.form_submit_button("Delete Link")
        
    if delete_sp_sub and delete_sp_sel:
        st.session_state['delete_sp_sel'] = delete_sp_sel
        st.session_state['delete_sp_ids'] = sp_options_del[delete_sp_sel]
        st.session_state['confirm_delete_sp'] = True
        
    if st.session_state.get('confirm_delete_sp'):
        st.markdown(get_delete_warning_html(st.session_state['delete_sp_sel']), unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, Delete", key="del_sp_yes"):
                sid, pid = st.session_state['delete_sp_ids']
                if execute_statement("DELETE FROM scientist_member_project WHERE scientist_id=%s AND project_id=%s", (sid, pid)):
                    st.success("Deleted!")
                    del st.session_state['confirm_delete_sp']
                    del st.session_state['delete_sp_sel']
                    del st.session_state['delete_sp_ids']
                    st.rerun()
                else:
                    st.error("Failed.")
        with c2:
            if st.button("Cancel", key="del_sp_no"):
                del st.session_state['confirm_delete_sp']
                st.rerun()
