-- V4__data_health_views.sql
-- Contains views and functions for data health monitoring dashboards.

-- View: data_health_last_seen
-- Calculates the last seen timestamp for each type of sensor.
CREATE OR REPLACE VIEW data_health_last_seen AS
WITH mpp_last_seen AS (
    SELECT
        'mpp_channel' AS sensor_type,
        'board_' || m.tracking_channel_board || '_channel_' || m.tracking_channel_channel AS sensor_id,
        MAX(m."timestamp") AS last_seen_timestamp
    FROM
        mpp_measurement m
    GROUP BY
        m.tracking_channel_board,
        m.tracking_channel_channel
),
temperature_last_seen AS (
    SELECT
        'temperature_sensor' AS sensor_type,
        temperature_sensor_id::TEXT AS sensor_id,
        MAX(tm."timestamp") AS last_seen_timestamp
    FROM
        temperature_measurement tm
    GROUP BY
        tm.temperature_sensor_id
),
irradiance_last_seen AS (
    SELECT
        'irradiance_sensor' AS sensor_type,
        irradiance_sensor_id::TEXT AS sensor_id,
        MAX(im."timestamp") AS last_seen_timestamp
    FROM
        irradiance_measurement im
    GROUP BY
        im.irradiance_sensor_id
)
SELECT * FROM mpp_last_seen
UNION ALL
SELECT * FROM temperature_last_seen
UNION ALL
SELECT * FROM irradiance_last_seen
ORDER BY sensor_type, sensor_id;

-- View: data_health_daily_measurements
-- Counts daily measurements per sensor type.
CREATE OR REPLACE VIEW data_health_daily_measurements AS
WITH mpp_daily AS (
    SELECT
        'mpp_channel' AS sensor_type,
        'board_' || m.tracking_channel_board || '_channel_' || m.tracking_channel_channel AS sensor_id,
        time_bucket('1 day', m."timestamp") AS day,
        COUNT(*) AS measurement_count
    FROM
        mpp_measurement m
    GROUP BY
        m.tracking_channel_board,
        m.tracking_channel_channel,
        day
),
temperature_daily AS (
    SELECT
        'temperature_sensor' AS sensor_type,
        temperature_sensor_id::TEXT AS sensor_id,
        time_bucket('1 day', tm."timestamp") AS day,
        COUNT(*) AS measurement_count
    FROM
        temperature_measurement tm
    GROUP BY
        tm.temperature_sensor_id,
        day
),
irradiance_daily AS (
    SELECT
        'irradiance_sensor' AS sensor_type,
        irradiance_sensor_id::TEXT AS sensor_id,
        time_bucket('1 day', im."timestamp") AS day,
        COUNT(*) AS measurement_count
    FROM
        irradiance_measurement im
    GROUP BY
        im.irradiance_sensor_id,
        day
)
SELECT * FROM mpp_daily
UNION ALL
SELECT * FROM temperature_daily
UNION ALL
SELECT * FROM irradiance_daily
ORDER BY sensor_type, sensor_id, day;

-- View: data_health_weekly_measurements
-- Counts weekly measurements per sensor type.
CREATE OR REPLACE VIEW data_health_weekly_measurements AS
WITH mpp_weekly AS (
    SELECT
        'mpp_channel' AS sensor_type,
        'board_' || m.tracking_channel_board || '_channel_' || m.tracking_channel_channel AS sensor_id,
        time_bucket('1 week', m."timestamp") AS week,
        COUNT(*) AS measurement_count
    FROM
        mpp_measurement m
    GROUP BY
        m.tracking_channel_board,
        m.tracking_channel_channel,
        week
),
temperature_weekly AS (
    SELECT
        'temperature_sensor' AS sensor_type,
        temperature_sensor_id::TEXT AS sensor_id,
        time_bucket('1 week', tm."timestamp") AS week,
        COUNT(*) AS measurement_count
    FROM
        temperature_measurement tm
    GROUP BY
        tm.temperature_sensor_id,
        week
),
irradiance_weekly AS (
    SELECT
        'irradiance_sensor' AS sensor_type,
        irradiance_sensor_id::TEXT AS sensor_id,
        time_bucket('1 week', im."timestamp") AS week,
        COUNT(*) AS measurement_count
    FROM
        irradiance_measurement im
    GROUP BY
        im.irradiance_sensor_id,
        week
)
SELECT * FROM mpp_weekly
UNION ALL
SELECT * FROM temperature_weekly
UNION ALL
SELECT * FROM irradiance_weekly
ORDER BY sensor_type, sensor_id, week;

-- Function: get_data_gaps
-- Identifies data gaps longer than a specified threshold for all sensor types.
CREATE OR REPLACE FUNCTION get_data_gaps(
    p_gap_threshold INTERVAL DEFAULT '5 minutes'
)
RETURNS TABLE (
    sensor_type TEXT,
    sensor_id TEXT,
    gap_start TIMESTAMP WITH TIME ZONE,
    gap_end TIMESTAMP WITH TIME ZONE,
    gap_duration INTERVAL
)
AS $$
BEGIN
    RETURN QUERY
    WITH all_measurements AS (
        SELECT
            'mpp_channel' AS sensor_type,
            'board_' || m.tracking_channel_board || '_channel_' || m.tracking_channel_channel AS sensor_id,
            m."timestamp" AS measurement_timestamp
        FROM
            mpp_measurement m
        UNION ALL
        SELECT
            'temperature_sensor' AS sensor_type,
            temperature_sensor_id::TEXT AS sensor_id,
            tm."timestamp" AS measurement_timestamp
        FROM
            temperature_measurement tm
        UNION ALL
        SELECT
            'irradiance_sensor' AS sensor_type,
            irradiance_sensor_id::TEXT AS sensor_id,
            im."timestamp" AS measurement_timestamp
        FROM
            irradiance_measurement im
    ),
    lagged_measurements AS (
        SELECT
            sensor_type,
            sensor_id,
            measurement_timestamp,
            LAG(measurement_timestamp, 1, measurement_timestamp) OVER (PARTITION BY sensor_type, sensor_id ORDER BY measurement_timestamp) AS prev_measurement_timestamp
        FROM
            all_measurements
    )
    SELECT
        lm.sensor_type,
        lm.sensor_id,
        lm.prev_measurement_timestamp AS gap_start,
        lm.measurement_timestamp AS gap_end,
        (lm.measurement_timestamp - lm.prev_measurement_timestamp) AS gap_duration
    FROM
        lagged_measurements lm
    WHERE
        (lm.measurement_timestamp - lm.prev_measurement_timestamp) > p_gap_threshold
    ORDER BY
        lm.sensor_type,
        lm.sensor_id,
        gap_start;
END;
$$ LANGUAGE plpgsql;