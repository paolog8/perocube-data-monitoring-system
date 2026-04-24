-- sym_node and sym_node_identity are all pre-populated by SymmetricDS when it first starts up and connects to the database. 

-- ------------------------------------------------------------
-- Channel
-- ------------------------------------------------------------


INSERT INTO sym_channel (
    channel_id,
    processing_order,
    max_batch_size,
    max_batch_to_send,
    extract_period_millis,
    batch_algorithm,
    use_old_data_to_route,
    use_row_data_to_route,
    use_pk_data_to_route,
    enabled,
    description,
    create_time,
    last_update_time
)
VALUES (
    'outdoor_monitoring',
    3,
    1000,
    10,
    0,
    'default',
    0,
    1,
    1,
    1,
    'All outdoor_monitoring tables',
    now(),
    now()
);

-- -- Group: edge

INSERT INTO sym_node_group (
    node_group_id,
    create_time,
    last_update_time   
)
VALUES (
    'edge',
    now(),
    now()
);

-- Group Link
INSERT INTO sym_node_group_link (
    source_node_group_id,
    target_node_group_id,
    data_event_action,
    sync_config_enabled,
    create_time,
    last_update_time
)
VALUES
    ('hub', 'edge', 'W', 1, now(), now()),
    ('edge', 'hub', 'P', 1, now(), now());

-- -- ------------------------------------------------------------
-- -- Router: edge → hub
-- -- ------------------------------------------------------------
INSERT INTO sym_router (
    router_id,
    target_catalog_name,
    target_schema_name,
    source_node_group_id,
    target_node_group_id,
    router_type,
    sync_on_update,
    sync_on_insert,
    sync_on_delete,
    create_time,
    last_update_time
)
VALUES (
    'edge_to_hub',
    'outdoor_monitoring',
    'public',
    'edge',
    'hub',
    'default',
    1,
    1,
    1,
    now(),
    now()
);

-- -- ------------------------------------------------------------
-- -- Triggers — one per table
-- -- ------------------------------------------------------------
INSERT INTO sym_trigger (
    trigger_id,
    source_table_name,
    channel_id,
    sync_on_update,
    sync_on_insert,
    sync_on_delete,
    sync_on_incoming_batch,
    create_time,
    last_update_time
)
VALUES
    ('trg_mpp_tracker',              'mpp_tracker',              'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_mpp_tracking_slot',        'mpp_tracking_slot',        'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_mpp_connection_mode',      'mpp_connection_mode',      'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_sensor',                   'sensor',                   'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_temperature_sensor',       'temperature_sensor',       'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_irradiance_sensor',        'irradiance_sensor',        'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_spectral_sensor',          'spectral_sensor',          'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_mpp_measurement',          'mpp_measurement',          'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_temperature_measurement',  'temperature_measurement',  'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_irradiance_measurement',   'irradiance_measurement',   'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_spectral_measurement',     'spectral_measurement',     'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_mpp_connection_event',     'mpp_connection_event',     'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_sensor_association_event', 'sensor_association_event', 'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_solar_cell',               'solar_cell',               'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_solar_cell_group',         'solar_cell_group',         'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_solar_cell_group_type',    'solar_cell_group_type',    'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_scientist',                'scientist',                'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_project',                  'project',                  'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_experiment',               'experiment',               'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_experiment_project',       'experiment_project',       'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_solar_cell_experiment',    'solar_cell_experiment',    'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_ingestion_log',            'ingestion_log',            'outdoor_monitoring', 1, 1, 1, 0, now(), now());

-- -- ------------------------------------------------------------
-- -- Trigger routers — link each trigger to edge_to_hub router
-- -- ------------------------------------------------------------
INSERT INTO sym_trigger_router (
    trigger_id,
    router_id,
    enabled,
    initial_load_order,
    initial_load_select,
    create_time,
    last_update_time
)
VALUES
    ('trg_mpp_tracker',              'edge_to_hub', 1, 1,  NULL, now(), now()),
    ('trg_mpp_tracking_slot',        'edge_to_hub', 1, 1,  NULL, now(), now()),
    ('trg_mpp_connection_mode',      'edge_to_hub', 1, 1,  NULL, now(), now()),
    ('trg_sensor',                   'edge_to_hub', 1, 1,  NULL, now(), now()),
    ('trg_temperature_sensor',       'edge_to_hub', 1, 1,  NULL, now(), now()),
    ('trg_irradiance_sensor',        'edge_to_hub', 1, 1,  NULL, now(), now()),
    ('trg_spectral_sensor',          'edge_to_hub', 1, 1,  NULL, now(), now()),
    ('trg_scientist',                'edge_to_hub', 1, 1,  NULL, now(), now()),
    ('trg_project',                  'edge_to_hub', 1, 1,  NULL, now(), now()),
    ('trg_experiment',               'edge_to_hub', 1, 1, NULL, now(), now()),
    ('trg_experiment_project',       'edge_to_hub', 1, 1, NULL, now(), now()),
    ('trg_solar_cell_group_type',    'edge_to_hub', 1, 1, NULL, now(), now()),
    ('trg_solar_cell_group',         'edge_to_hub', 1, 1, NULL, now(), now()),
    ('trg_solar_cell',               'edge_to_hub', 1, 1, NULL, now(), now()),
    ('trg_solar_cell_experiment',    'edge_to_hub', 1, 1, NULL, now(), now()),
    ('trg_mpp_connection_event',     'edge_to_hub', 1, 1, NULL, now(), now()),
    ('trg_sensor_association_event', 'edge_to_hub', 1, 1, NULL, now(), now()),
    ('trg_ingestion_log',            'edge_to_hub', 1, 1, NULL, now(), now()),
    ('trg_mpp_measurement',          'edge_to_hub', 1, 1, NULL, now(), now()),
    ('trg_temperature_measurement',  'edge_to_hub', 1, 1, NULL, now(), now()),
    ('trg_irradiance_measurement',   'edge_to_hub', 1, 1, NULL, now(), now()),
    ('trg_spectral_measurement',     'edge_to_hub', 1, 1, NULL, now(), now());
