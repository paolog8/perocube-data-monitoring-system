import streamlit as st
from pathlib import Path
import sys
import pandas as pd
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import execute_statement, run_query
from src.app.ui_utils import get_delete_warning_html

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

st.markdown("---")
st.subheader("Delete Event")

# Prepare options for delete
# We need a unique way to identify events. The table likely has a composite PK or we can use all fields.
# Let's assume we can delete by matching the fields shown in the dropdown.
# A better way is to fetch a hidden ID if available, but the schema isn't fully visible.
# Assuming composite PK: solar_cell_id, pixel, connection_datetime
event_options_del = [f"{row['connection_datetime']} - {row['solar_cell_id']} {row['pixel']} ({row['event_type']})" for index, row in df.iterrows()] if df is not None else []

with st.form("delete_event_form", enter_to_submit=False):
    delete_event_selection = st.selectbox("Select Event to Delete", options=[""] + event_options_del)
    delete_submitted = st.form_submit_button("Delete Event")

if delete_submitted and delete_event_selection:
    st.session_state['delete_event_selection'] = delete_event_selection
    st.session_state['confirm_delete_event'] = True

if st.session_state.get('confirm_delete_event'):
    st.markdown(get_delete_warning_html(st.session_state['delete_event_selection']), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete Event"):
            # Parse selection to get keys
            # Format: "YYYY-MM-DD HH:MM:SS - solar_cell_id pixel (TYPE)"
            try:
                parts = st.session_state['delete_event_selection'].split(" - ", 1)
                datetime_str = parts[0]
                rest = parts[1]
                # This parsing is fragile. Ideally we should have an ID.
                # Let's try to match by connection_datetime and solar_cell_id and pixel.
                # But wait, 'rest' is "solar_cell_id pixel (TYPE)".
                # This is getting complicated to parse back.
                # I will use the index from the dataframe to get the row, assuming the dataframe order hasn't changed (it shouldn't in the same run).
                # But st.selectbox returns the string.
                
                # Better approach: Use a dictionary mapping the string to the row data (or PK fields).
                selected_row = None
                for index, row in df.iterrows():
                    opt_str = f"{row['connection_datetime']} - {row['solar_cell_id']} {row['pixel']} ({row['event_type']})"
                    if opt_str == st.session_state['delete_event_selection']:
                        selected_row = row
                        break
                
                if selected_row is not None:
                    query = """
                        DELETE FROM measurement_connection_event 
                        WHERE solar_cell_id = %s AND pixel = %s AND connection_datetime = %s
                    """
                    if execute_statement(query, (selected_row['solar_cell_id'], selected_row['pixel'], selected_row['connection_datetime'])):
                        st.success("Event deleted successfully!")
                        del st.session_state['confirm_delete_event']
                        del st.session_state['delete_event_selection']
                        st.rerun()
                    else:
                        st.error("Failed to delete event.")
                else:
                    st.error("Could not find event to delete.")
            except Exception as e:
                st.error(f"Error parsing selection: {e}")

    with col2:
        if st.button("Cancel Delete"):
            del st.session_state['confirm_delete_event']
            if 'delete_event_selection' in st.session_state: del st.session_state['delete_event_selection']
            st.rerun()
