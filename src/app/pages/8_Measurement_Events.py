import streamlit as st
from pathlib import Path
import sys
import pandas as pd
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import execute_statement, run_query

st.set_page_config(page_title="Measurement Events", page_icon="🔌")

st.header("Manage Measurement Connection Events")

# Fetch data for dropdowns
pixels_df = run_query("SELECT solar_cell_id, pixel FROM solar_cell_pixel ORDER BY solar_cell_id, pixel")
channels_df = run_query("SELECT board, channel FROM mpp_tracking_channel ORDER BY board, channel")
temp_sensors_df = run_query("SELECT temperature_sensor_id, sensor_identifier FROM temperature_sensor ORDER BY sensor_identifier")
irr_sensors_df = run_query("SELECT irradiance_sensor_id, sensor_identifier, channel FROM irradiance_sensor ORDER BY sensor_identifier, channel")

pixel_options = [f"{row['solar_cell_id']} - {row['pixel']}" for index, row in pixels_df.iterrows()] if pixels_df is not None else []
channel_options = [f"Board {row['board']} - Channel {row['channel']}" for index, row in channels_df.iterrows()] if channels_df is not None else []
temp_sensor_options = {row['sensor_identifier']: row['temperature_sensor_id'] for index, row in temp_sensors_df.iterrows()} if temp_sensors_df is not None else {}
irr_sensor_options = {f"{row['sensor_identifier']} (Ch {row['channel']})": row['irradiance_sensor_id'] for index, row in irr_sensors_df.iterrows()} if irr_sensors_df is not None else {}

# Form to add a new event
st.subheader("Add New Connection Event")
with st.form("add_event_form", enter_to_submit=False):
    pixel_selection = st.selectbox("Solar Cell Pixel", options=[""] + pixel_options)
    channel_selection = st.selectbox("MPP Tracking Channel", options=[""] + channel_options)
    
    temp_sensor_name = st.selectbox("Temperature Sensor", options=[""] + list(temp_sensor_options.keys()))
    irr_sensor_name = st.selectbox("Irradiance Sensor", options=[""] + list(irr_sensor_options.keys()))
    
    mppt_mode = st.selectbox("MPPT Mode", options=["", "MPP", "J-V Scan", "Fixed Voltage"])
    mppt_polarity = st.selectbox("MPPT Polarity", options=["", "Forward", "Reverse"])
    
    connection_date = st.date_input("Date", value=datetime.now())
    connection_time = st.time_input("Time", value=datetime.now().time())
    
    event_type = st.selectbox("Event Type", options=["CONNECTED", "DISCONNECTED"])
    
    submitted = st.form_submit_button("Add Event")
    
    if submitted:
        if pixel_selection and event_type:
            # Parse selections
            solar_cell_id, pixel = pixel_selection.split(" - ", 1)
            
            board = None
            channel = None
            if channel_selection:
                parts = channel_selection.split(" - ")
                board = int(parts[0].replace("Board ", ""))
                channel = int(parts[1].replace("Channel ", ""))
            
            temp_sensor_id = temp_sensor_options.get(temp_sensor_name)
            irr_sensor_id = irr_sensor_options.get(irr_sensor_name)
            
            connection_datetime = datetime.combine(connection_date, connection_time)
            
            query = """
                INSERT INTO measurement_connection_event 
                (solar_cell_id, pixel, tracking_channel_board, tracking_channel_channel, 
                 temperature_sensor_id, irradiance_sensor_id, mppt_mode, mppt_polarity, 
                 connection_datetime, event_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (solar_cell_id, pixel, board, channel, temp_sensor_id, irr_sensor_id, 
                      mppt_mode, mppt_polarity, connection_datetime, event_type)
            
            if execute_statement(query, params):
                st.success("Event recorded successfully!")
            else:
                st.error("Failed to record event. Check if data is valid.")
        else:
            st.warning("Please select a pixel and event type.")

# List existing events
st.subheader("Recent Events")
df = run_query("SELECT * FROM measurement_connection_event ORDER BY connection_datetime DESC LIMIT 50")
if df is not None:
    st.dataframe(df)
else:
    st.error("Failed to load events.")
