-- Add edge→hub triggers for the solar_cell_type and mpp_polarity lookup tables.
--
-- These tables are seeded identically on edge and hub by the outdoor_monitoring
-- migrations (V29/V30), so their rows already match without replication. Adding
-- triggers ensures any FUTURE additions on the edge propagate to the hub, keeping
-- the SERIAL ids aligned so replicated solar_cell.cell_type_id / mpp_connection_event.polarity_id
-- FK values continue to resolve.
--
-- No initial load is required: the hub already holds identical rows, and the
-- ignore_duplicates_on_reload conflict rule (V3-V5) would ignore them anyway.

-- ------------------------------------------------------------
-- Triggers — one per lookup table
-- ------------------------------------------------------------
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
    ('trg_solar_cell_type', 'solar_cell_type', 'outdoor_monitoring', 1, 1, 1, 0, now(), now()),
    ('trg_mpp_polarity',    'mpp_polarity',    'outdoor_monitoring', 1, 1, 1, 0, now(), now());

-- ------------------------------------------------------------
-- Trigger routers — link each trigger to the edge_to_hub router
-- ------------------------------------------------------------
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
    ('trg_solar_cell_type', 'edge_to_hub', 1, 1, NULL, now(), now()),
    ('trg_mpp_polarity',    'edge_to_hub', 1, 1, NULL, now(), now());
