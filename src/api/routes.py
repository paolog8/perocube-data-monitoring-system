#!/usr/bin/env python3
"""
API routes for the Perocube data monitoring system.
"""

import logging
import yaml
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import UUID4

from .models import (
    MPPMeasurement, TemperatureMeasurement, IrradianceMeasurement,
    SolarCellDevice, Experiment, Project, Scientist,
    TemperatureSensor, IrradianceSensor, MeasurementResponse,
    MeasurementQuery
)

# Set up logging
logger = logging.getLogger("api")

# Load configuration
config_path = Path(__file__).resolve().parent.parent.parent.parent / 'config' / 'app_config.yaml'
try:
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
except Exception as e:
    logger.error(f"Failed to load config: {e}")
    config = {}

# Create FastAPI app
app = FastAPI(
    title="Perocube Data Monitoring API",
    description="API for accessing data from the Perocube monitoring system",
    version="0.1.0",
)

# Add CORS middleware
if "api" in config and "cors_origins" in config["api"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config["api"]["cors_origins"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Database connection dependency
async def get_db():
    """Get database connection for request"""
    # In a production environment, use SQLAlchemy or another ORM
    # For now, we'll just mock this connection
    db = {"connected": True}
    try:
        yield db
    finally:
        pass

# Health check endpoint
@app.get("/health")
async def health_check():
    """Check API health status"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# MPP measurement endpoints
@app.get("/measurements/mpp", response_model=MeasurementResponse)
async def get_mpp_measurements(
    query: MeasurementQuery = Depends(),
    board: Optional[int] = None,
    channel: Optional[int] = None,
    db=Depends(get_db)
):
    """
    Get MPP measurements with optional filtering
    """
    logger.info(f"Retrieving MPP measurements with query: {query}, board: {board}, channel: {channel}")
    
    # In a real implementation, query the database here
    # For now, return mock data
    result = {
        "data": [
            {
                "timestamp": datetime.now() - timedelta(minutes=i),
                "current": 0.05 - (i * 0.001),
                "voltage": 0.8 - (i * 0.01),
                "power": (0.05 - (i * 0.001)) * (0.8 - (i * 0.01)),
                "tracking_channel_board": board or 1,
                "tracking_channel_channel": channel or 1
            }
            for i in range(query.limit)
        ],
        "total": 1000,
        "page": query.offset // query.limit + 1 if query.limit > 0 else 1,
        "page_size": query.limit
    }
    return result

# Temperature measurement endpoints
@app.get("/measurements/temperature", response_model=MeasurementResponse)
async def get_temperature_measurements(
    query: MeasurementQuery = Depends(),
    sensor_id: Optional[UUID4] = None,
    db=Depends(get_db)
):
    """
    Get temperature measurements with optional filtering
    """
    logger.info(f"Retrieving temperature measurements with query: {query}, sensor_id: {sensor_id}")
    
    # Mock data for demonstration purposes
    result = {
        "data": [
            {
                "timestamp": datetime.now() - timedelta(minutes=i),
                "temperature": 25.0 + (i % 5) * 0.5,
                "temperature_sensor_id": sensor_id or UUID("a3086f43-c11c-4cad-9497-dcd1c7a1e9ed")
            }
            for i in range(query.limit)
        ],
        "total": 1000,
        "page": query.offset // query.limit + 1 if query.limit > 0 else 1,
        "page_size": query.limit
    }
    return result

# Irradiance measurement endpoints
@app.get("/measurements/irradiance", response_model=MeasurementResponse)
async def get_irradiance_measurements(
    query: MeasurementQuery = Depends(),
    sensor_id: Optional[UUID4] = None,
    db=Depends(get_db)
):
    """
    Get irradiance measurements with optional filtering
    """
    logger.info(f"Retrieving irradiance measurements with query: {query}, sensor_id: {sensor_id}")
    
    # Mock data for demonstration purposes
    result = {
        "data": [
            {
                "timestamp": datetime.now() - timedelta(minutes=i),
                "raw_reading": 1000 - (i * 10),
                "irradiance": 100.0 - i,
                "irradiance_sensor_id": sensor_id or UUID("b6e74d25-3a3e-4d0d-95a3-f91681b39857")
            }
            for i in range(query.limit)
        ],
        "total": 1000,
        "page": query.offset // query.limit + 1 if query.limit > 0 else 1,
        "page_size": query.limit
    }
    return result

# Solar cell device endpoints
@app.get("/devices", response_model=List[SolarCellDevice])
async def get_solar_cell_devices(
    experiment_id: Optional[UUID4] = None,
    owner_id: Optional[UUID4] = None,
    db=Depends(get_db)
):
    """
    Get solar cell devices with optional filtering
    """
    logger.info(f"Retrieving solar cell devices, experiment_id: {experiment_id}, owner_id: {owner_id}")
    
    # Mock data for demonstration purposes
    result = [
        {
            "nomad_id": UUID("c5d7a3d9-e887-4c3c-942d-8d888f8d8dcb"),
            "technology": "Perovskite",
            "form_factor": "Standard",
            "experiment_id": experiment_id or UUID("d1bf1e8e-8b3f-4b3f-8f8f-3e3e3e3e3e3e"),
            "owner_id": owner_id or UUID("e1234567-e123-4123-a123-123456789abc"),
            "producer_id": UUID("e7654321-e123-4123-a123-123456789abc"),
            "date_produced": datetime.now() - timedelta(days=30),
            "date_encapsulated": datetime.now() - timedelta(days=29),
            "encapsulation": "Glass",
            "area": 1.0,
            "initial_pce": 20.5
        }
    ]
    return result

# Experiment endpoints
@app.get("/experiments", response_model=List[Experiment])
async def get_experiments(
    project_id: Optional[UUID4] = None,
    scientist_id: Optional[UUID4] = None,
    db=Depends(get_db)
):
    """
    Get experiments with optional filtering
    """
    logger.info(f"Retrieving experiments, project_id: {project_id}, scientist_id: {scientist_id}")
    
    # Mock data for demonstration purposes
    result = [
        {
            "experiment_id": UUID("d1bf1e8e-8b3f-4b3f-8f8f-3e3e3e3e3e3e"),
            "name": "Outdoor stability test Q2 2024",
            "start_date": datetime.now() - timedelta(days=60),
            "end_date": None,
            "scientists": [
                {
                    "scientist_id": UUID("e1234567-e123-4123-a123-123456789abc"),
                    "name": "Dr. Jane Smith"
                }
            ]
        }
    ]
    return result

# Data statistics endpoints
@app.get("/statistics/mpp")
async def get_mpp_statistics(
    start_time: datetime = Query(None),
    end_time: datetime = Query(None),
    board: Optional[int] = None,
    channel: Optional[int] = None,
    db=Depends(get_db)
):
    """
    Get statistics for MPP measurements
    """
    logger.info(f"Retrieving MPP statistics, start_time: {start_time}, end_time: {end_time}, " +
                f"board: {board}, channel: {channel}")
    
    # Mock data for demonstration purposes
    return {
        "count": 1440,
        "avg_current": 0.05,
        "avg_voltage": 0.8,
        "avg_power": 0.04,
        "max_power": 0.045,
        "min_power": 0.035,
        "start_time": start_time or (datetime.now() - timedelta(days=1)),
        "end_time": end_time or datetime.now()
    }

@app.get("/statistics/temperature")
async def get_temperature_statistics(
    start_time: datetime = Query(None),
    end_time: datetime = Query(None),
    sensor_id: Optional[UUID4] = None,
    db=Depends(get_db)
):
    """
    Get statistics for temperature measurements
    """
    logger.info(f"Retrieving temperature statistics, start_time: {start_time}, end_time: {end_time}, " +
                f"sensor_id: {sensor_id}")
    
    # Mock data for demonstration purposes
    return {
        "count": 1440,
        "avg_temperature": 25.5,
        "max_temperature": 32.1,
        "min_temperature": 18.3,
        "start_time": start_time or (datetime.now() - timedelta(days=1)),
        "end_time": end_time or datetime.now()
    }

@app.get("/statistics/irradiance")
async def get_irradiance_statistics(
    start_time: datetime = Query(None),
    end_time: datetime = Query(None),
    sensor_id: Optional[UUID4] = None,
    db=Depends(get_db)
):
    """
    Get statistics for irradiance measurements
    """
    logger.info(f"Retrieving irradiance statistics, start_time: {start_time}, end_time: {end_time}, " +
                f"sensor_id: {sensor_id}")
    
    # Mock data for demonstration purposes
    return {
        "count": 1440,
        "avg_irradiance": 450.2,
        "max_irradiance": 980.5,
        "min_irradiance": 0.0,
        "start_time": start_time or (datetime.now() - timedelta(days=1)),
        "end_time": end_time or datetime.now()
    }