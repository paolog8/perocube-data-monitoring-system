-- Add PT device information to irradiance_sensor table
ALTER TABLE irradiance_sensor 
ADD COLUMN pt_device INTEGER,
ADD COLUMN pt_channel INTEGER,
ADD CONSTRAINT unique_pt_device_channel UNIQUE (pt_device, pt_channel);

-- Function to generate deterministic UUID from pt_device and pt_channel
CREATE OR REPLACE FUNCTION generate_irradiance_sensor_id(pt_device INTEGER, pt_channel INTEGER)
RETURNS UUID AS $$
BEGIN
    -- Generate a deterministic UUID using v5 (SHA1)
    -- We use a fixed namespace UUID (version 4) for consistency
    RETURN uuid_generate_v5(
        'f47ac10b-58cc-4372-a567-0e02b2c3d479'::UUID, 
        format('PT-%s_channel_%s', pt_device, pt_channel)
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Helper function to get or create irradiance sensor
CREATE OR REPLACE FUNCTION get_or_create_irradiance_sensor(
    p_pt_device INTEGER,
    p_pt_channel INTEGER,
    p_location VARCHAR DEFAULT NULL,
    p_installation_angle INTEGER DEFAULT NULL
) 
RETURNS UUID AS $$
DECLARE
    v_sensor_id UUID;
BEGIN
    -- Try to find existing sensor
    SELECT irradiance_sensor_id 
    INTO v_sensor_id
    FROM irradiance_sensor
    WHERE pt_device = p_pt_device AND pt_channel = p_pt_channel;
    
    -- If not found, create new sensor
    IF v_sensor_id IS NULL THEN
        v_sensor_id := generate_irradiance_sensor_id(p_pt_device, p_pt_channel);
        
        INSERT INTO irradiance_sensor (
            irradiance_sensor_id,
            pt_device,
            pt_channel,
            date_installed,
            location,
            installation_angle
        ) VALUES (
            v_sensor_id,
            p_pt_device,
            p_pt_channel,
            CURRENT_DATE,
            p_location,
            p_installation_angle
        );
    END IF;
    
    RETURN v_sensor_id;
END;
$$ LANGUAGE plpgsql;
