-- ================================================================================
-- V7: Refactor MPP Measurement Table
-- ================================================================================
-- This migration drops the old board-channel based mpp_measurement hypertable
-- and creates a new device-centric mpp_measurement hypertable.
--
-- ROLLBACK PROCEDURE:
-- If this migration needs to be reverted, Flyway does not support automatic
-- rollback. Manual rollback would require:
-- 1. DROP TABLE mpp_measurement CASCADE;
-- 2. (Recreate old table structure and hypertable - see V1)
--
-- ================================================================================

-- ================================================================================
-- SECTION 1: Drop Dependent Objects
-- ================================================================================

-- Drop views that depend on mpp_measurement
DROP VIEW IF EXISTS data_health_average_frequency CASCADE;
DROP VIEW IF EXISTS data_health_weekly_measurements CASCADE;
DROP VIEW IF EXISTS data_health_daily_measurements CASCADE;
DROP VIEW IF EXISTS data_health_last_seen CASCADE;

-- Drop functions that depend on mpp_measurement
DROP FUNCTION IF EXISTS get_data_gaps CASCADE;

-- ================================================================================
-- SECTION 2: Refactor MPP Measurement Table
-- ================================================================================

-- Drop existing mpp_measurement table (data volume was preserved in original table
-- but not copied to archive in V5 due to size. By dropping now, we are 
-- acknowledging that historical data is handled elsewhere if needed).
DROP TABLE IF EXISTS mpp_measurement CASCADE;

-- Create new mpp_measurement table with device-centric schema
CREATE TABLE mpp_measurement (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    solar_cell_id VARCHAR(255) NOT NULL,
    pixel VARCHAR(255) NOT NULL DEFAULT 'No pixel',
    voltage DOUBLE PRECISION,
    current DOUBLE PRECISION,
    power DOUBLE PRECISION,
    fill_factor DOUBLE PRECISION,
    efficiency DOUBLE PRECISION
);

-- Add foreign key constraints
ALTER TABLE mpp_measurement 
    ADD CONSTRAINT fk_mpp_solar_cell_device 
    FOREIGN KEY (solar_cell_id) REFERENCES solar_cell_device(name);

ALTER TABLE mpp_measurement 
    ADD CONSTRAINT fk_mpp_solar_cell_pixel 
    FOREIGN KEY (solar_cell_id, pixel) REFERENCES solar_cell_pixel(solar_cell_id, pixel);

-- Convert to hypertable with 7-day chunks (as recommended)
SELECT create_hypertable('mpp_measurement', 'time', chunk_time_interval => INTERVAL '7 days');

-- Create index for efficient device-based queries
CREATE INDEX idx_mpp_measurement_device_pixel_time 
    ON mpp_measurement (solar_cell_id, pixel, time DESC);

-- ================================================================================
-- SECTION 3: Documentation and Comments
-- ================================================================================

COMMENT ON TABLE mpp_measurement IS
'High-frequency MPP tracking measurements, referencing devices directly to eliminate hardware dependency.';

COMMENT ON COLUMN mpp_measurement.time IS 'Timestamp of the measurement';
COMMENT ON COLUMN mpp_measurement.solar_cell_id IS 'References the solar cell device name';
COMMENT ON COLUMN mpp_measurement.pixel IS 'Identifier for the specific pixel on the device';
COMMENT ON COLUMN mpp_measurement.voltage IS 'Measured voltage (V)';
COMMENT ON COLUMN mpp_measurement.current IS 'Measured current (A)';
COMMENT ON COLUMN mpp_measurement.power IS 'Calculated power (W)';
COMMENT ON COLUMN mpp_measurement.fill_factor IS 'Calculated fill factor (0-1)';
COMMENT ON COLUMN mpp_measurement.efficiency IS 'Calculated power conversion efficiency (0-1)';

-- ================================================================================
-- SECTION 4: Validation
-- ================================================================================

-- To verify the new table:
-- SELECT * FROM mpp_measurement LIMIT 0;

-- To verify hypertable status:
-- SELECT * FROM timescaledb_information.hypertables WHERE hypertable_name = 'mpp_measurement';
