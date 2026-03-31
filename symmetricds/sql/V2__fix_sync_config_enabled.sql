-- Enable config sync from hub to edge so the edge receives topology
-- configuration (triggers, routers, channels) after registration.
-- Without this, the edge never installs DB triggers and generates no batches.

INSERT INTO sym_node_group_link (
    source_node_group_id,
    target_node_group_id,
    data_event_action,
    sync_config_enabled
)
VALUES ('edge', 'hub', 'P', 1)
ON CONFLICT (source_node_group_id, target_node_group_id)
DO UPDATE SET sync_config_enabled = 1;