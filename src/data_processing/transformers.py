#!/usr/bin/env python3
"""
Data transformation utilities for the Perocube data monitoring system.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re

def transform_measurement_data(df, data_type):
    """
    Transform raw measurement data into a standardized format.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The raw data frame to transform
    data_type : str
        The type of data ('mpp', 'temperature', or 'irradiance')
        
    Returns:
    --------
    pandas.DataFrame
        Transformed data frame with standardized columns
    """
    if data_type == 'mpp':
        return _transform_mpp_data(df)
    elif data_type == 'temperature':
        return _transform_temperature_data(df)
    elif data_type == 'irradiance':
        return _transform_irradiance_data(df)
    else:
        raise ValueError(f"Unknown data type: {data_type}")

def _transform_mpp_data(df):
    """
    Transform raw MPP tracking data.
    
    Expected columns in input:
    - Timestamp or Time or DateTime
    - Current or I 
    - Voltage or V
    - Power or P (optional, will be calculated if missing)
    
    Returns DataFrame with standardized columns:
    - timestamp (datetime)
    - current (float)
    - voltage (float)
    - power (float)
    """
    # Create a copy to avoid modifying the original
    result = df.copy()
    
    # Standardize column names (case insensitive)
    col_mapping = {}
    for col in result.columns:
        if col.lower() in ['timestamp', 'time', 'datetime']:
            col_mapping[col] = 'timestamp'
        elif col.lower() in ['current', 'i']:
            col_mapping[col] = 'current'
        elif col.lower() in ['voltage', 'v']:
            col_mapping[col] = 'voltage'
        elif col.lower() in ['power', 'p']:
            col_mapping[col] = 'power'
    
    result = result.rename(columns=col_mapping)
    
    # Parse timestamp if it's a string
    if result['timestamp'].dtype == 'object':
        # Try multiple date formats
        try:
            result['timestamp'] = pd.to_datetime(result['timestamp'])
        except:
            # Try common formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%Y/%m/%d %H:%M:%S']:
                try:
                    result['timestamp'] = pd.to_datetime(result['timestamp'], format=fmt)
                    break
                except:
                    continue
    
    # Calculate power if missing
    if 'power' not in result.columns:
        result['power'] = result['current'] * result['voltage']
    
    # Select only the standardized columns
    return result[['timestamp', 'current', 'voltage', 'power']]

def _transform_temperature_data(df):
    """
    Transform raw temperature data.
    
    Expected columns in input:
    - Timestamp or Time or DateTime
    - Temperature or Temp or T
    
    Returns DataFrame with standardized columns:
    - timestamp (datetime)
    - temperature (float)
    """
    # Create a copy to avoid modifying the original
    result = df.copy()
    
    # Standardize column names (case insensitive)
    col_mapping = {}
    for col in result.columns:
        if col.lower() in ['timestamp', 'time', 'datetime']:
            col_mapping[col] = 'timestamp'
        elif col.lower() in ['temperature', 'temp', 't']:
            col_mapping[col] = 'temperature'
    
    result = result.rename(columns=col_mapping)
    
    # Parse timestamp if it's a string
    if result['timestamp'].dtype == 'object':
        # Try multiple date formats
        try:
            result['timestamp'] = pd.to_datetime(result['timestamp'])
        except:
            # Try common formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%Y/%m/%d %H:%M:%S']:
                try:
                    result['timestamp'] = pd.to_datetime(result['timestamp'], format=fmt)
                    break
                except:
                    continue
    
    # Select only the standardized columns
    return result[['timestamp', 'temperature']]

def _transform_irradiance_data(df):
    """
    Transform raw irradiance data.
    
    Expected columns in input:
    - Timestamp or Time or DateTime
    - RawReading or Raw or Reading
    - Irradiance or Irr
    
    Returns DataFrame with standardized columns:
    - timestamp (datetime)
    - raw_reading (int)
    - irradiance (float)
    """
    # Create a copy to avoid modifying the original
    result = df.copy()
    
    # Standardize column names (case insensitive)
    col_mapping = {}
    for col in result.columns:
        if col.lower() in ['timestamp', 'time', 'datetime']:
            col_mapping[col] = 'timestamp'
        elif col.lower() in ['rawreading', 'raw', 'reading']:
            col_mapping[col] = 'raw_reading'
        elif col.lower() in ['irradiance', 'irr']:
            col_mapping[col] = 'irradiance'
    
    result = result.rename(columns=col_mapping)
    
    # Parse timestamp if it's a string
    if result['timestamp'].dtype == 'object':
        # Try multiple date formats
        try:
            result['timestamp'] = pd.to_datetime(result['timestamp'])
        except:
            # Try common formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%Y/%m/%d %H:%M:%S']:
                try:
                    result['timestamp'] = pd.to_datetime(result['timestamp'], format=fmt)
                    break
                except:
                    continue
    
    # Calculate irradiance from raw reading if missing
    if 'irradiance' not in result.columns and 'raw_reading' in result.columns:
        # Apply a simple linear transformation - this should be calibrated for the actual sensor
        result['irradiance'] = result['raw_reading'] * 0.1  # Example conversion factor
    
    # Select only the standardized columns
    return result[['timestamp', 'raw_reading', 'irradiance']]