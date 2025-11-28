import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import execute_statement, run_query
from src.app.ui_utils import get_delete_warning_html

st.set_page_config(page_title="MPP Tracking Channel", page_icon="⚡")

st.header("Manage MPP Tracking Channels")

# Form to add a new channel
st.subheader("Add New Tracking Channel")
with st.form("add_channel_form", enter_to_submit=False):
    board = st.number_input("Board Number", min_value=0, step=1)
    channel = st.number_input("Channel Number", min_value=0, step=1)
    address = st.text_input("Address")
    com_port = st.text_input("COM Port")
    current_limit = st.number_input("Current Limit", min_value=0.0, format="%.4f")
    
    submitted = st.form_submit_button("Add Channel")
    
    if submitted:
        query = """
            INSERT INTO mpp_tracking_channel (board, channel, address, com_port, current_limit)
            VALUES (%s, %s, %s, %s, %s)
        """
        if execute_statement(query, (board, channel, address, com_port, current_limit)):
            st.success(f"Channel {board}-{channel} added successfully!")
        else:
            st.error("Failed to add channel. Board/Channel combination might already exist.")

# List existing channels
st.subheader("Existing Channels")
df = run_query("SELECT * FROM mpp_tracking_channel ORDER BY board, channel")
if df is not None:
    st.dataframe(df)
else:
    st.error("Failed to load channels.")

st.markdown("---")
st.subheader("Delete Tracking Channel")

# Prepare options for delete
channel_options_del = [f"Board {row['board']} - Channel {row['channel']}" for index, row in df.iterrows()] if df is not None else []

with st.form("delete_channel_form", enter_to_submit=False):
    delete_selection = st.selectbox("Select Channel to Delete", options=[""] + channel_options_del)
    delete_submitted = st.form_submit_button("Delete Channel")

if delete_submitted and delete_selection:
    st.session_state['delete_channel_selection'] = delete_selection
    st.session_state['confirm_delete_channel'] = True

if st.session_state.get('confirm_delete_channel'):
    st.markdown(get_delete_warning_html(st.session_state['delete_channel_selection']), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete Channel"):
            parts = st.session_state['delete_channel_selection'].split(" - ")
            board = int(parts[0].replace("Board ", ""))
            channel = int(parts[1].replace("Channel ", ""))
            
            query = "DELETE FROM mpp_tracking_channel WHERE board = %s AND channel = %s"
            if execute_statement(query, (board, channel)):
                st.success(f"Channel '{st.session_state['delete_channel_selection']}' deleted successfully!")
                # Clear state
                del st.session_state['confirm_delete_channel']
                del st.session_state['delete_channel_selection']
                st.rerun()
            else:
                st.error("Failed to delete channel. It might be referenced by other records.")
    with col2:
        if st.button("Cancel Delete"):
            del st.session_state['confirm_delete_channel']
            if 'delete_channel_selection' in st.session_state: del st.session_state['delete_channel_selection']
            st.rerun()
