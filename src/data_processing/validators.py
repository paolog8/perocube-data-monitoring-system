#!/usr/bin/env python3
"""
Data validation utilities for the Perocube data monitoring system.
"""

import pandas as pd
import numpy as np
from datetime import datetime

def validate_data_format(df, data_type):
    """
    Validate that a DataFrame has the required columns and format.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The data frame to validate
    data_type : str
        The type of data ('mpp', 'temperature', or 'irradiance')
        
    Returns:
    --------
    bool
        True if the data format is valid, False otherwise
    """
    if data_type == 'mpp':
        return _validate_mpp_data_format(df)
    elif data_type == 'temperature':
        return _validate_temperature_data_format(df)
    elif data_type == 'irradiance':
        return _validate_irradiance_data_format(df)
    else:
        raise ValueError(f"Unknown data type: {data_type}")

def _validate_mpp_data_format(df):
    """
    Validate that a DataFrame has the required columns for MPP data.
    
    Required columns (case insensitive):
    - Timestamp/Time/DateTime
    - Current/I
    - Voltage/V
    """
    # Check if the DataFrame has the required columns
    has_timestamp = any(col.lower() in ['timestamp', 'time', 'datetime'] for col in df.columns)
    has_current = any(col.lower() in ['current', 'i'] for col in df.columns)
    has_voltage = any(col.lower() in ['voltage', 'v'] for col in df.columns)
    
    if not (has_timestamp and has_current and has_voltage):
        return False
    
    # Check if the timestamp column is a valid datetime or can be converted to one
    timestamp_col = next(col for col in df.columns if col.lower() in ['timestamp', 'time', 'datetime'])
    
    # If already datetime type, we're good
    if pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
        return True
    
    # Try to convert to datetime
    try:
        pd.to_datetime(df[timestamp_col])
        return True
    except:
        # Try common formats
        for fmt in ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%Y/%m/%d %H:%M:%S']:
            try:
                pd.to_datetime(df[timestamp_col], format=fmt)
                return True
            except:
                continue
    
    return False

def _validate_temperature_data_format(df):
    """
    Validate that a DataFrame has the required columns for temperature data.
    
    Required columns (case insensitive):
    - Timestamp/Time/DateTime
    - Temperature/Temp/T
    """
    # Check if the DataFrame has the required columns
    has_timestamp = any(col.lower() in ['timestamp', 'time', 'datetime'] for col in df.columns)
    has_temperature = any(col.lower() in ['temperature', 'temp', 't'] for col in df.columns)
    
    if not (has_timestamp and has_temperature):
        return False
    
    # Check if the timestamp column is a valid datetime or can be converted to one
    timestamp_col = next(col for col in df.columns if col.lower() in ['timestamp', 'time', 'datetime'])
    
    # If already datetime type, we're good
    if pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
        return True
    
    # Try to convert to datetime
    try:
        pd.to_datetime(df[timestamp_col])
        return True
    except:
        # Try common formats
        for fmt in ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%Y/%m/%d %H:%M:%S']:
            try:
                pd.to_datetime(df[timestamp_col], format=fmt)
                return True
            except:
                continue
    
    return False

def _validate_irradiance_data_format(df):
    """
    Validate that a DataFrame has the required columns for irradiance data.
    
    Required columns (case insensitive):
    - Timestamp/Time/DateTime
    - At least one of: RawReading/Raw/Reading or Irradiance/Irr
    """
    # Check if the DataFrame has the required columns
    has_timestamp = any(col.lower() in ['timestamp', 'time', 'datetime'] for col in df.columns)
    has_raw = any(col.lower() in ['rawreading', 'raw', 'reading'] for col in df.columns)
    has_irradiance = any(col.lower() in ['irradiance', 'irr'] for col in df.columns)
    
    if not (has_timestamp and (has_raw or has_irradiance)):
        return False
    
    # Check if the timestamp column is a valid datetime or can be converted to one
    timestamp_col = next(col for col in df.columns if col.lower() in ['timestamp', 'time', 'datetime'])
    
    # If already datetime type, we're good
    if pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
        return True
    
    # Try to convert to datetime
    try:
        pd.to_datetime(df[timestamp_col])
        return True
    except:
        # Try common formats
        for fmt in ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%Y/%m/%d %H:%M:%S']:
            try:
                pd.to_datetime(df[timestamp_col], format=fmt)
                return True
            except:
                continue
    
    return False