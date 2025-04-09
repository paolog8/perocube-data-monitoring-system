#!/usr/bin/env python3
"""
LabVIEW connector for the Perocube data monitoring system.
This module provides functionality to receive data directly from LabVIEW and store it in TimescaleDB.
"""

import socket
import json
import logging
import psycopg2
import threading
import time
import sys
from pathlib import Path
from datetime import datetime

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

class LabVIEWConnector:
    """
    A connector to receive data from LabVIEW and store it in TimescaleDB.
    
    This class creates a TCP socket server that listens for data from LabVIEW.
    Data is expected to be in JSON format with the following structure:
    {
        "type": "mpp|temperature|irradiance",
        "data": {
            "timestamp": "2023-09-20T12:00:00",
            ... (measurement specific fields)
        },
        "metadata": {
            ... (measurement specific metadata)
        }
    }
    """
    
    def __init__(self, host="0.0.0.0", port=5000, db_config=None):
        """
        Initialize the LabVIEW connector.
        
        Parameters:
        -----------
        host : str
            The IP address to bind the TCP server to
        port : int
            The port to bind the TCP server to
        db_config : dict
            Database configuration parameters
        """
        self.host = host
        self.port = port
        
        # Default database configuration
        default_db_config = {
            "dbname": "perocube",
            "user": "postgres",
            "password": "",
            "host": "localhost",
            "port": "5432"
        }
        
        # Override with provided configuration if any
        self.db_config = default_db_config
        if db_config:
            self.db_config.update(db_config)
            
        self.server_socket = None
        self.is_running = False
        self.db_conn = None
        
    def start(self):
        """
        Start the TCP server and begin listening for connections.
        """
        try:
            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            logger.info(f"Server started on {self.host}:{self.port}")
            
            # Connect to database
            self._connect_to_database()
            
            # Start accepting connections
            self.is_running = True
            self._accept_connections()
            
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            if self.server_socket:
                self.server_socket.close()
                
    def stop(self):
        """
        Stop the TCP server and close all connections.
        """
        logger.info("Stopping server...")
        self.is_running = False
        
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
            
        # Close database connection
        if self.db_conn:
            self.db_conn.close()
            
        logger.info("Server stopped")
        
    def _connect_to_database(self):
        """
        Establish a connection to the PostgreSQL database.
        """
        try:
            self.db_conn = psycopg2.connect(**self.db_config)
            logger.info("Connected to database successfully")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
            
    def _accept_connections(self):
        """
        Accept and handle incoming connections.
        """
        while self.is_running:
            try:
                client_socket, client_address = self.server_socket.accept()
                logger.info(f"New connection from {client_address}")
                
                # Handle client in a separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.is_running:
                    logger.error(f"Error accepting connection: {e}")
                    time.sleep(1)  # Avoid tight loop if there's an issue
                    
    def _handle_client(self, client_socket, client_address):
        """
        Handle communication with a connected client.
        
        Parameters:
        -----------
        client_socket : socket.socket
            The client socket object
        client_address : tuple
            The client's address (IP, port)
        """
        try:
            while self.is_running:
                # Receive data from client
                data = client_socket.recv(4096)
                if not data:
                    break
                    
                # Process received data
                message = data.decode('utf-8')
                self._process_message(message)
                
                # Send acknowledgment
                client_socket.sendall(b'ACK')
                
        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()
            logger.info(f"Connection from {client_address} closed")
            
    def _process_message(self, message):
        """
        Process a received message and store it in the database.
        
        Parameters:
        -----------
        message : str
            The received message (should be JSON)
        """
        try:
            # Parse JSON message
            data = json.loads(message)
            
            # Extract data type and measurement
            data_type = data.get('type')
            measurement = data.get('data')
            metadata = data.get('metadata', {})
            
            if not data_type or not measurement:
                logger.error("Invalid message format: missing type or data")
                return
                
            # Store in database based on data type
            if data_type == 'mpp':
                self._store_mpp_measurement(measurement, metadata)
            elif data_type == 'temperature':
                self._store_temperature_measurement(measurement, metadata)
            elif data_type == 'irradiance':
                self._store_irradiance_measurement(measurement, metadata)
            else:
                logger.error(f"Unknown data type: {data_type}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON message")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
    def _store_mpp_measurement(self, measurement, metadata):
        """
        Store an MPP measurement in the database.
        
        Parameters:
        -----------
        measurement : dict
            The MPP measurement data
        metadata : dict
            Additional metadata for the measurement
        """
        try:
            timestamp = datetime.fromisoformat(measurement.get('timestamp'))
            current = float(measurement.get('current', 0))
            voltage = float(measurement.get('voltage', 0))
            power = float(measurement.get('power', current * voltage))
            
            board = int(metadata.get('board', 0))
            channel = int(metadata.get('channel', 0))
            
            cursor = self.db_conn.cursor()
            cursor.execute(
                """
                INSERT INTO mpp_measurement 
                (timestamp, current, voltage, power, tracking_channel_board, tracking_channel_channel)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (timestamp, current, voltage, power, board, channel)
            )
            self.db_conn.commit()
            cursor.close()
            
            logger.debug(f"Stored MPP measurement: {timestamp}, board {board}, channel {channel}")
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error storing MPP measurement: {e}")
            
    def _store_temperature_measurement(self, measurement, metadata):
        """
        Store a temperature measurement in the database.
        
        Parameters:
        -----------
        measurement : dict
            The temperature measurement data
        metadata : dict
            Additional metadata for the measurement
        """
        try:
            timestamp = datetime.fromisoformat(measurement.get('timestamp'))
            temperature = float(measurement.get('temperature', 0))
            sensor_id = metadata.get('sensor_id')
            
            cursor = self.db_conn.cursor()
            cursor.execute(
                """
                INSERT INTO temperature_measurement 
                (timestamp, temperature, temperature_sensor_id)
                VALUES (%s, %s, %s)
                """,
                (timestamp, temperature, sensor_id)
            )
            self.db_conn.commit()
            cursor.close()
            
            logger.debug(f"Stored temperature measurement: {timestamp}, sensor {sensor_id}")
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error storing temperature measurement: {e}")
            
    def _store_irradiance_measurement(self, measurement, metadata):
        """
        Store an irradiance measurement in the database.
        
        Parameters:
        -----------
        measurement : dict
            The irradiance measurement data
        metadata : dict
            Additional metadata for the measurement
        """
        try:
            timestamp = datetime.fromisoformat(measurement.get('timestamp'))
            raw_reading = int(measurement.get('raw_reading', 0))
            irradiance = float(measurement.get('irradiance', 0))
            sensor_id = metadata.get('sensor_id')
            
            cursor = self.db_conn.cursor()
            cursor.execute(
                """
                INSERT INTO irradiance_measurement 
                (timestamp, raw_reading, irradiance, irradiance_sensor_id)
                VALUES (%s, %s, %s, %s)
                """,
                (timestamp, raw_reading, irradiance, sensor_id)
            )
            self.db_conn.commit()
            cursor.close()
            
            logger.debug(f"Stored irradiance measurement: {timestamp}, sensor {sensor_id}")
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error storing irradiance measurement: {e}")

def main():
    """
    Main entry point for the LabVIEW connector.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='LabVIEW connector for Perocube data monitoring system.')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind the TCP server to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind the TCP server to')
    parser.add_argument('--db-host', default='localhost', help='Database host')
    parser.add_argument('--db-port', default='5432', help='Database port')
    parser.add_argument('--db-name', default='perocube', help='Database name')
    parser.add_argument('--db-user', default='postgres', help='Database user')
    parser.add_argument('--db-password', default='', help='Database password')
    
    args = parser.parse_args()
    
    # Create database configuration
    db_config = {
        "dbname": args.db_name,
        "user": args.db_user,
        "password": args.db_password,
        "host": args.db_host,
        "port": args.db_port
    }
    
    # Create and start connector
    connector = LabVIEWConnector(host=args.host, port=args.port, db_config=db_config)
    
    try:
        connector.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, stopping server...")
    finally:
        connector.stop()

if __name__ == '__main__':
    main()