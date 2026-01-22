-- ================================================================================
-- V9: Update MPP Retrieval Functions
-- ================================================================================
-- This migration recreates the get_mpp_data_for_pixel function to work with
-- the new device-centric schema, removing board-channel dependencies.
--
-- ROLLBACK PROCEDURE:
-- If this migration needs to be reverted, Flyway does not support automatic
-- rollback. Manual rollback would require:
-- 1. DROP FUNCTION get_mpp_data_for_pixel(TEXT, TEXT, TIMESTAMPTZ, TIMESTAMPTZ);
--
-- ================================================================================

-- ================================================================================
-- SECTION 1: Recreate get_mpp_data_for_pixel
-- ================================================================================

-- Note: Old overloads were already dropped in V8.

CREATE OR REPLACE FUNCTION get_mpp_data_for_pixel(
    p_solar_cell_id TEXT,
    p_pixel TEXT,
    p_start_time TIMESTAMPTZ DEFAULT NULL,
    p_end_time TIMESTAMPTZ DEFAULT NULL
)
RETURNS TABLE (
    "time" TIMESTAMPTZ,
    voltage DOUBLE PRECISION,
    current DOUBLE PRECISION,
    power DOUBLE PRECISION,
    fill_factor DOUBLE PRECISION,
    efficiency DOUBLE PRECISION
)
AS $$
BEGIN
    -- This function retrieves MPP measurement data for a specific device and pixel.
    -- It simplifies retrieval by querying the device-centric mpp_measurement table
    -- directly, eliminating the need for complex joins with connection events.
    
    RETURN QUERY
    SELECT
        m.time,
        m.voltage,
        m.current,
        m.power,
        m.fill_factor,
        m.efficiency
    FROM
        mpp_measurement m
    WHERE
        m.solar_cell_id = p_solar_cell_id
        AND m.pixel = p_pixel
        -- Handle optional start time (default to earliest if NULL)
        AND (p_start_time IS NULL OR m.time >= p_start_time)
        -- Handle optional end time (default to latest if NULL)
        AND (p_end_time IS NULL OR m.time <= p_end_time)
    ORDER BY
        m.time ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_mpp_data_for_pixel IS
'Retrieves MPP measurement data for a specific solar cell and pixel within an optional time range. Queries the device-centric mpp_measurement table directly.';

-- ================================================================================
-- SECTION 2: Example Usage and Testing
-- ================================================================================

-- Example 1: Query all data for a specific device and pixel
-- SELECT * FROM get_mpp_data_for_pixel('DEVICE_001', 'A');

-- Example 2: Query data within a specific time range
-- SELECT * FROM get_mpp_data_for_pixel('DEVICE_001', 'A', '2025-01-01 00:00:00+00', '2025-01-01 23:59:59+00');

-- Example 3: Query data from a start time onwards
-- SELECT * FROM get_mpp_data_for_pixel('DEVICE_001', 'A', p_start_time => '2025-01-01 12:00:00+00');
