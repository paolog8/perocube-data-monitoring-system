-- Tables without time-series characteristics (PostgreSQL)

CREATE TABLE scientist (
    scientist_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    -- Add other scientist attributes here if needed
    UNIQUE (name) -- Consider adding this to ensure name uniqueness if required
);

CREATE TABLE experiment (
    experiment_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    start_date DATE,
    end_date DATE,
    -- Add other experiment attributes here if needed
    UNIQUE (name)    
);

CREATE TABLE project (
    project_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    -- Add other project attributes here if needed
    UNIQUE (name)
);

CREATE TABLE solar_cell_device (
    nomad_id UUID PRIMARY KEY,
    technology VARCHAR(255),
    form_factor VARCHAR(255),
    experiment_id UUID,
    owner_id UUID,
    producer_id UUID,
    date_produced DATE,
    date_encapsulated DATE,
    encapsulation VARCHAR(255),
    area FLOAT,
    initial_pce FLOAT,
    FOREIGN KEY (owner_id) REFERENCES scientist(scientist_id),
    FOREIGN KEY (producer_id) REFERENCES scientist(scientist_id),
    FOREIGN KEY (experiment_id) REFERENCES experiment(experiment_id)
);

CREATE TABLE solar_cell_pixel (
    solar_cell_id UUID,
    pixel VARCHAR(255),
    active_area FLOAT,
    PRIMARY KEY (solar_cell_id, pixel),
    FOREIGN KEY (solar_cell_id) REFERENCES solar_cell_device(nomad_id)
);

CREATE TABLE mpp_tracking_channel (
    board INTEGER,
    channel INTEGER,
    address VARCHAR(255),
    com_port VARCHAR(255),
    current_limit FLOAT,
    PRIMARY KEY (board, channel)
);

CREATE TABLE temperature_sensor (
    temperature_sensor_id UUID PRIMARY KEY,
    date_installed DATE,
    location VARCHAR(255),
    sensor_identifier VARCHAR(255),
    UNIQUE (sensor_identifier)
);

CREATE TABLE irradiance_sensor (
    irradiance_sensor_id UUID PRIMARY KEY,
    date_installed DATE,
    location VARCHAR(255),
    installation_angle INTEGER,
    sensor_identifier VARCHAR(255),
    channel INTEGER,
    UNIQUE (sensor_identifier, channel)
);

CREATE TABLE measurement_connection_event (
    solar_cell_id UUID,
    pixel VARCHAR(255),
    tracking_channel_board INTEGER,
    tracking_channel_channel INTEGER,
    temperature_sensor_id UUID,
    irradiance_sensor_id UUID,
    mppt_mode VARCHAR(255),
    mppt_polarity VARCHAR(255),
    connection_datetime TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (solar_cell_id, pixel, connection_datetime),
    FOREIGN KEY (solar_cell_id, pixel) REFERENCES solar_cell_pixel(solar_cell_id, pixel),
    FOREIGN KEY (tracking_channel_board, tracking_channel_channel) REFERENCES mpp_tracking_channel(board, channel),
    FOREIGN KEY (temperature_sensor_id) REFERENCES temperature_sensor(temperature_sensor_id),
    FOREIGN KEY (irradiance_sensor_id) REFERENCES irradiance_sensor(irradiance_sensor_id)
);

CREATE TABLE scientist_performed_experiment (
    scientist_id UUID,
    experiment_id UUID,
    PRIMARY KEY (scientist_id, experiment_id),
    FOREIGN KEY (scientist_id) REFERENCES scientist(scientist_id),
    FOREIGN KEY (experiment_id) REFERENCES experiment(experiment_id)
);

CREATE TABLE experiment_contributed_project (
    experiment_id UUID,
    project_id UUID,
    PRIMARY KEY (experiment_id, project_id),
    FOREIGN KEY (experiment_id) REFERENCES experiment(experiment_id),
    FOREIGN KEY (project_id) REFERENCES project(project_id)
);

CREATE TABLE scientist_member_project (
    scientist_id UUID,
    project_id UUID,
    PRIMARY KEY (scientist_id, project_id),
    FOREIGN KEY (scientist_id) REFERENCES scientist(scientist_id),
    FOREIGN KEY (project_id) REFERENCES project(project_id)
);

-- Tables with time-series characteristics (TimescaleDB)

CREATE TABLE mpp_measurement (
    "timestamp" TIMESTAMP WITH TIME ZONE NOT NULL,
    current FLOAT,
    voltage FLOAT,
    power FLOAT,
    tracking_channel_board INTEGER NOT NULL,
    tracking_channel_channel INTEGER NOT NULL,
    FOREIGN KEY (tracking_channel_board, tracking_channel_channel) REFERENCES mpp_tracking_channel(board, channel)
);

SELECT create_hypertable('mpp_measurement', 'timestamp');

CREATE TABLE temperature_measurement (
    "timestamp" TIMESTAMP WITH TIME ZONE NOT NULL,
    temperature FLOAT,
    temperature_sensor_id UUID NOT NULL,
    FOREIGN KEY (temperature_sensor_id) REFERENCES temperature_sensor(temperature_sensor_id)
);

SELECT create_hypertable('temperature_measurement', 'timestamp');

CREATE TABLE irradiance_measurement (
    "timestamp" TIMESTAMP WITH TIME ZONE NOT NULL,
    raw_reading INTEGER,
    irradiance FLOAT,
    irradiance_sensor_id UUID NOT NULL,
    FOREIGN KEY (irradiance_sensor_id) REFERENCES irradiance_sensor(irradiance_sensor_id)
);

SELECT create_hypertable('irradiance_measurement', 'timestamp');