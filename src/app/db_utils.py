import psycopg2
import yaml
import logging
import os
from pathlib import Path
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    """Load application configuration from the YAML file."""
    project_root = Path(__file__).resolve().parent.parent.parent
    config_path = project_root / 'config' / 'app_config.yaml'
    try:
        with open(config_path, 'r') as config_file:
            return yaml.safe_load(config_file)
    except Exception as e:
        logger.error(f"Error loading application configuration: {e}")
        return {}

def get_db_connection():
    """Establish a connection to the PostgreSQL database."""
    config = load_config()
    db_config = config.get('database', {})
    
    # Prioritize environment variables, fallback to config file, then defaults
    dbname = os.getenv('DB_NAME', db_config.get('dbname', 'perocube'))
    user = os.getenv('DB_USER', db_config.get('user', 'postgres'))
    password = os.getenv('DB_PASSWORD', db_config.get('password', ''))
    host = os.getenv('DB_HOST', db_config.get('host', 'localhost'))
    port = os.getenv('DB_PORT', db_config.get('port', '5432'))

    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def run_query(query, params=None):
    """Run a query and return the results as a DataFrame."""
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql(query, conn, params=params)
            conn.close()
            return df
        except Exception as e:
            logger.error(f"Error running query: {e}")
            conn.close()
            return None
    return None

def execute_statement(statement, params=None):
    """Execute a SQL statement (INSERT, UPDATE, DELETE)."""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(statement, params)
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error executing statement: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    return False
