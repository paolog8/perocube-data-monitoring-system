#!/usr/bin/env python3
"""
API data models for the Perocube data monitoring system.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, UUID4


class SensorBase(BaseModel):
    """Base model for sensors"""
    date_installed: Optional[datetime] = None
    location: str


class TemperatureSensor(SensorBase):
    """Temperature sensor model"""
    temperature_sensor_id: UUID4
    
    class Config:
        orm_mode = True


class IrradianceSensor(SensorBase):
    """Irradiance sensor model"""
    irradiance_sensor_id: UUID4
    installation_angle: int
    
    class Config:
        orm_mode = True


class ScientistBase(BaseModel):
    """Base model for scientist"""
    name: str


class Scientist(ScientistBase):
    """Scientist model"""
    scientist_id: UUID4
    
    class Config:
        orm_mode = True


class ExperimentBase(BaseModel):
    """Base model for experiment"""
    name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class Experiment(ExperimentBase):
    """Experiment model"""
    experiment_id: UUID4
    scientists: List[Scientist] = []
    
    class Config:
        orm_mode = True


class ProjectBase(BaseModel):
    """Base model for project"""
    name: str


class Project(ProjectBase):
    """Project model"""
    project_id: UUID4
    scientists: List[Scientist] = []
    experiments: List[Experiment] = []
    
    class Config:
        orm_mode = True


class SolarCellDeviceBase(BaseModel):
    """Base model for solar cell device"""
    technology: Optional[str] = None
    form_factor: Optional[str] = None
    date_produced: Optional[datetime] = None
    date_encapsulated: Optional[datetime] = None
    encapsulation: Optional[str] = None
    area: Optional[float] = None
    initial_pce: Optional[float] = None


class SolarCellDevice(SolarCellDeviceBase):
    """Solar cell device model"""
    nomad_id: UUID4
    experiment_id: Optional[UUID4] = None
    owner_id: Optional[UUID4] = None
    producer_id: Optional[UUID4] = None
    
    class Config:
        orm_mode = True


class SolarCellPixelBase(BaseModel):
    """Base model for solar cell pixel"""
    pixel: str
    active_area: float


class SolarCellPixel(SolarCellPixelBase):
    """Solar cell pixel model"""
    solar_cell_id: UUID4
    
    class Config:
        orm_mode = True


class MPPTrackingChannelBase(BaseModel):
    """Base model for MPP tracking channel"""
    board: int
    channel: int
    address: str
    com_port: str
    current_limit: float


class MPPTrackingChannel(MPPTrackingChannelBase):
    """MPP tracking channel model"""
    
    class Config:
        orm_mode = True


class MeasurementConnectionEventBase(BaseModel):
    """Base model for measurement connection event"""
    connection_datetime: datetime
    mppt_mode: str
    mppt_polarity: str


class MeasurementConnectionEvent(MeasurementConnectionEventBase):
    """Measurement connection event model"""
    solar_cell_id: UUID4
    pixel: str
    tracking_channel_board: int
    tracking_channel_channel: int
    temperature_sensor_id: Optional[UUID4] = None
    irradiance_sensor_id: Optional[UUID4] = None
    
    class Config:
        orm_mode = True


class MPPMeasurementBase(BaseModel):
    """Base model for MPP measurement"""
    timestamp: datetime
    current: float
    voltage: float
    power: float


class MPPMeasurement(MPPMeasurementBase):
    """MPP measurement model"""
    tracking_channel_board: int
    tracking_channel_channel: int
    
    class Config:
        orm_mode = True


class TemperatureMeasurementBase(BaseModel):
    """Base model for temperature measurement"""
    timestamp: datetime
    temperature: float


class TemperatureMeasurement(TemperatureMeasurementBase):
    """Temperature measurement model"""
    temperature_sensor_id: UUID4
    
    class Config:
        orm_mode = True


class IrradianceMeasurementBase(BaseModel):
    """Base model for irradiance measurement"""
    timestamp: datetime
    raw_reading: int
    irradiance: float


class IrradianceMeasurement(IrradianceMeasurementBase):
    """Irradiance measurement model"""
    irradiance_sensor_id: UUID4
    
    class Config:
        orm_mode = True


class MeasurementQuery(BaseModel):
    """Query parameters for measurements"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)
    sort: str = "timestamp"
    order: str = "desc"
    
    
class MeasurementResponse(BaseModel):
    """Response model for measurements"""
    data: List[Union[MPPMeasurement, TemperatureMeasurement, IrradianceMeasurement]]
    total: int
    page: int
    page_size: int
    
    class Config:
        orm_mode = True