-- Reduce max_batch_size to avoid read timeouts during historical data sync.
-- 10,000-row batches take long enough to extract from TimescaleDB hypertables
-- that the nginx proxy times out before the push completes.
-- Compensate with more batches per push cycle (500 instead of 100) so
-- overall throughput stays high.
UPDATE sym_channel
SET
    max_batch_size    = 1000,
    max_batch_to_send = 1000,
    last_update_time  = now()
WHERE channel_id = 'outdoor_monitoring';
