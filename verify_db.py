import sys
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.db_utils import get_db_connection, run_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify():
    logger.info("Attempting to connect to the database...")
    conn = get_db_connection()
    if conn:
        logger.info("Successfully connected to the database!")
        conn.close()
        
        logger.info("Attempting to run a query...")
        df = run_query("SELECT 1 as test")
        if df is not None and not df.empty and df.iloc[0]['test'] == 1:
            logger.info("Query execution successful!")
        else:
            logger.error("Query execution failed or returned unexpected result.")
    else:
        logger.error("Failed to connect to the database.")

if __name__ == "__main__":
    verify()
