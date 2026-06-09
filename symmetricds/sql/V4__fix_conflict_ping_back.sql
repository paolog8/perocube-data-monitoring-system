-- Fix the conflict rule inserted in V3:
--   1. ping_back must be the enum string 'OFF', not '0'
--   2. Scope the rule to the outdoor_monitoring channel only so it does
--      not interfere with heartbeat and other internal SymmetricDS channels
UPDATE sym_conflict
SET ping_back         = 'OFF',
    target_channel_id = 'outdoor_monitoring',
    last_update_time  = now(),
    last_update_by    = 'admin'
WHERE conflict_id = 'ignore_duplicates_on_reload';
