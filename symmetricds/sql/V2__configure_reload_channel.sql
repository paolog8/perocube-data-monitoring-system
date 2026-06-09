UPDATE sym_channel
SET max_batch_size   = 1000,
    max_batch_to_send = 10,
    last_update_time  = now(),
    last_update_by    = 'admin'
WHERE channel_id = 'reload';
