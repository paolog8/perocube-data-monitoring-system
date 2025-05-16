# Requirements for Temperature Data Upload Notebook

## Scope
This document captures requirements and specifications for creating a Jupyter notebook to process and upload temperature measurement data to the TimescaleDB database.

## Implementation Overview
The notebook will:
1. Read temperature data files with pattern `m7004_ID_{identifier}.txt` from data directories
2. Parse the sensor identifier from filenames (format appears to be m7004_ID_XXXXXXXXXXXX where X is a hex value)
3. Generate deterministic UUIDs for sensors using UUID5 with namespace '12345678-1234-5678-1234-567812345678'
4. Create sensors in the database if they don't exist (with NULL location)
5. Process data in batches of 5000 rows
6. Skip files if data already exists for the time range
7. Upload measurements to the TimescaleDB hypertable
8. Log progress and provide basic statistics

## Questions and Answers

### Data Source
- File naming pattern: `m7004_ID_{identifier}.txt`
  - Example: For file "m7004_ID_37F6F9511A64FF28.txt":
    - sensor_identifier: "m7004_ID_37F6F9511A64FF28"
  - Note: All temperature sensor files start with "m7004_ID_" prefix
- Location: Same directory structure as MPP data (under sample_data/datasets/PeroCube-sample-data)

### Data Structure
- Columns:
  1. timestamp (UTC, format: YYYY-MM-DDThh:mm:ss)
  2. temperature (numeric value in degrees Celsius)
- File format: Tab-separated values (TSV)
- Data types: 
  - timestamp: datetime
  - temperature: numeric (float)

### Data Validation
- Primary focus: Handle NULL/NaN values in timestamp column (critical for TimescaleDB hypertables)
- Further validation rules to be defined in future iterations
- No specific validation requirements for temperature values at this stage

### Database Schema
Tables:
1. `temperature_sensor`:
   - temperature_sensor_id (UUID PRIMARY KEY)
   - date_installed (DATE)
   - location (VARCHAR(255))
   - sensor_identifier (VARCHAR(255)) - Stores complete identifier (e.g., "m7004_ID_37F6F9511A64FF28")
   - UNIQUE constraint on sensor_identifier

2. `temperature_measurement`:
   - timestamp (TIMESTAMP WITH TIME ZONE NOT NULL)
   - temperature (FLOAT)
   - temperature_sensor_id (UUID NOT NULL) - Foreign key to temperature_sensor table
   - Note: Implemented as a TimescaleDB hypertable with timestamp as the time dimension
   - Has an index on temperature_sensor_id (idx_temperature_measurement_sensor)

### Processing Requirements
- Batch Size: 5000 (same as irradiance upload)
- Sensor Creation:
  - Use UUID5 with fixed namespace '12345678-1234-5678-1234-567812345678' for sensor IDs
  - Leave location as NULL when creating new sensors
- Duplicate Data Checking: 
  - Check timestamp ranges for specific sensor_identifier
  - Skip files if data already exists for the time range
- Logging Requirements:
  - Track files processed, skipped, and errors
  - Similar logging approach as irradiance upload notebook
  - Basic statistics about number of files and records processed

## Dependencies and Setup
The notebook will require:
1. Python Libraries:
   - pandas: for data processing
   - numpy: for numerical operations
   - uuid: for UUID generation
   - sqlalchemy: for database connection
   - psycopg2-binary: PostgreSQL adapter
   - python-dotenv: for environment variables
   - pathlib: for path handling
   - tqdm: for progress tracking
   - logging: for structured logging

2. Environment Configuration:
   - Database connection parameters from .env file
   - Same directory structure as irradiance upload
   - TimescaleDB instance running

## Implementation Plan

### Notebook Structure
1. Setup and Configuration
   - Import required libraries
   - Configure logging
   - Load environment variables
   - Set database configuration
   - Define constants (batch size, UUID namespace, file patterns)

2. Utility Functions
   - Database connection function
   - Sensor UUID generation (UUID5 with namespace)
   - File pattern matching and info extraction
   - Data validation function (focusing on timestamp NULL handling)
   - Duplicate data checking function
   - Get or create sensor function

3. Main Processing Functions
   - File discovery and filtering
   - Data reading and preprocessing
   - Sensor management
   - Batch processing
   - Database upload

4. Progress Tracking and Statistics
   - Process monitoring using tqdm
   - File counts (processed, skipped, errors)
   - Record counts
   - Execution time tracking

### Development Approach
1. First Implementation
   - Create basic structure following irradiance notebook pattern
   - Implement core functionality without validation
   - Test with sample data
   
2. Testing and Validation
   - Test with different file patterns
   - Verify UUID generation
   - Check duplicate handling
   - Validate database entries

3. Error Handling and Logging
   - Add comprehensive error handling
   - Implement logging similar to irradiance notebook
   - Add progress tracking

### Troubleshooting Notes
This section will be updated during implementation with any issues encountered and their solutions.

## Development Status
All requirements have been gathered and clarified:
- File naming and structure ✓
- Data format and types ✓
- Database schema ✓
- Validation requirements ✓
- Processing requirements ✓
- UUID generation approach ✓
- Error handling and logging ✓

Ready to proceed with notebook creation.
