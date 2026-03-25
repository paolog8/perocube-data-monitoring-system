-- SymmetricDS topology configuration for one-way sync:
-- outdoor-data-monitoring (edge) → perocube server (hub)
--
-- Applied to the outdoor_monitoring database via flyway-sym-config service,
-- using a separate Flyway history table (flyway_schema_history_sym).

-- ------------------------------------------------------------
-- Node groups
-- ------------------------------------------------------------
INSERT INTO sym_node_group (node_group_id, description)
VALUES
    ('edge', 'Outdoor measuring PC — source of all data'),
    ('hub',  'Remote server — receives and stores data');

-- ------------------------------------------------------------
-- Node group link: edge pushes to hub (one-way)
-- sync_config_enabled=0 means hub does not push its sym config
-- back to the edge.
-- ------------------------------------------------------------
INSERT INTO sym_node_group_link (
    source_node_group_id,
    target_node_group_id,
    data_event_action,
    sync_config_enabled
)
VALUES ('edge', 'hub', 'W', 0);

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
    use_old_data_enabled,
    use_row_data_enabled,
    use_pk_data_enabled,
    enabled,
    description
)
VALUES (
    'outdoor_monitoring',
    1,
    10000,
    10,
    0,
    'default',
    0,
    1,
    1,
    1,
    'All outdoor_monitoring tables'
);

-- ------------------------------------------------------------
-- Router: edge → hub
-- ------------------------------------------------------------
INSERT INTO sym_router (
    router_id,
    source_node_group_id,
    target_node_group_id,
    router_type,
    sync_on_update,
    sync_on_insert,
    sync_on_delete
)
VALUES (
    'edge_to_hub',
    'edge',
    'hub',
    'default',
    1,
    1,
    1
);

-- ------------------------------------------------------------
-- Triggers — one per user table
-- ------------------------------------------------------------
INSERT INTO sym_trigger (
    trigger_id,
    source_table_name,
    channel_id,
    sync_on_update,
    sync_on_insert,
    sync_on_delete,
    sync_on_incoming_batch
)
VALUES
    ('trg_mpp_tracker',              'mpp_tracker',              'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_mpp_tracking_slot',        'mpp_tracking_slot',        'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_mpp_connection_mode',      'mpp_connection_mode',      'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_sensor',                   'sensor',                   'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_temperature_sensor',       'temperature_sensor',       'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_irradiance_sensor',        'irradiance_sensor',        'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_spectral_sensor',          'spectral_sensor',          'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_mpp_measurement',          'mpp_measurement',          'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_temperature_measurement',  'temperature_measurement',  'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_irradiance_measurement',   'irradiance_measurement',   'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_spectral_measurement',     'spectral_measurement',     'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_mpp_connection_event',     'mpp_connection_event',     'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_sensor_association_event', 'sensor_association_event', 'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_solar_cell',               'solar_cell',               'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_solar_cell_group',         'solar_cell_group',         'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_solar_cell_group_type',    'solar_cell_group_type',    'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_scientist',                'scientist',                'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_project',                  'project',                  'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_experiment',               'experiment',               'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_experiment_project',       'experiment_project',       'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_solar_cell_experiment',    'solar_cell_experiment',    'outdoor_monitoring', 1, 1, 1, 0),
    ('trg_ingestion_log',            'ingestion_log',            'outdoor_monitoring', 1, 1, 1, 0);

-- ------------------------------------------------------------
-- Trigger routers — link each trigger to edge_to_hub router
-- ------------------------------------------------------------
INSERT INTO sym_trigger_router (
    trigger_id,
    router_id,
    enabled,
    initial_load_order,
    initial_load_select
)
VALUES
    ('trg_mpp_tracker',              'edge_to_hub', 1, 1,  NULL),
    ('trg_mpp_tracking_slot',        'edge_to_hub', 1, 2,  NULL),
    ('trg_mpp_connection_mode',      'edge_to_hub', 1, 3,  NULL),
    ('trg_sensor',                   'edge_to_hub', 1, 4,  NULL),
    ('trg_temperature_sensor',       'edge_to_hub', 1, 5,  NULL),
    ('trg_irradiance_sensor',        'edge_to_hub', 1, 6,  NULL),
    ('trg_spectral_sensor',          'edge_to_hub', 1, 7,  NULL),
    ('trg_scientist',                'edge_to_hub', 1, 8,  NULL),
    ('trg_project',                  'edge_to_hub', 1, 9,  NULL),
    ('trg_experiment',               'edge_to_hub', 1, 10, NULL),
    ('trg_experiment_project',       'edge_to_hub', 1, 11, NULL),
    ('trg_solar_cell_group_type',    'edge_to_hub', 1, 12, NULL),
    ('trg_solar_cell_group',         'edge_to_hub', 1, 13, NULL),
    ('trg_solar_cell',               'edge_to_hub', 1, 14, NULL),
    ('trg_solar_cell_experiment',    'edge_to_hub', 1, 15, NULL),
    ('trg_mpp_connection_event',     'edge_to_hub', 1, 16, NULL),
    ('trg_sensor_association_event', 'edge_to_hub', 1, 17, NULL),
    ('trg_ingestion_log',            'edge_to_hub', 1, 18, NULL),
    ('trg_mpp_measurement',          'edge_to_hub', 1, 19, NULL),
    ('trg_temperature_measurement',  'edge_to_hub', 1, 20, NULL),
    ('trg_irradiance_measurement',   'edge_to_hub', 1, 21, NULL),
    ('trg_spectral_measurement',     'edge_to_hub', 1, 22, NULL);
