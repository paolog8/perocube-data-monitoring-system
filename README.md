# Perocube Data Monitoring System

A PostgreSQL+TimescaleDB system for monitoring perocube data at PVcomB. This system collects, stores, and provides access to time-series data from solar cell devices.

## Project Structure

```
perocube-data-monitoring-system/
├── config/                      # Configuration files
│   ├── app_config.yaml          # Application configuration
│   └── logging_config.yaml      # Logging configuration
├── db/                          # Database-related files
│   ├── config/                  # Database configuration
│   │   └── timescaledb.conf     # TimescaleDB configuration
│   ├── migrations/              # Database migration scripts
│   │   └── V1__initial_schema.sql  # Initial schema migration
│   ├── scripts/                 # Database utility scripts
│   │   ├── backup_db.sh         # Database backup script
│   │   └── init_db.sh           # Database initialization script
│   └── sql/                     # SQL scripts
│       ├── functions/           # Database functions
│       ├── queries/             # Common queries
│       └── schema/              # Schema definition
│           ├── init.sql         # Database creation
│           ├── tables.sql       # Table definitions
│           └── indexes.sql      # Index definitions
├── docs/                        # Documentation
│   ├── architecture/            # Architecture documentation
│   └── data-models/             # Data models documentation
│       └── logical-data-model.mmd  # Logical data model
├── logs/                        # Log files (created at runtime)
├── notebooks/                   # Jupyter notebooks
│   ├── analysis/                # Data analysis notebooks
│   └── data_upload/             # Data upload notebooks
│       ├── Upload_MPP_data.ipynb    # MPP data upload notebook
│       └── Upload_Temp_Irr_data.ipynb  # Temperature and irradiance data upload notebook
├── sample_data/                 # Sample data for testing
│   └── datasets/                # Organized sample datasets
├── src/                         # Source code
│   ├── api/                     # API layer
│   │   ├── __init__.py          
│   │   ├── models.py            # API data models
│   │   └── routes.py            # API endpoints
│   ├── app/                     # Application layer
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration handling
│   │   └── main.py              # Main application entry point
│   ├── data_processing/         # Data processing modules
│   │   ├── __init__.py
│   │   ├── transformers.py      # Data transformation utilities
│   │   └── validators.py        # Data validation utilities
│   └── ingestion/               # Data ingestion modules
│       ├── __init__.py
│       ├── ingest_data.py       # General data ingestion utilities
│       ├── labview_connector.py # LabVIEW connector for real-time data
│       └── upload_historical_data.py  # Historical data upload script
├── tests/                       # Test directory
│   ├── integration/             # Integration tests
│   └── unit/                    # Unit tests
├── Dockerfile                   # Docker configuration
├── README.md                    # This file
└── requirements.txt             # Python dependencies
```

## Setup

### Prerequisites

- PostgreSQL 13+ with TimescaleDB extension
- Python 3.9+
- LabVIEW (for real-time data collection)

### Installation

1. Clone the repository:
   ```bash
   git clone [repository-url] perocube-data-monitoring-system
   cd perocube-data-monitoring-system
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   chmod +x db/scripts/init_db.sh
   ./db/scripts/init_db.sh
   ```

## Usage

### Starting the API Server

```bash
python -m src.app.main api
```

This will start the FastAPI server that provides access to the data through a RESTful API.

### Starting the LabVIEW Connector

```bash
python -m src.app.main labview
```

This will start a TCP server that listens for data from LabVIEW and stores it in the database.

### Uploading Historical Data

```bash
python -m src.ingestion.upload_historical_data --data-dir /path/to/data --data-type mpp --board 1 --channel 1
```

## API Documentation

Once the API server is running, you can access the Swagger UI at `http://localhost:8000/docs` for interactive API documentation.

Key endpoints:
- `/measurements/mpp` - Get MPP measurements
- `/measurements/temperature` - Get temperature measurements
- `/measurements/irradiance` - Get irradiance measurements
- `/statistics/mpp` - Get MPP statistics
- `/statistics/temperature` - Get temperature statistics
- `/statistics/irradiance` - Get irradiance statistics

## Database Structure

The database is structured with regular PostgreSQL tables for metadata and TimescaleDB hypertables for time-series data. Key tables include:

- `scientist` - Information about scientists
- `experiment` - Information about experiments
- `project` - Information about projects
- `solar_cell_device` - Information about solar cell devices
- `mpp_measurement` (hypertable) - MPP tracking data
- `temperature_measurement` (hypertable) - Temperature data
- `irradiance_measurement` (hypertable) - Irradiance data

## Configuration

The system is configured through YAML files in the `config/` directory:

- `app_config.yaml` - Application configuration
- `logging_config.yaml` - Logging configuration

## Development

### Running Tests

```bash
pytest tests/
```

### Database Backups

To backup the database:

```bash
chmod +x db/scripts/backup_db.sh
./db/scripts/backup_db.sh
```