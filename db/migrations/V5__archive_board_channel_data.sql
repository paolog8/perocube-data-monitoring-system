-- ================================================================================
-- V4: Archive Board-Channel Architecture Data
-- ================================================================================
-- This migration preserves existing MPP tracking data and board-channel
-- infrastructure before refactoring to a device-centric schema.
--
-- ROLLBACK PROCEDURE:
-- If this migration needs to be reverted, Flyway does not support automatic
-- rollback. Manual rollback would require:
-- 1. DROP TABLE mpp_measurement_archive CASCADE;
-- 2. DROP TABLE measurement_connection_event_archive CASCADE;
-- 3. DROP TABLE mpp_tracking_channel_archive CASCADE;
--
-- ================================================================================

-- ================================================================================
-- SECTION 1: Create Archive Tables
-- ================================================================================

-- Archive table for mpp_tracking_channel
-- Preserves the board-channel hardware configuration that was in use
CREATE TABLE mpp_tracking_channel_archive (
    board INTEGER,
    channel INTEGER,
    address VARCHAR(255),
    com_port VARCHAR(255),
    current_limit FLOAT,
    archived_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (board, channel)
);

COMMENT ON TABLE mpp_tracking_channel_archive IS
'Archive of MPP tracking channel configurations before schema refactoring. Contains board-channel hardware setup that was used for historical measurements.';

COMMENT ON COLUMN mpp_tracking_channel_archive.archived_at IS
'Timestamp when this record was archived during migration V4';

-- Archive table for measurement_connection_event
-- Preserves the connection history between devices and board-channel trackers
CREATE TABLE measurement_connection_event_archive (
    solar_cell_id VARCHAR(255) NOT NULL,
    pixel VARCHAR(255) DEFAULT 'No pixel',
    tracking_channel_board INTEGER,
    tracking_channel_channel INTEGER,
    temperature_sensor_id UUID,
    irradiance_sensor_id UUID,
    mppt_mode VARCHAR(255),
    mppt_polarity VARCHAR(255),
    connection_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    event_type VARCHAR(255) NOT NULL CHECK (event_type IN ('CONNECTED', 'DISCONNECTED')),
    archived_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (solar_cell_id, pixel, connection_datetime, event_type)
);

COMMENT ON TABLE measurement_connection_event_archive IS
'Archive of connection events showing when devices were connected/disconnected to/from board-channel MPP trackers. Critical for understanding the context of archived MPP measurements.';

COMMENT ON COLUMN measurement_connection_event_archive.archived_at IS
'Timestamp when this record was archived during migration V4';

-- Archive table for mpp_measurement (regular table, not hypertable)
-- Preserves all historical MPP measurement data
CREATE TABLE mpp_measurement_archive (
    "timestamp" TIMESTAMP WITH TIME ZONE NOT NULL,
    current FLOAT,
    voltage FLOAT,
    power FLOAT,
    tracking_channel_board INTEGER NOT NULL,
    tracking_channel_channel INTEGER NOT NULL,
    archived_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE mpp_measurement_archive IS
'Archive of all MPP measurements before schema refactoring. Data is indexed by board-channel, use measurement_connection_event_archive to map to specific devices.';

COMMENT ON COLUMN mpp_measurement_archive.archived_at IS
'Timestamp when this record was archived during migration V4';

-- Create indexes on archive tables for efficient querying
CREATE INDEX idx_mpp_measurement_archive_time
    ON mpp_measurement_archive("timestamp" DESC);

CREATE INDEX idx_mpp_measurement_archive_channel
    ON mpp_measurement_archive(tracking_channel_board, tracking_channel_channel, "timestamp" DESC);

CREATE INDEX idx_connection_event_archive_device
    ON measurement_connection_event_archive(solar_cell_id, pixel, connection_datetime);

CREATE INDEX idx_connection_event_archive_channel
    ON measurement_connection_event_archive(tracking_channel_board, tracking_channel_channel);

-- ================================================================================
-- SECTION 2: Copy Data to Archive Tables
-- ================================================================================

-- Copy mpp_tracking_channel data
INSERT INTO mpp_tracking_channel_archive (board, channel, address, com_port, current_limit)
SELECT board, channel, address, com_port, current_limit
FROM mpp_tracking_channel;

-- Copy measurement_connection_event data
INSERT INTO measurement_connection_event_archive
    (solar_cell_id, pixel, tracking_channel_board, tracking_channel_channel,
     temperature_sensor_id, irradiance_sensor_id, mppt_mode, mppt_polarity,
     connection_datetime, event_type)
SELECT
    solar_cell_id, pixel, tracking_channel_board, tracking_channel_channel,
    temperature_sensor_id, irradiance_sensor_id, mppt_mode, mppt_polarity,
    connection_datetime, event_type
FROM measurement_connection_event;

-- Copy mpp_measurement data
-- IMPORTANT: Skipped due to large data volume (268M+ rows)
-- Historical MPP data remains accessible in the original mpp_measurement table
-- until it is dropped in a later migration. At that point, if archiving is needed,
-- a separate offline process should be used (pg_dump, COPY TO, etc.)
--
-- Uncomment and run separately if archiving is required:
-- INSERT INTO mpp_measurement_archive ("timestamp", current, voltage, power, tracking_channel_board, tracking_channel_channel)
-- SELECT "timestamp", current, voltage, power, tracking_channel_board, tracking_channel_channel
-- FROM mpp_measurement;

-- ================================================================================
-- SECTION 3: Verify Archive Integrity
-- ================================================================================

-- Validation queries (as comments for DBA reference)
--
-- Verify row counts match for metadata tables:
-- SELECT
--     (SELECT COUNT(*) FROM mpp_tracking_channel) as original_channels,
--     (SELECT COUNT(*) FROM mpp_tracking_channel_archive) as archived_channels,
--     (SELECT COUNT(*) FROM measurement_connection_event) as original_events,
--     (SELECT COUNT(*) FROM measurement_connection_event_archive) as archived_events;
--
-- Expected result: Each pair should have matching counts
--
-- Note: mpp_measurement_archive is empty by design (data volume too large).
-- Historical data remains in the original mpp_measurement table.
--
-- Verify archive timestamps were set:
-- SELECT MIN(archived_at), MAX(archived_at), COUNT(*)
-- FROM mpp_tracking_channel_archive;
--
-- SELECT MIN(archived_at), MAX(archived_at), COUNT(*)
-- FROM measurement_connection_event_archive;
--
-- SELECT MIN(archived_at), MAX(archived_at), COUNT(*)
-- FROM mpp_measurement_archive;
--
-- Verify data integrity - check sample records exist in both tables:
-- SELECT * FROM mpp_tracking_channel LIMIT 5;
-- SELECT board, channel, address, com_port, current_limit FROM mpp_tracking_channel_archive LIMIT 5;
--
-- ================================================================================
-- SECTION 4: Archive Access Pattern Documentation
-- ================================================================================

-- To query archived MPP data for a specific device and time period:
--
-- WITH device_connections AS (
--     SELECT
--         mcea.tracking_channel_board,
--         mcea.tracking_channel_channel,
--         mcea.connection_datetime,
--         LEAD(mcea.connection_datetime) OVER (
--             PARTITION BY mcea.solar_cell_id, mcea.pixel
--             ORDER BY mcea.connection_datetime
--         ) as next_event_time,
--         mcea.event_type
--     FROM measurement_connection_event_archive mcea
--     WHERE mcea.solar_cell_id = 'YOUR_DEVICE_NAME'
--       AND mcea.pixel = 'YOUR_PIXEL'
-- )
-- SELECT
--     mma."timestamp",
--     mma.current,
--     mma.voltage,
--     mma.power
-- FROM mpp_measurement_archive mma
-- JOIN device_connections dc
--     ON mma.tracking_channel_board = dc.tracking_channel_board
--    AND mma.tracking_channel_channel = dc.tracking_channel_channel
-- WHERE dc.event_type = 'CONNECTED'
--   AND mma."timestamp" >= dc.connection_datetime
--   AND (dc.next_event_time IS NULL OR mma."timestamp" < dc.next_event_time)
-- ORDER BY mma."timestamp";

-- Archive created successfully
