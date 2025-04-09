#!/usr/bin/env python3
"""
Main entry point for the Perocube data monitoring system.

This module initializes the application, sets up logging, and provides
a command-line interface for starting different components of the system.
"""

import sys
import os
import logging
import logging.config
import argparse
import yaml
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """Set up logging configuration from the YAML file."""
    logging_config_path = project_root / 'config' / 'logging_config.yaml'
    
    # Create logs directory if it doesn't exist
    logs_dir = project_root / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    try:
        with open(logging_config_path, 'r') as config_file:
            config = yaml.safe_load(config_file)
            logging.config.dictConfig(config)
            return True
    except Exception as e:
        print(f"Error loading logging configuration: {e}")
        return False

def load_config():
    """Load application configuration from the YAML file."""
    config_path = project_root / 'config' / 'app_config.yaml'
    try:
        with open(config_path, 'r') as config_file:
            return yaml.safe_load(config_file)
    except Exception as e:
        logging.error(f"Error loading application configuration: {e}")
        return {}

def start_api_server(config):
    """Start the API server for data access."""
    from src.api.routes import app
    import uvicorn
    
    api_config = config.get('api', {})
    host = api_config.get('host', '0.0.0.0')
    port = api_config.get('port', 8000)
    debug = api_config.get('debug', False)
    
    logging.info(f"Starting API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")

def start_labview_connector(config):
    """Start the LabVIEW connector for data ingestion."""
    from src.ingestion.labview_connector import LabVIEWConnector
    
    connector_config = config.get('ingestion', {}).get('labview', {})
    db_config = config.get('database', {})
    
    host = connector_config.get('host', '0.0.0.0')
    port = connector_config.get('port', 5000)
    
    connector = LabVIEWConnector(host=host, port=port, db_config=db_config)
    logging.info(f"Starting LabVIEW connector on {host}:{port}")
    
    try:
        connector.start()
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received, stopping server...")
    finally:
        connector.stop()

def main():
    """Main entry point."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Perocube Data Monitoring System'
    )
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # API server command
    api_parser = subparsers.add_parser('api', help='Start the API server')
    
    # LabVIEW connector command
    labview_parser = subparsers.add_parser('labview', help='Start the LabVIEW connector')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up logging
    if not setup_logging():
        print("Using basic logging configuration")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Load configuration
    config = load_config()
    
    # Execute the requested command
    if args.command == 'api':
        start_api_server(config)
    elif args.command == 'labview':
        start_labview_connector(config)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()