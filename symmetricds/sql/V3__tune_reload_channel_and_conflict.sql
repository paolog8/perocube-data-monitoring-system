-- Ignore duplicate-key conflicts during initial load.
-- The hub already has partial data from a previous reload attempt; without
-- this rule, SymmetricDS errors on INSERT when a row already exists there.
-- IGNORE is correct for immutable time-series rows: if the row is present
-- it was synced correctly and does not need to be re-applied.
INSERT INTO sym_conflict (
    conflict_id,
    source_node_group_id,
    target_node_group_id,
    target_channel_id,
    target_catalog_name,
    target_schema_name,
    target_table_name,
    detect_type,
    detect_expression,
    resolve_type,
    ping_back,
    resolve_changes_only,
    resolve_row_only,
    create_time,
    last_update_by,
    last_update_time
) VALUES (
    'ignore_duplicates_on_reload',
    'edge',
    'hub',
    NULL,          -- applies to all channels
    NULL,
    NULL,
    NULL,          -- applies to all tables
    'USE_PK_DATA',
    NULL,
    'IGNORE',
    '0',
    '0',
    '0',
    now(),
    'admin',
    now()
);
