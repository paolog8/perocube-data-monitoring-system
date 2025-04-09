#!/usr/bin/env python3
"""
Historical data uploader for the Perocube data monitoring system.
This script reads data from CSV/TXT files and uploads it to the TimescaleDB database.
"""

import os
import sys
import argparse
import logging
import psycopg2
import pandas as pd
from datetime import datetime
import uuid
from pathlib import Path

# Add parent directory to sys.path to import project-level modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data_processing.transformers import transform_measurement_data
from data_processing.validators import validate_data_format

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def connect_to_database():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname="perocube",
            user="postgres",
            password="",  # Add password if needed
            host="localhost",
            port="5432"
        )
        logger.info("Connected to database successfully")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        sys.exit(1)

def parse_mpp_data_file(file_path):
    """Parse MPP tracking data from a text file."""
    try:
        # Determine file type and read accordingly
        if file_path.endswith('.txt'):
            df = pd.read_csv(file_path, delimiter='\t')
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            logger.error(f"Unsupported file format: {file_path}")
            return None
            
        # Validate and transform data
        if validate_data_format(df, 'mpp'):
            return transform_measurement_data(df, 'mpp')
        else:
            logger.error(f"Invalid data format in file: {file_path}")
            return None
    except Exception as e:
        logger.error(f"Error parsing MPP data file {file_path}: {e}")
        return None

def insert_mpp_data(conn, data, board, channel):
    """Insert MPP data into the database."""
    try:
        cursor = conn.cursor()
        for _, row in data.iterrows():
            cursor.execute(
                """
                INSERT INTO mpp_measurement 
                (timestamp, current, voltage, power, tracking_channel_board, tracking_channel_channel)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    row['timestamp'],
                    row['current'],
                    row['voltage'],
                    row['power'], 
                    board,
                    channel
                )
            )
        conn.commit()
        logger.info(f"Inserted {len(data)} MPP records for board {board}, channel {channel}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting MPP data: {e}")

def main():
    """Main entry point for the historical data upload script."""
    parser = argparse.ArgumentParser(description='Upload historical data to TimescaleDB.')
    parser.add_argument('--data-dir', required=True, help='Directory containing data files')
    parser.add_argument('--data-type', required=True, choices=['mpp', 'temperature', 'irradiance'], 
                      help='Type of data to upload')
    parser.add_argument('--board', type=int, help='Board number for MPP data')
    parser.add_argument('--channel', type=int, help='Channel number for MPP data')
    
    args = parser.parse_args()
    
    # Connect to the database
    conn = connect_to_database()
    
    # Process data based on type
    if args.data_type == 'mpp':
        if args.board is None or args.channel is None:
            logger.error("Board and channel must be specified for MPP data")
            sys.exit(1)
            
        # Check if data directory exists
        data_dir = Path(args.data_dir)
        if not data_dir.exists() or not data_dir.is_dir():
            logger.error(f"Data directory not found: {args.data_dir}")
            sys.exit(1)
            
        # Find all data files in the directory
        data_files = list(data_dir.glob('*.txt')) + list(data_dir.glob('*.csv'))
        if not data_files:
            logger.error(f"No data files found in {args.data_dir}")
            sys.exit(1)
            
        # Process each file
        for file_path in data_files:
            logger.info(f"Processing {file_path}...")
            data = parse_mpp_data_file(file_path)
            if data is not None:
                insert_mpp_data(conn, data, args.board, args.channel)
    
    # Close the database connection
    conn.close()
    logger.info("Data upload completed successfully")

if __name__ == '__main__':
    main()