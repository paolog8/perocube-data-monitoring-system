-- Scope the conflict rule to the reload channel only.
-- V4 incorrectly set target_channel_id to 'outdoor_monitoring';
-- conflicts only need to be ignored during initial load (reload channel).
UPDATE sym_conflict
SET target_channel_id = 'reload',
    last_update_time  = now(),
    last_update_by    = 'admin'
WHERE conflict_id = 'ignore_duplicates_on_reload';
