import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

st.set_page_config(
    page_title="Perocube Metadata Ingestion",
    page_icon="🧪",
    layout="wide"
)

st.title("Perocube Data Monitoring System")
st.header("Metadata Ingestion")

st.markdown("""
Welcome to the Metadata Ingestion App. 
Use the sidebar to navigate to the specific form you want to fill out.

**Available Forms:**
- **Scientist**: Manage scientists.
- **Experiment**: Manage experiments.
- **Project**: Manage projects.
- **Solar Cell Device**: Register new solar cell devices.
- **Solar Cell Pixel**: Define pixels for devices.
- **MPP Tracking Channel**: Configure tracking channels.
- **Sensors**: Manage temperature and irradiance sensors.
- **Measurement Events**: Record connection events.
- **Relations**: Link scientists, experiments, and projects.
""")
