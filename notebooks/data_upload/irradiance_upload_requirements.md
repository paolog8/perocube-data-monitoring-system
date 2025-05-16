# Requirements for Irradiance Data Upload Notebook

## Scope
This document captures requirements and specifications for creating a Jupyter notebook to process and upload irradiance measurement data to the TimescaleDB database, similar to the existing MPP data upload notebook.

## Implementation Overview
The notebook will:
1. Read irradiance data files with pattern `PT-{sensor_identifier}_channel_{channel}.txt` from data directories
2. Parse the sensor identifier and channel from filenames
3. Generate deterministic UUIDs for sensors using UUID5 with namespace '12345678-1234-5678-1234-567812345678'
4. Create sensors in the database if they don't exist (with NULL location and installation_angle)
5. Process data in batches of 5000 rows
6. Skip files if data already exists for the time range
7. Upload measurements to the TimescaleDB hypertable
8. Log progress and provide basic statistics

## Questions and Answers

### Data Source
- File naming pattern: `{sensor_identifier}_channel_{channel}.txt`
  - Example: For file "PT-104_channel_01.txt":
    - sensor_identifier: "PT-104" (complete identifier including prefix)
    - channel: "01"
  - Note: Current files use "PT-" prefix, but the code should be flexible for future sensors with different prefixes
- Location: Same directory structure as MPP data (under sample_data/datasets/PeroCube-sample-data)

### Data Structure
- Columns:
  1. timestamp (UTC, format: YYYY-MM-DDThh:mm:ss)
  2. raw_reading (numerical value from sensor)
  3. irradiance (presumably in W/m², converted from raw reading)
- File format: Tab-separated values (TSV)
- Data types: 
  - timestamp: datetime
  - raw_reading: numeric (integer)
  - irradiance: numeric (float)

### Data Validation
- Primary focus: Handle NULL/NaN values in timestamp column (critical for TimescaleDB hypertables)
- Further validation rules to be defined in future iterations
- No specific validation requirements for raw_reading and irradiance values at this stage

### Database Schema
Tables:
1. `irradiance_sensor`:
   - irradiance_sensor_id (UUID PRIMARY KEY)
   - date_installed (DATE)
   - location (VARCHAR(255))
   - installation_angle (INTEGER)
   - sensor_identifier (VARCHAR(255)) - Stores complete identifier (e.g., "PT-104")
   - channel (INTEGER)
   - UNIQUE constraint on (sensor_identifier, channel)

2. `irradiance_measurement`:
   - timestamp (TIMESTAMP WITH TIME ZONE NOT NULL)
   - raw_reading (INTEGER)
   - irradiance (FLOAT)
   - irradiance_sensor_id (UUID NOT NULL) - Foreign key to irradiance_sensor table
   - Note: Implemented as a TimescaleDB hypertable with timestamp as the time dimension
   - Has an index on irradiance_sensor_id (idx_irradiance_measurement_sensor)

### Processing Requirements
- Batch Size: 5000 (same as MPP upload)
- Sensor Creation:
  - Use UUID5 with fixed namespace '12345678-1234-5678-1234-567812345678' for irradiance sensor IDs
  - Leave location and installation_angle as NULL when creating new sensors
- Duplicate Data Checking: 
  - Check timestamp ranges for specific sensor_identifier and channel combinations
  - Skip files if data already exists for the time range
- Logging Requirements:
  - Track files processed, skipped, and errors
  - Similar logging approach as MPP upload notebook
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
   - Same directory structure as MPP upload
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
   - Create basic structure following MPP notebook pattern
   - Implement core functionality without validation
   - Test with sample data
   
2. Testing and Validation
   - Test with different file patterns
   - Verify UUID generation
   - Check duplicate handling
   - Validate database entries

3. Error Handling and Logging
   - Add comprehensive error handling
   - Implement logging similar to MPP notebook
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
2. Should we use the same batch size as MPP data upload (5000)?
3. Are there any specific requirements for error handling or logging?
4. Should we implement the same duplicate data checking as in the MPP upload?
5. Do we need to track which files have been processed?

## Continuation Instructions

If this interview needs to be continued at a later time, here's what the interviewer needs to know:

### Current Status
- We have established basic file structure and location
- We have documented data format and columns
- We have decided to focus on timestamp NULL handling as the primary validation
- We have NOT yet discussed database schema or processing requirements

### Next Steps
1. Review the existing database schema (in db/migrations/V1__initial_schema.sql) to understand how irradiance data should be integrated
2. Determine specific processing requirements:
   - Batch size
   - Error handling approach
   - Duplicate data handling
   - File processing tracking
3. Discuss any specific performance requirements or constraints
4. Review any existing irradiance data handling code in the project

### Required Context
The interviewer should have access to:
1. The database schema files
2. Sample irradiance data files
3. The MPP data upload notebook for reference
4. Any existing data processing scripts in the project

### Tools Needed
- Access to TimescaleDB instance
- Python environment with required packages
- Sample data files for testing
