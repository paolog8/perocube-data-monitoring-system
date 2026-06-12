# Perocube Data Monitoring System

Central **hub server** for PV outdoor monitoring data at PVcomB. A PostgreSQL +
TimescaleDB instance receives data replicated from the outdoor measurement PC
(SymmetricDS, edge → hub) and serves it to scientists through **Grafana** dashboards and
**JupyterHub** notebooks, behind an Nginx reverse proxy.

> ⚠️ **The Postgres instance on this server is shared.** It hosts the legacy `perocube`
> database *and* the replicated `outdoor_monitoring` database (and potentially others).
> Never run destructive operations instance-wide; always target the specific database,
> and treat schema changes to anything but `outdoor_monitoring` as out of scope.

## Architecture

```
Measurement PC (edge)                      This server (hub)
┌────────────────────────┐                 ┌─────────────────────────────────────┐
│ outdoor-data-monitoring│   SymmetricDS   │ timescaledb (shared instance)       │
│ Postgres + ingestion   │ ──────────────► │   ├── outdoor_monitoring  ◄─ synced │
│ + Streamlit registry   │   push (31415)  │   └── perocube (legacy)             │
└────────────────────────┘                 │ grafana ── jupyterhub ── streamlit  │
                                           │ nginx: / → grafana, /hub → jupyter  │
                                           └─────────────────────────────────────┘
```

### Docker Compose services

| Service | Purpose |
|---|---|
| `timescaledb` | PostgreSQL 15 + TimescaleDB (shared instance, multiple DBs) |
| `flyway` | Migrations for the legacy `perocube` DB — files live on NFS, **not in git** |
| `create-outdoor-db` | One-shot: creates the `outdoor_monitoring` database if missing |
| `flyway-outdoor` | Migrations for `outdoor_monitoring` from `db/outdoor_migrations/` (in git) |
| `flyway-sym-config` | Applies SymmetricDS hub configuration from `symmetricds/sql/` |
| `symmetricds-hub` | Replication hub; the edge node registers and pushes here (port 31415) |
| `restart-orchestrator` | Periodically restarts SymmetricDS (workaround for long-run stalls) |
| `grafana` | Dashboards — see [`grafana/dashboards/README.md`](grafana/dashboards/README.md) |
| `jupyterhub` | Notebook analytics (+ Voilà) |
| `streamlit` | Legacy metadata UI for the `perocube` schema |
| `nginx` | Reverse proxy: `/` → Grafana, `/hub` → JupyterHub |

## Two databases, two migration pipelines

**Do not confuse these.**

| Database | Migrations | Schema |
|---|---|---|
| `perocube` (legacy) | NFS mount (`/nfs/.../flyway/migrations/`), not in git | `solar_cell_device`, `measurement_connection_event`, `mpp_tracking_channel`, … |
| `outdoor_monitoring` | [`db/outdoor_migrations/`](db/outdoor_migrations/) (in git) | Replica of the *outdoor-data-monitoring* repo schema |

Rules for `db/outdoor_migrations/`:

- **Append only, never renumber.** The live hub has all versions applied and frozen.
  Version numbers are offset from the upstream outdoor repo (this repo inserted
  `V24__sym_user_superuser` and two legacy files): upstream V24 = here V25; upstream
  V25–V31 = here V28–V34.
- `V26__mpp_functions.sql` and `V27__board_connection_status.sql` are **dead
  migrations**: they reference legacy-schema tables that don't exist in
  `outdoor_monitoring`, so the functions they create are uncallable there. Leave them in
  place (Flyway history depends on them); never mirror them upstream.
- New upstream migrations are copied here with the +3 offset and applied by
  `flyway-outdoor` on the next `docker compose up`.

## Dashboards & analytics

All Grafana dashboards target the **`outdoor_monitoring`** database only. Dashboards are
version-controlled in [`grafana/dashboards/`](grafana/dashboards/) and provisioned
automatically — see [`grafana/dashboards/README.md`](grafana/dashboards/README.md) for
the dashboard inventory, the PCE formula and its validity constraints, and the query
performance rules.

## Repository layout

```
config/                  app, logging, nginx, TLS configuration
db/outdoor_migrations/   Flyway migrations for outdoor_monitoring (in git, append-only)
docs/RUNBOOK.md          server setup & operations procedures (SymmetricDS, registration)
docs/data-models/        legacy schema diagrams
grafana/dashboards/      provisioned dashboard JSON + documentation
grafana/provisioning/    dashboard/datasource provisioning config
symmetricds/engines/     hub engine properties
symmetricds/sql/         hub replication configuration (applied by flyway-sym-config)
src/                     legacy Perocube code (Streamlit CRUD UI, FastAPI stubs,
                         LabVIEW TCP connector, CSV bulk uploader) — targets the
                         legacy `perocube` schema, not outdoor_monitoring
notebooks/               data upload / analysis notebooks (legacy)
```

## Operations

Deployment, SymmetricDS setup, node registration, and recovery procedures are in
[`docs/RUNBOOK.md`](docs/RUNBOOK.md).

Day-to-day:

```bash
docker compose up -d          # start / apply new migrations & dashboards
docker compose logs -f symmetricds-hub
docker compose logs flyway-outdoor
```

Grafana picks up dashboard JSON changes within ~30 s of a `git pull` (file
provisioning); no restart needed.

## Configuration

- `config/app_config.yaml` — application defaults, overridden by env vars
  (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`)
- `config/logging_config.yaml` — structured logging
- `config/nginx.conf` — reverse proxy and TLS
- `.env` — secrets (DB passwords, `SYM_PASSWORD`); never committed
