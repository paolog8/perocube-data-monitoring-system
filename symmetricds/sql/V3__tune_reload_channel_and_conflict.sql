-- Ignore duplicate-key conflicts during initial load.
-- The hub already has partial data from a previous reload attempt; without
-- this rule, SymmetricDS errors on INSERT when a row already exists there.
-- IGNORE is correct for immutable time-series rows: if the row is present
-- it was synced correctly and does not need to be re-applied.
INSERT INTO sym_conflict (
    conflict_id,
    source_node_group_id,
    target_node_group_id,
    target_catalog_name,
    target_schema_name,
    target_table_name,
    detect_type,
    resolve_type,
    ping_back,
    use_row_data,
    create_time,
    last_update_time,
    last_update_by
) VALUES (
    'ignore_duplicates_on_reload',
    'edge',
    'hub',
    NULL,
    NULL,
    NULL,          -- applies to all tables
    'USE_PK_DATA',
    'IGNORE',
    '0',
    '0',
    now(),
    now(),
    'admin'
);
