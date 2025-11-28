------------------------------------------------------------------------------
-- Channels
------------------------------------------------------------------------------
INSERT INTO sym_channel 
(channel_id, processing_order, max_batch_size, enabled, description) 
VALUES('default', 1, 100000, 1, 'Default channel')
ON CONFLICT (channel_id) DO NOTHING;

------------------------------------------------------------------------------
-- Node Groups
------------------------------------------------------------------------------
INSERT INTO sym_node_group (node_group_id, description) 
VALUES ('cloud', 'Cloud Node')
ON CONFLICT (node_group_id) DO NOTHING;

INSERT INTO sym_node_group (node_group_id, description) 
VALUES ('edge', 'Edge Node')
ON CONFLICT (node_group_id) DO NOTHING;

------------------------------------------------------------------------------
-- Node Group Links
------------------------------------------------------------------------------
-- Edge pushes to Cloud
INSERT INTO sym_node_group_link (source_node_group_id, target_node_group_id, data_event_action) 
VALUES ('edge', 'cloud', 'P')
ON CONFLICT (source_node_group_id, target_node_group_id) DO NOTHING;

-- Cloud waits for pull
INSERT INTO sym_node_group_link (source_node_group_id, target_node_group_id, data_event_action) 
VALUES ('cloud', 'edge', 'W')
ON CONFLICT (source_node_group_id, target_node_group_id) DO NOTHING;

------------------------------------------------------------------------------
-- Routers
------------------------------------------------------------------------------
INSERT INTO sym_router 
(router_id, source_node_group_id, target_node_group_id, router_type, create_time, last_update_time) 
VALUES('edge_2_cloud', 'edge', 'cloud', 'default', current_timestamp, current_timestamp)
ON CONFLICT (router_id) DO NOTHING;

------------------------------------------------------------------------------
-- Triggers
------------------------------------------------------------------------------
-- Sync all tables
INSERT INTO sym_trigger 
(trigger_id, source_table_name, channel_id, last_update_time, create_time) 
VALUES('all_tables', '*', 'default', current_timestamp, current_timestamp)
ON CONFLICT (trigger_id) DO NOTHING;

------------------------------------------------------------------------------
-- Trigger Routers
------------------------------------------------------------------------------
INSERT INTO sym_trigger_router 
(trigger_id, router_id, initial_load_order, last_update_time, create_time) 
VALUES('all_tables', 'edge_2_cloud', 100, current_timestamp, current_timestamp)

