-- ================================================================================
-- V10: Equipment Connection History Functions
-- ================================================================================
-- This migration adds a helper function to retrieve the connection history
-- of measurement equipment for a specific solar cell device and pixel.
--
-- ROLLBACK PROCEDURE:
-- If this migration needs to be reverted, Flyway does not support automatic
-- rollback. Manual rollback would require:
-- 1. DROP FUNCTION get_equipment_connections_for_device(TEXT, TEXT);
--
-- ================================================================================

-- ================================================================================
-- SECTION 1: Create get_equipment_connections_for_device
-- ================================================================================

CREATE OR REPLACE FUNCTION get_equipment_connections_for_device(
    p_solar_cell_id TEXT,
    p_pixel TEXT DEFAULT 'No pixel'
)
RETURNS TABLE (
    equipment_id VARCHAR(255),
    equipment_type VARCHAR(255),
    equipment_metadata JSONB,
    connection_datetime TIMESTAMP WITH TIME ZONE,
    disconnection_datetime TIMESTAMP WITH TIME ZONE,
    notes TEXT
)
AS $$
BEGIN
    -- This function allows researchers to trace which equipment was used
    -- for measurements on a specific device over time.
    
    RETURN QUERY
    SELECT
        ec.equipment_id,
        ec.equipment_type,
        ec.equipment_metadata,
        ec.connection_datetime,
        ec.disconnection_datetime,
        ec.notes
    FROM
        equipment_connection ec
    WHERE
        ec.solar_cell_id = p_solar_cell_id
        AND ec.pixel = p_pixel
    ORDER BY
        ec.connection_datetime DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_equipment_connections_for_device IS
'Retrieves the full history of measurement equipment connected to a specific solar cell device and pixel, ordered by connection date (most recent first).';

-- ================================================================================
-- SECTION 2: Example Usage and Testing
-- ================================================================================

-- Example 1: Get connection history for a specific pixel
-- SELECT * FROM get_equipment_connections_for_device('DEVICE_001', 'A');

-- Example 2: Get history for a whole device (defaulting to 'No pixel')
-- SELECT * FROM get_equipment_connections_for_device('DEVICE_001');

-- Example 3: Filter for active connections only
-- SELECT * FROM get_equipment_connections_for_device('DEVICE_001', 'A') 
-- WHERE disconnection_datetime IS NULL;

-- ================================================================================
-- SECTION 3: Validation
-- ================================================================================

-- Verify function exists:
-- SELECT 
--     n.nspname as schema,
--     p.proname as function_name,
--     pg_get_function_arguments(p.oid) as arguments
-- FROM pg_proc p
-- JOIN pg_namespace n ON p.pronamespace = n.oid
-- WHERE p.proname = 'get_equipment_connections_for_device';
