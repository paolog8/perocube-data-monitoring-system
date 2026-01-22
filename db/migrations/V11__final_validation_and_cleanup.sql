-- ================================================================================
-- V11: Final Validation and Documentation
-- ================================================================================
-- This migration provides final validation queries and documentation for the
-- new device-centric schema, and includes example data insertion scripts.
--
-- This migration does not modify the schema but serves as a central point for
-- verification and example usage of the refactored database.
--
-- ROLLBACK PROCEDURE:
-- N/A - This migration only contains comments and documentation.
-- ================================================================================

-- ================================================================================
-- SECTION 1: Example Data Insertion
-- ================================================================================

/*
-- EXAMPLE: How to use the new schema for a new measurement session

-- 1. Record the connection of a device to an MPP tracker
INSERT INTO equipment_connection (
    solar_cell_id,
    pixel,
    equipment_id,
    equipment_type,
    equipment_metadata,
    connection_datetime,
    notes
) VALUES (
    'TEST_DEVICE_001',
    'Pixel_1',
    'MPPT_UNIT_A',
    'MPP_TRACKER',
    '{"hardware_rev": "2.1", "firmware": "1.0.4", "port": "/dev/ttyUSB0"}'::jsonb,
    '2026-01-22 10:00:00+00',
    'Outdoor stability test'
);

-- 2. Insert measurements referencing the device directly
INSERT INTO mpp_measurement (
    time,
    solar_cell_id,
    pixel,
    voltage,
    current,
    power,
    fill_factor,
    efficiency
) VALUES 
('2026-01-22 10:00:01+00', 'TEST_DEVICE_001', 'Pixel_1', 0.61, 0.025, 0.01525, 0.72, 0.15),
('2026-01-22 10:00:02+00', 'TEST_DEVICE_001', 'Pixel_1', 0.62, 0.026, 0.01612, 0.73, 0.16);

-- 3. Record disconnection when the experiment ends
UPDATE equipment_connection
SET disconnection_datetime = '2026-01-22 12:00:00+00',
    notes = notes || ' | Experiment completed successfully'
WHERE solar_cell_id = 'TEST_DEVICE_001'
  AND pixel = 'Pixel_1'
  AND equipment_id = 'MPPT_UNIT_A'
  AND disconnection_datetime IS NULL;
*/

-- ================================================================================
-- SECTION 2: Comprehensive Validation Queries
-- ================================================================================

-- Query 1: Check New Schema Structures
-- SELECT table_name, column_name, data_type, is_nullable
-- FROM information_schema.columns 
-- WHERE table_name IN ('mpp_measurement', 'equipment_connection')
-- ORDER BY table_name, ordinal_position;

-- Query 2: Verify Hypertable Configuration
-- SELECT hypertable_name, time_column, num_dimensions, chunk_time_interval
-- FROM timescaledb_information.hypertables 
-- WHERE hypertable_name = 'mpp_measurement';

-- Query 3: Verify Foreign Key Integrity
-- SELECT
--     tc.table_name, kcu.column_name, 
--     ccu.table_name AS foreign_table_name,
--     ccu.column_name AS foreign_column_name 
-- FROM information_schema.table_constraints AS tc 
-- JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
-- JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
-- WHERE tc.constraint_type = 'FOREIGN KEY' 
--   AND tc.table_name IN ('mpp_measurement', 'equipment_connection');

-- Query 4: Check Archive Data Status
-- SELECT 
--     'mpp_tracking_channel_archive' as table, COUNT(*) as rows FROM mpp_tracking_channel_archive
-- UNION ALL
-- SELECT 
--     'measurement_connection_event_archive', COUNT(*) FROM measurement_connection_event_archive;

-- Query 5: Test Retrieval Functions
-- SELECT * FROM get_mpp_data_for_pixel('TEST_DEVICE_001', 'Pixel_1') LIMIT 5;
-- SELECT * FROM get_equipment_connections_for_device('TEST_DEVICE_001', 'Pixel_1');

-- ================================================================================
-- SECTION 3: Rollback Plan (Summary)
-- ================================================================================
/*
To roll back the entire Board-Channel removal (V6-V11):
1. Export any new data from mpp_measurement and equipment_connection.
2. DROP TABLE equipment_connection CASCADE;
3. DROP TABLE mpp_measurement CASCADE;
4. Recreate mpp_tracking_channel and measurement_connection_event (from V1).
5. Restore data from archive tables to original tables.
6. Recreate old mpp_measurement hypertable (from V1).
7. Recreate all original functions and views (from V2, V3, V4).
*/
