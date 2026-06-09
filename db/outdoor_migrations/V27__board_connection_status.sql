-- Function to get the connection status of all boards and channels at a specific time
CREATE OR REPLACE FUNCTION get_board_connection_status(
    p_check_time TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
RETURNS TABLE (
    board_number INTEGER,
    channel_number INTEGER,
    solar_cell_name VARCHAR(255),
    pixel_identifier VARCHAR(255),
    is_active INTEGER,
    last_event_time TIMESTAMP WITH TIME ZONE,
    last_event_type VARCHAR(255)
)
AS $$
BEGIN
    -- This function returns the connection status of all boards and channels
    -- at a specific point in time. For each board/channel combination:
    -- - Returns the cell/pixel currently connected to it (if any)
    -- - Returns whether it's active (1) or inactive (0)
    -- - Returns the timestamp and type of the last connection event
    
    RETURN QUERY
    WITH LastEvents AS (
        -- Get the most recent event for each board/channel before the check time
        SELECT DISTINCT ON (tracking_channel_board, tracking_channel_channel)
            tracking_channel_board,
            tracking_channel_channel,
            solar_cell_id,
            pixel,
            connection_datetime,
            event_type,
            -- Convert event type to active status (1 for CONNECTED, 0 for DISCONNECTED)
            CASE 
                WHEN event_type = 'CONNECTED' THEN 1
                ELSE 0
            END as active_status
        FROM 
            measurement_connection_event
        WHERE 
            connection_datetime <= p_check_time
        ORDER BY 
            tracking_channel_board,
            tracking_channel_channel,
            connection_datetime DESC
    )
    SELECT
        le.tracking_channel_board as board_number,
        le.tracking_channel_channel as channel_number,
        le.solar_cell_id as solar_cell_name,
        le.pixel as pixel_identifier,
        le.active_status as is_active,
        le.connection_datetime as last_event_time,
        le.event_type as last_event_type
    FROM 
        LastEvents le
    ORDER BY
        le.tracking_channel_board,
        le.tracking_channel_channel;
END;
$$ LANGUAGE plpgsql;

-- Overloaded function to get connection status history between two timestamps
CREATE OR REPLACE FUNCTION get_board_connection_status(
    p_start_time TIMESTAMP WITH TIME ZONE,
    p_end_time TIMESTAMP WITH TIME ZONE
)
RETURNS TABLE (
    board_number INTEGER,
    channel_number INTEGER,
    solar_cell_name VARCHAR(255),
    pixel_identifier VARCHAR(255),
    is_active INTEGER,
    event_time TIMESTAMP WITH TIME ZONE,
    event_type VARCHAR(255)
)
AS $$
BEGIN
    -- This overloaded version returns the connection status history
    -- for all boards and channels between two timestamps
    
    RETURN QUERY
    SELECT
        mce.tracking_channel_board as board_number,
        mce.tracking_channel_channel as channel_number,
        mce.solar_cell_id as solar_cell_name,
        mce.pixel as pixel_identifier,
        CASE 
            WHEN mce.event_type = 'CONNECTED' THEN 1
            ELSE 0
        END as is_active,
        mce.connection_datetime as event_time,
        mce.event_type
    FROM 
        measurement_connection_event mce
    WHERE 
        mce.connection_datetime BETWEEN p_start_time AND p_end_time
    ORDER BY
        mce.tracking_channel_board,
        mce.tracking_channel_channel,
        mce.connection_datetime;
END;
$$ LANGUAGE plpgsql;
