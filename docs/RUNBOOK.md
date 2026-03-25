# Operations Runbook

Procedures for setting up and operating the perocube-data-monitoring-system server.

---

## SymmetricDS Sync Setup (outdoor_monitoring)

One-way replication from the outdoor measuring PC (edge) to this server (hub).
The edge pushes data into the `outdoor_monitoring` database on this server.

### Prerequisites

Replace `<SERVER_HOSTNAME>` with the actual public hostname in:
- `symmetricds/engines/outdoor-hub.properties`
- `outdoor-data-monitoring/symmetricds/engines/monitoring-node.properties` (on the measuring PC)

Add `SYM_PASSWORD` to the `.env` files on **both** the measuring PC and the server. This is the password for the dedicated `sym_user` database account used by SymmetricDS:

```bash
# .env (both machines)
SYM_PASSWORD=<choose a strong password>
```

Also pass `SYM_PASSWORD` through to the Flyway and SymmetricDS containers. In `docker-compose.yml` on the measuring PC, add it to the `flyway` and `symmetricds` environment blocks. On the server it is already wired into `flyway-outdoor` and `symmetricds-hub`.

### Step 1 — Create the outdoor_monitoring database (run once)

This only needs to be done once. If the stack is ever rebuilt from scratch, run it again before starting services.

```bash
# Create the database
docker exec postgres psql -U postgres -c "CREATE DATABASE outdoor_monitoring;"

# Enable TimescaleDB extension
docker exec postgres psql -U postgres -d outdoor_monitoring \
  -c "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"
```

### Step 2 — Bring up the new services

This starts only the three new services. The existing containers (timescaledb, grafana, jupyterhub, nginx) are not restarted.

```bash
docker compose up flyway-outdoor flyway-sym-config symmetricds-hub -d
```

`flyway-outdoor` applies V1–V21 migrations to `outdoor_monitoring`.
`flyway-sym-config` installs the SymmetricDS topology (channels, routers, triggers).
`symmetricds-hub` starts the hub engine and waits for edge registrations.

### Step 3 — Reload nginx (graceful, zero downtime)

```bash
docker exec nginx nginx -s reload
```

### Step 4 — Verify hub is reachable

```bash
curl https://<SERVER_HOSTNAME>/sync/outdoor-hub
# Expected: SymmetricDS web response, not a 404 or 502
```

### Step 5 — Register the edge node

On the **measuring PC**, restart the SymmetricDS container:

```bash
docker compose restart symmetricds
```

The edge will automatically register with the hub. Verify registration on the server:

```bash
docker exec postgres psql -U postgres -d outdoor_monitoring \
  -c "SELECT node_id, node_group_id, sync_url, heartbeat_time FROM sym_node;"
# Edge node row should appear within ~30 seconds
```

### Step 6 — Trigger initial load (run once)

Pushes all existing data from the edge to the hub. Run this **once** after initial registration.

On the **measuring PC**:

```bash
docker exec symmetricds bin/symadmin --engine monitoring-node \
  send-initial-load outdoor-hub-000
```

Monitor progress on the server:

```bash
docker exec postgres psql -U postgres -d outdoor_monitoring \
  -c "SELECT * FROM sym_incoming_batch ORDER BY create_time DESC LIMIT 20;"
```

### Step 7 — Verify sync

Compare row counts between edge and hub for the same database:

```bash
# Run on both measuring PC and server:
docker exec postgres psql -U postgres -d outdoor_monitoring \
  -c "SELECT
        (SELECT COUNT(*) FROM mpp_measurement)        AS mpp_measurements,
        (SELECT COUNT(*) FROM temperature_measurement) AS temp_measurements,
        (SELECT COUNT(*) FROM solar_cell)              AS solar_cells;"
```

---

## Ongoing Operations

### Check sync health

```bash
# Outgoing batches on edge (measuring PC):
docker exec postgres psql -U postgres -d outdoor_monitoring \
  -c "SELECT batch_id, node_id, status, error_flag, create_time
      FROM sym_outgoing_batch
      ORDER BY create_time DESC LIMIT 10;"

# Incoming batches on hub (server):
docker exec postgres psql -U postgres -d outdoor_monitoring \
  -c "SELECT batch_id, node_id, status, error_flag, create_time
      FROM sym_incoming_batch
      ORDER BY create_time DESC LIMIT 10;"
```

Status codes: `OK` = success, `ER` = error, `RQ` = queued, `LD` = loading.

### Restart SymmetricDS hub

```bash
docker compose restart symmetricds-hub
```

### View SymmetricDS hub logs

```bash
docker compose logs -f symmetricds-hub
```
