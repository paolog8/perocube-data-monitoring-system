import streamlit as st
import uuid
from pathlib import Path
import sys
import pandas as pd

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import execute_statement, run_query

st.set_page_config(page_title="Solar Cell Device", page_icon="☀️")

st.header("Manage Solar Cell Devices")

# Fetch data for dropdowns
scientists_df = run_query("SELECT scientist_id, name FROM scientist ORDER BY name")
experiments_df = run_query("SELECT experiment_id, name FROM experiment ORDER BY name")

scientist_options = {row['name']: row['scientist_id'] for index, row in scientists_df.iterrows()} if scientists_df is not None else {}
experiment_options = {row['name']: row['experiment_id'] for index, row in experiments_df.iterrows()} if experiments_df is not None else {}

# Form to add a new device
st.subheader("Add New Solar Cell Device")
with st.form("add_device_form"):
    name = st.text_input("Device Name (ID)")
    nomad_id = st.text_input("Nomad ID (UUID)", help="Optional")
    technology = st.text_input("Technology")
    form_factor = st.text_input("Form Factor")
    
    experiment_name = st.selectbox("Experiment", options=[""] + list(experiment_options.keys()))
    owner_name = st.selectbox("Owner", options=[""] + list(scientist_options.keys()))
    producer_name = st.selectbox("Producer", options=[""] + list(scientist_options.keys()))
    
    date_produced = st.date_input("Date Produced", value=None)
    date_encapsulated = st.date_input("Date Encapsulated", value=None)
    encapsulation = st.text_input("Encapsulation")
    area = st.number_input("Area", min_value=0.0, format="%.4f")
    initial_pce = st.number_input("Initial PCE", min_value=0.0, format="%.4f")
    
    submitted = st.form_submit_button("Add Device")
    
    if submitted:
        if name:
            experiment_id = experiment_options.get(experiment_name)
            owner_id = scientist_options.get(owner_name)
            producer_id = scientist_options.get(producer_name)
            
            # Handle empty nomad_id
            nomad_uuid = nomad_id if nomad_id else None
            
            query = """
                INSERT INTO solar_cell_device 
                (name, nomad_id, technology, form_factor, experiment_id, owner_id, producer_id, 
                 date_produced, date_encapsulated, encapsulation, area, initial_pce)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (name, nomad_uuid, technology, form_factor, experiment_id, owner_id, producer_id,
                      date_produced, date_encapsulated, encapsulation, area, initial_pce)
            
            if execute_statement(query, params):
                st.success(f"Device '{name}' added successfully!")
            else:
                st.error("Failed to add device. Name might already exist or invalid data.")
        else:
            st.warning("Please enter a device name.")

# List existing devices
st.subheader("Existing Devices")
df = run_query("SELECT * FROM solar_cell_device ORDER BY name")
if df is not None:
    st.dataframe(df)
else:
    st.error("Failed to load devices.")
