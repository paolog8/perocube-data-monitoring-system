import streamlit as st
import uuid
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import execute_statement, run_query
from src.app.ui_utils import get_delete_warning_html

st.set_page_config(page_title="Sensors", page_icon="🌡️")

st.header("Manage Sensors")

tab1, tab2 = st.tabs(["Temperature Sensors", "Irradiance Sensors"])

with tab1:
    st.subheader("Add Temperature Sensor")
    with st.form("add_temp_sensor_form", enter_to_submit=False):
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

    st.markdown("---")
    st.subheader("Delete Temperature Sensor")

    # Prepare options for delete
    temp_options_del = {row['sensor_identifier']: row['temperature_sensor_id'] for index, row in df_temp.iterrows()} if df_temp is not None else {}

    with st.form("delete_temp_sensor_form", enter_to_submit=False):
        delete_temp_name = st.selectbox("Select Temperature Sensor to Delete", options=[""] + list(temp_options_del.keys()))
        delete_temp_submitted = st.form_submit_button("Delete Temperature Sensor")

    if delete_temp_submitted and delete_temp_name:
        st.session_state['delete_temp_name'] = delete_temp_name
        st.session_state['delete_temp_id'] = temp_options_del[delete_temp_name]
        st.session_state['confirm_delete_temp'] = True

    if st.session_state.get('confirm_delete_temp'):
        st.markdown(get_delete_warning_html(st.session_state['delete_temp_name']), unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Delete Temperature Sensor"):
                query = "DELETE FROM temperature_sensor WHERE temperature_sensor_id = %s"
                if execute_statement(query, (st.session_state['delete_temp_id'],)):
                    st.success(f"Temperature Sensor '{st.session_state['delete_temp_name']}' deleted successfully!")
                    # Clear state
                    del st.session_state['confirm_delete_temp']
                    del st.session_state['delete_temp_name']
                    del st.session_state['delete_temp_id']
                    st.rerun()
                else:
                    st.error("Failed to delete sensor. It might be referenced by other records.")
        with col2:
            if st.button("Cancel Delete", key="cancel_temp"):
                del st.session_state['confirm_delete_temp']
                if 'delete_temp_name' in st.session_state: del st.session_state['delete_temp_name']
                if 'delete_temp_id' in st.session_state: del st.session_state['delete_temp_id']
                st.rerun()

with tab2:
    st.subheader("Add Irradiance Sensor")
    with st.form("add_irr_sensor_form", enter_to_submit=False):
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

    st.markdown("---")
    st.subheader("Delete Irradiance Sensor")

    # Prepare options for delete
    irr_options_del = {f"{row['sensor_identifier']} (Ch {row['channel']})": row['irradiance_sensor_id'] for index, row in df_irr.iterrows()} if df_irr is not None else {}

    with st.form("delete_irr_sensor_form", enter_to_submit=False):
        delete_irr_name = st.selectbox("Select Irradiance Sensor to Delete", options=[""] + list(irr_options_del.keys()))
        delete_irr_submitted = st.form_submit_button("Delete Irradiance Sensor")

    if delete_irr_submitted and delete_irr_name:
        st.session_state['delete_irr_name'] = delete_irr_name
        st.session_state['delete_irr_id'] = irr_options_del[delete_irr_name]
        st.session_state['confirm_delete_irr'] = True

    if st.session_state.get('confirm_delete_irr'):
        st.markdown(get_delete_warning_html(st.session_state['delete_irr_name']), unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Delete Irradiance Sensor"):
                query = "DELETE FROM irradiance_sensor WHERE irradiance_sensor_id = %s"
                if execute_statement(query, (st.session_state['delete_irr_id'],)):
                    st.success(f"Irradiance Sensor '{st.session_state['delete_irr_name']}' deleted successfully!")
                    # Clear state
                    del st.session_state['confirm_delete_irr']
                    del st.session_state['delete_irr_name']
                    del st.session_state['delete_irr_id']
                    st.rerun()
                else:
                    st.error("Failed to delete sensor. It might be referenced by other records.")
        with col2:
            if st.button("Cancel Delete", key="cancel_irr"):
                del st.session_state['confirm_delete_irr']
                if 'delete_irr_name' in st.session_state: del st.session_state['delete_irr_name']
                if 'delete_irr_id' in st.session_state: del st.session_state['delete_irr_id']
                st.rerun()

with tab1:
    # ... existing code ...
    # I need to append to tab1 as well, but replace_file_content replaces a block.
    # I will use multi_replace_file_content or careful targeting.
    # The current tool call targets the end of the file which is inside tab2.
    # I need to add delete for tab1 too.
    pass
