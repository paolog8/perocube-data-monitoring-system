# Query Patterns

## Querying measurements for a solar cell

### What the function does

`mpp_measurements_for_cell` hides the complexity of the hardware schema. MPP data is stored per tracker slot, not per cell — and a cell can move between slots over time. The function automatically finds every interval when the named cell was connected, scopes the measurements to those intervals, and returns them in a single result set. You never need to know which slot a cell was on.

```sql
-- Every measurement ever taken for 'Cell_A'
SELECT * FROM mpp_measurements_for_cell('Cell_A');

-- Restrict to a time window
SELECT * FROM mpp_measurements_for_cell('Cell_A', '2024-06-01', '2024-07-01');
```

### Output columns

| Column | Type | Meaning |
|---|---|---|
| `measured_at` | `TIMESTAMPTZ` | Timestamp of the measurement (or bucket start when downsampling) |
| `mode_code` | `TEXT` | Connection mode: `'mpp_tracking'`, `'short_circuit'`, or `'open_circuit'` |
| `voltage` | `DOUBLE PRECISION` | Voltage in Volts |
| `current_a` | `DOUBLE PRECISION` | Current in Amps |
| `power_mw` | `DOUBLE PRECISION` | Power in milliWatts |

### Downsampling with `time_bucket`

Raw data can be collected at high frequency (e.g. every second). For plots or exports covering hours or days, returning every raw point is slow and more data than you need.

TimescaleDB provides `time_bucket(interval, timestamp)`, which works like rounding a timestamp down to the nearest fixed boundary:

```
time_bucket('1 hour',    '2024-06-15 14:37:22+00')  →  '2024-06-15 14:00:00+00'
time_bucket('5 minutes', '2024-06-15 14:37:22+00')  →  '2024-06-15 14:35:00+00'
```

All raw rows that land in the same bucket are grouped together and averaged. The function accepts an optional fourth argument `p_bucket_interval` that activates this mode:

```sql
-- One averaged row per minute
SELECT * FROM mpp_measurements_for_cell('Cell_A', '2024-06-01', '2024-06-02', '1 minute');

-- One averaged row per hour
SELECT * FROM mpp_measurements_for_cell('Cell_A', '2024-06-01', '2024-07-01', '1 hour');

-- One averaged row per day
SELECT * FROM mpp_measurements_for_cell('Cell_A', '2024-01-01', '2025-01-01', '1 day');

-- 10-second buckets, no time window restriction
SELECT * FROM mpp_measurements_for_cell('Cell_A', p_bucket_interval => '10 seconds');
```

The last example uses a **named argument** (`p_bucket_interval => ...`) to skip the `p_start`/`p_end` positional arguments without having to supply them explicitly.

In bucketed mode:
- `measured_at` is the **start** of the bucket window, not the exact time of any individual measurement.
- `voltage`, `current_a`, `power_mw` are the **averages** of all raw values that fell in that window.
- `mode_code` is the **most frequent** mode in the window (almost always a single mode, but edge cases around reconnection events are handled gracefully).

### Choosing a bucket width

- Match the bucket width to your display resolution. A 24-hour plot with one point per pixel needs at most ~1000 buckets — `'1 minute'` or `'5 minutes'` is usually enough.
- Do not go smaller than your data collection interval. If data is recorded every 5 seconds, a `'1 second'` bucket would return the same data as raw with added overhead.
- Typical choices: `'10 seconds'` for real-time monitoring, `'1 minute'` for hourly views, `'1 hour'` for multi-day overviews, `'1 day'` for long-term trends.
