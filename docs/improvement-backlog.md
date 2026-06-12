# Improvement Backlog (hub)

From the 2026-06-12 review of both repos. Edge-side items live in the
outdoor-data-monitoring repo's `docs/improvement-backlog.md`.

## Done (branch `feature/system-overview-rework`)

- System Overview: replaced "Total Power" panels (scientist feedback: meaningless
  across heterogeneous cells) with **Data Freshness** and **Power per Cell**; added
  **Ingestion Runs** table from the replicated `ingestion_log`.
- New dashboards: **Environmental Conditions**, **Connection History & Data Coverage**
  (dashboard roadmap complete).
- **Connection-event annotations** on Single Cell Deep-Dive and Degradation Tracking.
- **Experiment filter** on Multi-Cell Comparison (`solar_cell_experiment` is already
  replicated — no SymmetricDS changes were needed).
- **Daily Energy Yield** panel (mWh/cm²/day) on Single Cell Deep-Dive.
- Docs: `grafana/dashboards/README.md` (inventory, PCE formula, performance rules),
  README rewrite; CI for dashboard JSON / UID uniqueness / migration numbering.

## Open

1. **Grafana alerting on Data Freshness** — notify (email/webhook) when MPP data age
   exceeds the export cadence, and on `ingestion_log` rows with `status='failed'`.
   Highest operational value, low effort. Needs a notification channel configured in
   the Grafana instance (alerting rules can then be provisioned from git).
2. **"Dead cell on a sunny day" alert** — connected `mpp_tracking` cell with ~0 power
   while irradiance is high for several daylight hours → broken contact/device.
3. **Per-cell irradiance for PCE** — see the detailed spec in the outdoor repo's
   backlog (new `irradiance_for_cell()` helper + migration pair, then switch the PCE
   queries in Deep-Dive / Multi-Cell / Degradation).
4. **`src/api` FastAPI routes return mock data** — back them with the DB or remove
   them to avoid misleading users.
5. **Legacy `perocube` Streamlit UI / notebooks** — decide deprecation or maintenance;
   they target the legacy schema and confuse new contributors.
6. **Dead migrations** `V26`/`V27` in `db/outdoor_migrations/` — harmless; optional
   cleanup migration dropping the uncallable functions (coordinate with frozen Flyway
   history).
7. **Spectral data visualization** — `spectral_measurement` arrays are unused; Grafana
   is a poor fit for time × wavelength heatmaps, consider a JupyterHub/Voilà notebook.
8. **Slot occupancy state-timeline panel** on Connection History & Coverage.
