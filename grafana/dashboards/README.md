# Grafana Dashboards — Outdoor PV Monitoring

Version-tracked dashboards for the outdoor solar cell monitoring data. All dashboards
query the **`outdoor_monitoring`** database (datasource UID `ffk21zlrlrqioe`, see
`../provisioning/datasources/outdoor-monitoring.yml`). The legacy `perocube` database is
out of scope for dashboards.

Dashboards are provisioned from this directory via
`../provisioning/dashboards/dashboards.yml` (file provider, 30 s reload, UI edits
allowed). To change a dashboard permanently, edit the JSON here and commit — UI-only
edits are overwritten on the next provisioning cycle unless exported back into this
directory.

---

## Dashboard inventory

| Dashboard | UID | Audience / question it answers |
|---|---|---|
| [System Overview](#system-overview) | `outdoor-system-overview` | "Is the system healthy right now? What is connected and producing?" |
| [Single Cell Deep-Dive](#single-cell-deep-dive) | — | "How is *this* cell performing?" |
| [Multi-Cell Comparison](#multi-cell-comparison) | — | "Which of these cells performs best, area-normalized?" |
| [Degradation Tracking](#degradation-tracking) | — | "How fast are my cells degrading? When do they hit T80?" |
| Environmental Conditions | `outdoor-environmental-conditions` | "What were the conditions? Per-sensor irradiance, cell temperature, daily insolation" |
| Connection History & Coverage | `outdoor-connection-history` | "When was this cell mounted where, and which periods have data?" |

---

## System Overview

Default range: last 24 h, 30 s auto-refresh. All connection-state panels respect
`$__timeTo()`, so navigating to a historical time range shows the system state *as of
that time*.

| Panel | Notes |
|---|---|
| Active Cells (stat) | Count of slots whose latest connection event is `connection` |
| Data Freshness (stat) | Age of the newest MPP / irradiance / temperature row. Yellow ≥ 48 h, red ≥ 14 d — tuned to the bulk-export cadence (data arrives in periodic exports, not streaming; hours-to-days of age is normal). If one stream lags the others, that pipeline stage is stalled. |
| Irradiance / Cell Temperature (stats) | Latest 5-min average with 24 h sparkline. Temperature filters the `-999` sensor-error sentinel. Temperature is **cell temperature**, not ambient. |
| Power per Cell (timeseries) | Per-cell power, 5-min buckets. Measurements attributed to cells via connection intervals (`LEAD` over `mpp_connection_event`, same pattern as `mpp_measurements_for_cell`). A missing/flat trace shows immediately which cell stopped producing. |
| Irradiance & Cell Temperature (timeseries) | Dual axis: W/m² left, °C right. Stacked directly below Power per Cell (both full-width, same time axis) so production can be compared against irradiance at a glance. The `Cell Temperature` variable toggles the temperature series on/off (`Show`/`Hide`) when only irradiance vs. power matters. |
| Active Connections (table) | One row per connected slot: tracker, slot, cell, mode, polarity, connected-since, duration, latest P/V/I |
| Ingestion Runs (table) | Recent `ingestion_log` rows replicated from the measurement PC — edge ingestion failures are visible on the hub |

> The earlier "Total Power Output" / "Total Power Over Time" panels were removed after
> scientist feedback: summing power across heterogeneous test cells (different areas,
> technologies, connection modes) has no scientific meaning.

**`Cell Temperature` toggle (System Overview):** a `custom` template variable
(`show_temperature`, values `show`/`hide`) gates the temperature target's `WHERE`
clause with `AND '$show_temperature' = 'show'`. When set to `hide`, the query returns
zero rows, so the series and its right-hand axis simply don't render — no panel
duplication needed.

## Single Cell Deep-Dive

Variables: `cell` (single-select, `SELECT name FROM solar_cell ORDER BY name`),
`min_irr` (textbox, default 50 — irradiance floor in W/m² for PCE validity).

Panels: Cell Details table (type, structure, area, initial PCE, manufacturer/owner,
PVcomB ID, NOMAD link), KPI stats (peak/avg power, peak/avg PCE), Power Over Time,
dual-axis Voltage & Current, PCE over time, and Daily Energy Yield (mWh/cm²/day,
`mpp_tracking` periods only, hourly server-side buckets summed per day).

**Connection-event annotations:** connect/disconnect events for the selected cell are
drawn as vertical markers (also on Degradation Tracking, for all selected cells), so
steps in power/PCE curves can be attributed to physical interventions.

Data access goes through `mpp_measurements_for_cell(cell, from, to, bucket)` — see
[Performance rules](#performance-rules). The function returns
`measured_at, mode_code, voltage, current_a, power_mw`.

## Multi-Cell Comparison

Variables: `experiment` (single-select with an `(all experiments)` sentinel; filters
the cell list via `solar_cell_experiment` so a whole experiment can be selected in one
click), `cell` (multi-select, includeAll, defaults to a "none" sentinel — see
[Multi-select default](#multi-select-cell-variable-default)), `min_irr` (textbox,
default 50).

Panels: PCE per cell, Power per cell, Average PCE Ranking (bargauge), Comparison &
Coverage table (avg/peak PCE, avg power, first/last measurement, days of data — derived
from the same function pass, **not** from `mpp_data_coverage`, see performance rules).

PCE — not raw power — is the fair comparison metric because it is area-normalized.

## Degradation Tracking

Variables: `cell` (multi-select, defaults to none), `min_irr` (default 50),
`baseline_hours` (default 24 — length of the reference window), `degradation_threshold`
(default 80 — i.e. T80). Default time range starts 2020-01-01 so the full lifetime is
visible.

- **Normalized PCE**: each cell normalized to 100 % = its own average PCE during
  `[first_connection, first_connection + baseline_hours)`. The baseline is computed from
  `mpp_connection_history()` + a fixed-window function call, *independent of the
  dashboard time range*, so zooming in does not lose the baseline.
- **Irradiance & Cell Temperature**: fleet-wide context panel — check whether an apparent
  PCE drop is just a weather period.
- **Degradation Summary** table: baseline window, baseline PCE, latest normalized
  performance, linear degradation rate (%/year via `regr_slope`), and an extrapolated
  T`$degradation_threshold` date (blank if the slope is non-negative).

---

## The PCE formula

```
PCE (%) = 1000 * power_mw / (irradiance_W_m2 * area_cm2)
```

Derivation: P_out[W] = power_mw · 10⁻³; P_in[W] = irradiance[W/m²] · area_cm2 · 10⁻⁴.

Validity constraints applied everywhere PCE is shown:

1. **`mode_code = 'mpp_tracking'` only** — power in open/short-circuit modes is not
   P_max, so PCE would be meaningless.
2. **`irradiance > $min_irr`** (default 50 W/m²) — avoids divide-by-near-zero noise at
   dawn/dusk/night.
3. Uses the **global** irradiance sensor (the schema has no per-cell irradiance
   association) and the cell's registered `area_cm2`.
4. Assumes `mpp_measurement.power` is in **milliwatts**.

PCE panels bucket power and irradiance separately with the same `time_bucket` and join
on the bucket timestamp.

---

## Performance rules

These exist because they were each learned the slow way. Follow them in any new panel.

1. **Always pass the 4th (bucket) argument to `mpp_measurements_for_cell`**, as
   `INTERVAL '1 millisecond' * $__interval_ms`, so downsampling happens server-side and
   adapts to the zoom level. Since V34 (hub numbering) dropped the inlinable 3-arg SQL
   overload, a bare 3-arg call resolves to the plpgsql 4-arg function with
   `bucket = NULL`, whose raw path **materializes every measurement row** — very slow on
   wide ranges.
2. **Never use a fixed `time_bucket('5 minutes', …)` over a wide/variable range** in
   per-cell panels; use the adaptive `$__interval_ms` bucket so joins stay small.
   (System Overview keeps fixed 5-min buckets deliberately: plain hypertable
   aggregates, 24 h default range — that is fine.)
3. **Avoid `mpp_data_coverage`** in dashboards — it is an unfiltered full scan across
   all cells. Derive first/last/days from the same function pass with
   `MIN(t)`, `MAX(t)`, `COUNT(DISTINCT t::date)`.
4. **Connection-state queries must use `$__timeTo()`** (not `now()`) so historical
   navigation works.

### Multi-select `cell` variable default

Any dashboard with a multi-select, `includeAll: true` cell variable must default to
**no real cells selected** — opening with "All" fans out the per-cell function across
the whole fleet over the wide default range.

`"current": {"text": [], "value": []}` does **not** work: Grafana falls back to
`options[0]` ("All") when `current.value` is empty. The working pattern is a sentinel
placeholder injected in the variable SQL via the `__text`/`__value` aliases:

```sql
SELECT 0 AS ord, '— none (select cells below) —' AS __text, '__none__' AS __value
UNION ALL
SELECT 1, name, name FROM solar_cell ORDER BY ord, __text
```

with `"sort": 0` (so Grafana keeps the ordering) and
`"current": {"text": ["— none (select cells below) —"], "value": ["__none__"]}`.
`${cell:sqlstring}` then renders `'__none__'`, matching zero rows, and panels load
instantly. "All" stays available in the dropdown.

---

## Adding a new dashboard

1. Build it in the Grafana UI (provisioned dashboards allow UI edits).
2. Share → Export → "Export for sharing externally" **off** (keep the datasource UID).
3. Save the JSON into this directory; set a stable `"uid"` and `"version": 1`.
4. Check it against the [performance rules](#performance-rules) above.
5. Commit. Provisioning picks it up within 30 s.

## Ideas for future dashboards

- **Grafana alerting** on the Data Freshness query (notify when MPP data age exceeds the
  export cadence) — highest operational value.
- Connection-state **timeline** panel (state-timeline of slot occupancy over time).
- Spectral measurement visualization (`spectral_measurement` arrays are currently
  unused in dashboards).
