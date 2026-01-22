-- ================================================================================
-- V6: Create Flexible Equipment Connection Tracking Table
-- ================================================================================
-- This migration creates a generic equipment_connection table to track which
-- measurement equipment was connected to which devices over time, independent
-- of specific hardware architectures (replacing board-channel abstraction).
--
-- ROLLBACK PROCEDURE:
-- If this migration needs to be reverted, Flyway does not support automatic
-- rollback. Manual rollback would require:
-- 1. DROP TABLE equipment_connection CASCADE;
--
-- ================================================================================

-- ================================================================================
-- SECTION 1: Create Equipment Connection Table
-- ================================================================================

CREATE TABLE equipment_connection (
    id SERIAL PRIMARY KEY,
    solar_cell_id VARCHAR(255) NOT NULL,
    pixel VARCHAR(255) NOT NULL DEFAULT 'No pixel',
    equipment_id VARCHAR(255) NOT NULL,
    equipment_type VARCHAR(255) NOT NULL,
    equipment_metadata JSONB,
    connection_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    disconnection_datetime TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    FOREIGN KEY (solar_cell_id) REFERENCES solar_cell_device(name),
    FOREIGN KEY (solar_cell_id, pixel) REFERENCES solar_cell_pixel(solar_cell_id, pixel),
    CHECK (disconnection_datetime IS NULL OR disconnection_datetime > connection_datetime)
);

COMMENT ON TABLE equipment_connection IS
'Tracks connection history between solar cell devices and measurement equipment. Generic design allows flexibility for different hardware architectures.';

COMMENT ON COLUMN equipment_connection.id IS
'Auto-incrementing primary key for equipment connection records';

COMMENT ON COLUMN equipment_connection.solar_cell_id IS
'References the solar cell device name (solar_cell_device.name)';

COMMENT ON COLUMN equipment_connection.pixel IS
'Pixel identifier on the device (default: ''No pixel'' for whole cells)';

COMMENT ON COLUMN equipment_connection.equipment_id IS
'Identifier for the measurement equipment (e.g., serial number, device name, channel ID)';

COMMENT ON COLUMN equipment_connection.equipment_type IS
'Type of equipment (e.g., ''MPP_TRACKER'', ''TEMPERATURE_SENSOR'', ''IRRADIANCE_SENSOR'')';

COMMENT ON COLUMN equipment_connection.equipment_metadata IS
'Flexible JSONB field for equipment-specific configuration (e.g., {\"board\": 1, \"channel\": 2, \"mppt_mode\": \"voltage\", \"current_limit\": 0.5})';

COMMENT ON COLUMN equipment_connection.connection_datetime IS
'Timestamp when equipment was connected to the device';

COMMENT ON COLUMN equipment_connection.disconnection_datetime IS
'Timestamp when equipment was disconnected (NULL if still connected)';

COMMENT ON COLUMN equipment_connection.notes IS
'Optional notes about the connection (e.g., ''Replaced faulty tracker'', ''Moved to new test location'')';

-- ================================================================================
-- SECTION 2: Create Indexes
-- ================================================================================

-- Index for querying connections by device and pixel over time
CREATE INDEX idx_equipment_connection_device_time
    ON equipment_connection(solar_cell_id, pixel, connection_datetime);

-- Index for querying connections by equipment
CREATE INDEX idx_equipment_connection_equipment
    ON equipment_connection(equipment_id, equipment_type);

-- Index for finding currently connected equipment (where disconnection is NULL)
CREATE INDEX idx_equipment_connection_active
    ON equipment_connection(solar_cell_id, pixel)
    WHERE disconnection_datetime IS NULL;

-- Index for time-range queries
CREATE INDEX idx_equipment_connection_time_range
    ON equipment_connection(connection_datetime, disconnection_datetime);

-- ================================================================================
-- SECTION 3: Validation Queries
-- ================================================================================

-- Verify table was created successfully:
-- SELECT
--     table_name,
--     column_name,
--     data_type,
--     is_nullable,
--     column_default
-- FROM information_schema.columns
-- WHERE table_name = 'equipment_connection'
-- ORDER BY ordinal_position;

-- Verify foreign key constraints:
-- SELECT
--     tc.constraint_name,
--     tc.table_name,
--     kcu.column_name,
--     ccu.table_name AS foreign_table_name,
--     ccu.column_name AS foreign_column_name
-- FROM information_schema.table_constraints AS tc
-- JOIN information_schema.key_column_usage AS kcu
--     ON tc.constraint_name = kcu.constraint_name
--     AND tc.table_schema = kcu.table_schema
-- JOIN information_schema.constraint_column_usage AS ccu
--     ON ccu.constraint_name = tc.constraint_name
--     AND ccu.table_schema = tc.table_schema
-- WHERE tc.constraint_type = 'FOREIGN KEY'
--     AND tc.table_name = 'equipment_connection';

-- Verify check constraint:
-- SELECT
--     tc.constraint_name,
--     cc.check_clause
-- FROM information_schema.table_constraints AS tc
-- JOIN information_schema.check_constraints AS cc
--     ON tc.constraint_name = cc.constraint_name
-- WHERE tc.table_name = 'equipment_connection'
--     AND tc.constraint_type = 'CHECK';

-- Verify indexes:
-- SELECT
--     indexname,
--     indexdef
-- FROM pg_indexes
-- WHERE tablename = 'equipment_connection'
-- ORDER BY indexname;

-- ================================================================================
-- SECTION 4: Example Usage
-- ================================================================================

-- Example: Insert a connection event for MPP tracker
-- INSERT INTO equipment_connection (
--     solar_cell_id,
--     pixel,
--     equipment_id,
--     equipment_type,
--     equipment_metadata,
--     connection_datetime,
--     notes
-- ) VALUES (
--     'DEVICE_001',
--     'A',
--     'MPP_TRACKER_CH_1_2',
--     'MPP_TRACKER',
--     '{"board": 1, "channel": 2, "mppt_mode": "voltage", "current_limit": 0.5}'::jsonb,
--     '2025-01-01 10:00:00+00',
--     'Initial connection for outdoor testing'
-- );

-- Example: Record disconnection
-- UPDATE equipment_connection
-- SET disconnection_datetime = '2025-01-15 16:30:00+00',
--     notes = CONCAT(COALESCE(notes, ''), ' | Disconnected for maintenance')
-- WHERE solar_cell_id = 'DEVICE_001'
--   AND pixel = 'A'
--   AND equipment_id = 'MPP_TRACKER_CH_1_2'
--   AND disconnection_datetime IS NULL;

-- Example: Query connection history for a device
-- SELECT
--     equipment_id,
--     equipment_type,
--     equipment_metadata,
--     connection_datetime,
--     disconnection_datetime,
--     EXTRACT(EPOCH FROM (COALESCE(disconnection_datetime, NOW()) - connection_datetime))/3600 as hours_connected,
--     notes
-- FROM equipment_connection
-- WHERE solar_cell_id = 'DEVICE_001'
--   AND pixel = 'A'
-- ORDER BY connection_datetime DESC;

-- Example: Find currently connected equipment
-- SELECT
--     solar_cell_id,
--     pixel,
--     equipment_id,
--     equipment_type,
--     equipment_metadata,
--     connection_datetime,
--     EXTRACT(EPOCH FROM (NOW() - connection_datetime))/3600 as hours_connected
-- FROM equipment_connection
-- WHERE disconnection_datetime IS NULL
-- ORDER BY connection_datetime;

-- Table created successfully
