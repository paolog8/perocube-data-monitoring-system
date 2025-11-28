import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import execute_statement, run_query

st.set_page_config(page_title="MPP Tracking Channel", page_icon="⚡")

st.header("Manage MPP Tracking Channels")

# Form to add a new channel
st.subheader("Add New Tracking Channel")
with st.form("add_channel_form"):
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
