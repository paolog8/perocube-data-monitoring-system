-- ================================================================================
-- V8: Remove Obsolete Board-Channel Tables
-- ================================================================================
-- This migration removes the old board-channel infrastructure tables and
-- associated functions, as they have been replaced by the device-centric 
-- equipment_connection table.
--
-- ROLLBACK PROCEDURE:
-- If this migration needs to be reverted, Flyway does not support automatic
-- rollback. Manual rollback would require recreating the tables and functions
-- from V1, V2, and V3.
-- ================================================================================

-- ================================================================================
-- SECTION 1: Drop Dependent Functions
-- ================================================================================

-- Drop functions from V2
DROP FUNCTION IF EXISTS get_pixel_activity_range(VARCHAR, VARCHAR) CASCADE;
DROP FUNCTION IF EXISTS get_mpp_data_for_pixel(VARCHAR, VARCHAR, TIMESTAMP WITH TIME ZONE, TIMESTAMP WITH TIME ZONE) CASCADE;
DROP FUNCTION IF EXISTS get_mpp_data_for_pixel(VARCHAR, VARCHAR) CASCADE;
DROP FUNCTION IF EXISTS get_queryable_solar_cell_pixels() CASCADE;

-- Drop functions from V3
DROP FUNCTION IF EXISTS get_board_connection_status(TIMESTAMP WITH TIME ZONE) CASCADE;
DROP FUNCTION IF EXISTS get_board_connection_status(TIMESTAMP WITH TIME ZONE, TIMESTAMP WITH TIME ZONE) CASCADE;

-- ================================================================================
-- SECTION 2: Drop Obsolete Tables
-- ================================================================================

-- Drop obsolete tables (data was archived in V5)
DROP TABLE IF EXISTS measurement_connection_event CASCADE;
DROP TABLE IF EXISTS mpp_tracking_channel CASCADE;

-- ================================================================================
-- SECTION 3: Verification
-- ================================================================================

-- Verify tables are gone:
-- SELECT table_name FROM information_schema.tables WHERE table_name IN ('measurement_connection_event', 'mpp_tracking_channel');
