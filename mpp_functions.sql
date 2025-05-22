-- Helper function to determine the default activity range for a pixel
CREATE OR REPLACE FUNCTION get_pixel_activity_range(
    p_solar_cell_id_in VARCHAR(255),
    p_pixel_in VARCHAR(255)
)
RETURNS TABLE (
    calculated_start_datetime TIMESTAMP WITH TIME ZONE,
    calculated_end_datetime TIMESTAMP WITH TIME ZONE
)
AS $$
DECLARE
    v_first_connected_ts TIMESTAMP WITH TIME ZONE;
    v_last_event_ts TIMESTAMP WITH TIME ZONE;
    v_last_event_type VARCHAR(255);
BEGIN
    -- This helper function calculates a default time range for a given solar cell pixel.
    -- The start time is the timestamp of the first 'CONNECTED' event.
    -- The end time is the timestamp of the last 'DISCONNECTED' event, or NOW()
    -- if the pixel is currently considered connected (i.e., the last event was 'CONNECTED').

    -- Find the timestamp of the first 'CONNECTED' event for the specified pixel
    SELECT MIN(mce.connection_datetime)
    INTO v_first_connected_ts
    FROM measurement_connection_event mce
    WHERE mce.solar_cell_id = p_solar_cell_id_in
      AND mce.pixel = p_pixel_in
      AND mce.event_type = 'CONNECTED';

    IF v_first_connected_ts IS NULL THEN
        -- If no 'CONNECTED' events are found, there's no activity range.
        -- Both start and end will be NULL.
        calculated_start_datetime := NULL;
        calculated_end_datetime := NULL;
    ELSE
        -- A 'CONNECTED' event exists, so set the start time.
        calculated_start_datetime := v_first_connected_ts;

        -- Find the timestamp and type of the very last event (connected or disconnected) for this pixel.
        SELECT mce.connection_datetime, mce.event_type
        INTO v_last_event_ts, v_last_event_type
        FROM measurement_connection_event mce
        WHERE mce.solar_cell_id = p_solar_cell_id_in
          AND mce.pixel = p_pixel_in
        ORDER BY mce.connection_datetime DESC
        LIMIT 1;

        -- Determine the end datetime based on the last event type.
        IF v_last_event_type = 'CONNECTED' THEN
            -- If the last recorded event was a connection, the activity is considered ongoing up to NOW().
            calculated_end_datetime := NOW();
        ELSE
            -- If the last event was 'DISCONNECTED' (or any other type),
            -- the activity ends at that event's timestamp.
            calculated_end_datetime := v_last_event_ts;
        END IF;
    END IF;

    RETURN NEXT; -- Required for TABLE functions in PL/pgSQL to return the row.
END;
$$ LANGUAGE plpgsql;

-- Original function to get MPP data with explicit start and end datetimes
CREATE OR REPLACE FUNCTION get_mpp_data_for_pixel(
    p_solar_cell_id VARCHAR(255),      -- Corresponds to solar_cell_device.name
    p_pixel VARCHAR(255),
    p_start_datetime TIMESTAMP WITH TIME ZONE,
    p_end_datetime TIMESTAMP WITH TIME ZONE
)
RETURNS TABLE (
    "timestamp" TIMESTAMP WITH TIME ZONE,
    current FLOAT,
    voltage FLOAT,
    power FLOAT,
    tracking_channel_board INTEGER,
    tracking_channel_channel INTEGER,
    connection_event_time TIMESTAMP WITH TIME ZONE -- Timestamp of the 'CONNECTED' event for this data period
)
AS $$
BEGIN
    -- This function retrieves Maximum Power Point (MPP) tracking data for a specific
    -- solar cell pixel within a defined time range.
    -- It considers the connection history of the pixel to ensure that only data
    -- from active connection periods to an MPP tracker is returned.

    -- CTE to identify all relevant events for the given pixel and determine the
    -- timestamp of the next event. This helps define the end of the current event's applicability.
    RETURN QUERY
    WITH connection_periods AS (
        SELECT
            mce.connection_datetime AS event_ts, -- Timestamp of the current connection event
            mce.event_type,                     -- Type of event ('CONNECTED' or 'DISCONNECTED')
            mce.tracking_channel_board,
            mce.tracking_channel_channel,
            -- Find the timestamp of the next event for this specific solar_cell_id and pixel.
            -- If no subsequent event, use the end of the query window (p_end_datetime) plus a microsecond
            -- as the upper bound for the period. This ensures the last period is included.
            LEAD(mce.connection_datetime, 1, p_end_datetime + INTERVAL '1 microsecond')
                OVER (PARTITION BY mce.solar_cell_id, mce.pixel ORDER BY mce.connection_datetime) AS next_event_ts
        FROM
            measurement_connection_event mce
        WHERE
            mce.solar_cell_id = p_solar_cell_id
            AND mce.pixel = p_pixel
            -- Consider events that start before or at the query window's end,
            -- as they might define a period that overlaps with the query window.
            AND mce.connection_datetime <= p_end_datetime
    ),
    -- CTE to filter for 'CONNECTED' events and define their effective active intervals
    -- within the requested query window [p_start_datetime, p_end_datetime].
    active_connection_intervals AS (
        SELECT
            cp.event_ts AS period_start_event_time, -- The actual timestamp of the 'CONNECTED' event
            -- The effective start of the period for fetching MPP data:
            -- Max of the connection event time and the query window start.
            GREATEST(cp.event_ts, p_start_datetime) AS effective_period_start,
            -- The effective end of the period for fetching MPP data:
            -- Min of the next event's time and the query window end (plus a microsecond for boundary conditions).
            LEAST(cp.next_event_ts, p_end_datetime + INTERVAL '1 microsecond') AS effective_period_end,
            cp.tracking_channel_board,
            cp.tracking_channel_channel
        FROM
            connection_periods cp
        WHERE
            cp.event_type = 'CONNECTED'  -- Only interested in periods initiated by a 'CONNECTED' event.
            -- Ensure the connection period is valid (start time is before end time).
            AND cp.event_ts < LEAST(cp.next_event_ts, p_end_datetime + INTERVAL '1 microsecond')
            -- Ensure the connection period overlaps with the query window:
            -- Connection must start before the query window ends.
            AND cp.event_ts < (p_end_datetime + INTERVAL '1 microsecond')
            -- Connection period must end after the query window starts.
            AND cp.next_event_ts > p_start_datetime
    )
    -- Final SELECT to retrieve MPP measurements that fall within any of the
    -- identified active connection intervals and the overall query window.
    SELECT
        mpp."timestamp",
        mpp.current,
        mpp.voltage,
        mpp.power,
        aci.tracking_channel_board,
        aci.tracking_channel_channel,
        aci.period_start_event_time AS connection_event_time -- Include the 'CONNECTED' event time for context
    FROM
        active_connection_intervals aci
    JOIN
        mpp_measurement mpp ON mpp.tracking_channel_board = aci.tracking_channel_board
                           AND mpp.tracking_channel_channel = aci.tracking_channel_channel
    WHERE
        -- Filter MPP measurements to be within the precise effective start and end of each active period.
        -- The end of the period (effective_period_end) is exclusive.
        mpp."timestamp" >= aci.effective_period_start
        AND mpp."timestamp" < aci.effective_period_end
    ORDER BY
        mpp."timestamp"; -- Return data chronologically
END;
$$ LANGUAGE plpgsql;

-- Overloaded function that uses the calculated activity range as defaults
CREATE OR REPLACE FUNCTION get_mpp_data_for_pixel(
    p_solar_cell_id_in VARCHAR(255),
    p_pixel_in VARCHAR(255)
)
RETURNS TABLE (
    "timestamp" TIMESTAMP WITH TIME ZONE,
    current FLOAT,
    voltage FLOAT,
    power FLOAT,
    tracking_channel_board INTEGER,
    tracking_channel_channel INTEGER,
    connection_event_time TIMESTAMP WITH TIME ZONE
)
AS $$
DECLARE
    v_start_datetime TIMESTAMP WITH TIME ZONE;
    v_end_datetime TIMESTAMP WITH TIME ZONE;
BEGIN
    -- This overloaded version of get_mpp_data_for_pixel automatically determines
    -- the time range from the pixel's first connection to its last disconnection (or NOW()).

    -- Get the default activity range for the pixel using the helper function.
    SELECT ar.calculated_start_datetime, ar.calculated_end_datetime
    INTO v_start_datetime, v_end_datetime
    FROM get_pixel_activity_range(p_solar_cell_id_in, p_pixel_in) ar;

    -- If no activity range is found (e.g., pixel never connected, so start/end are NULL),
    -- return an empty result set.
    IF v_start_datetime IS NULL OR v_end_datetime IS NULL THEN
        RETURN; -- Exits the function, effectively returning an empty table.
    END IF;

    -- Call the original function (which requires explicit start and end times)
    -- with the dynamically determined date range.
    RETURN QUERY
    SELECT *
    FROM get_mpp_data_for_pixel(
        p_solar_cell_id_in,
        p_pixel_in,
        v_start_datetime,
        v_end_datetime
    );
END;
$$ LANGUAGE plpgsql;

