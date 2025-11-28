import streamlit as st
import uuid
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import execute_statement, run_query

st.set_page_config(page_title="Sensors", page_icon="🌡️")

st.header("Manage Sensors")

tab1, tab2 = st.tabs(["Temperature Sensors", "Irradiance Sensors"])

with tab1:
    st.subheader("Add Temperature Sensor")
    with st.form("add_temp_sensor_form"):
        sensor_identifier = st.text_input("Sensor Identifier")
        location = st.text_input("Location")
        date_installed = st.date_input("Date Installed", value=None)
        
        submitted = st.form_submit_button("Add Temperature Sensor")
        
        if submitted:
            if sensor_identifier:
                sensor_id = str(uuid.uuid4())
                query = """
                    INSERT INTO temperature_sensor (temperature_sensor_id, sensor_identifier, location, date_installed)
                    VALUES (%s, %s, %s, %s)
                """
                if execute_statement(query, (sensor_id, sensor_identifier, location, date_installed)):
                    st.success(f"Temperature Sensor '{sensor_identifier}' added successfully!")
                else:
                    st.error("Failed to add sensor. Identifier might already exist.")
            else:
                st.warning("Please enter a sensor identifier.")
    
    st.subheader("Existing Temperature Sensors")
    df_temp = run_query("SELECT * FROM temperature_sensor ORDER BY sensor_identifier")
    if df_temp is not None:
        st.dataframe(df_temp)

with tab2:
    st.subheader("Add Irradiance Sensor")
    with st.form("add_irr_sensor_form"):
        sensor_identifier = st.text_input("Sensor Identifier")
        channel = st.number_input("Channel", min_value=0, step=1)
        location = st.text_input("Location")
        installation_angle = st.number_input("Installation Angle", min_value=0, step=1)
        date_installed = st.date_input("Date Installed", value=None)
        
        submitted = st.form_submit_button("Add Irradiance Sensor")
        
        if submitted:
            if sensor_identifier:
                sensor_id = str(uuid.uuid4())
                query = """
                    INSERT INTO irradiance_sensor 
                    (irradiance_sensor_id, sensor_identifier, channel, location, installation_angle, date_installed)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                if execute_statement(query, (sensor_id, sensor_identifier, channel, location, installation_angle, date_installed)):
                    st.success(f"Irradiance Sensor '{sensor_identifier}' (Channel {channel}) added successfully!")
                else:
                    st.error("Failed to add sensor. Identifier/Channel combination might already exist.")
            else:
                st.warning("Please enter a sensor identifier.")

    st.subheader("Existing Irradiance Sensors")
    df_irr = run_query("SELECT * FROM irradiance_sensor ORDER BY sensor_identifier, channel")
    if df_irr is not None:
        st.dataframe(df_irr)
