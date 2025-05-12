# Perocube Data Monitoring System

A PostgreSQL+TimescaleDB system for monitoring perocube data at PVcomB. This system collects, stores, and provides access to time-series data from solar cell devices.

## Project Structure

```
perocube-data-monitoring-system/
├── config/
│   ├── app_config.yaml
│   └── logging_config.yaml
├── db/
│   ├── config/
│   │   └── timescaledb.conf
│   ├── migrations/
│   │   └── V1__initial_schema.sql
│   ├── scripts/
│   │   ├── backup_db.sh
│   │   └── init_db.sh
│   └── sql/
│       ├── functions/
│       ├── queries/
│       └── schema/              
│           ├── init.sql         # Database initialization
│           ├── tables.sql
│           └── indexes.sql
├── docs/
│   ├── architecture/
│   └── data-models/
│       └── logical-data-model.mmd
├── logs/                        # Created at runtime
├── notebooks/
│   ├── analysis/
│   └── data_upload/
│       ├── Upload_MPP_data.ipynb
│       └── Upload_Temp_Irr_data.ipynb
├── sample_data/
│   └── datasets/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── routes.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── main.py
│   ├── data_processing/
│   │   ├── __init__.py
│   │   ├── transformers.py
│   │   └── validators.py
│   └── ingestion/
│       ├── __init__.py
│       ├── ingest_data.py
│       ├── labview_connector.py         # Connector for real-time data collection
│       └── upload_historical_data.py
├── tests/
│   ├── integration/
│   └── unit/
├── Dockerfile
├── README.md
└── requirements.txt
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

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize database:
   ```bash
   chmod +x db/scripts/init_db.sh
   ./db/scripts/init_db.sh
   ```

## Usage

### API Server

```bash
python -m src.app.main api
```

### LabVIEW Data Collection

```bash
python -m src.app.main labview
```

### Historical Data Upload

```bash
python -m src.ingestion.upload_historical_data --data-dir /path/to/data --data-type mpp --board 1 --channel 1
```

## API Documentation

The Swagger UI is available at `http://localhost:8000/docs`.

Key endpoints:
- `/measurements/mpp`
- `/measurements/temperature`
- `/measurements/irradiance`
- `/statistics/mpp`
- `/statistics/temperature`
- `/statistics/irradiance`

## Database Structure

The database uses regular PostgreSQL tables for metadata and TimescaleDB hypertables for time-series data:

- `scientist`
- `experiment`
- `project`
- `solar_cell_device`
- `mpp_measurement` (hypertable)
- `temperature_measurement` (hypertable)
- `irradiance_measurement` (hypertable)

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