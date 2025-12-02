# SymmetricDS Integration Walkthrough

## Overview
This feature adds database synchronization between the Edge (local) and Cloud instances using SymmetricDS.

## Services Added
- `timescaledb-cloud`: Simulates the Cloud database.
- `flyway-cloud`: Initializes the Cloud database schema (application tables).
- `symmetricds-edge`: The synchronization engine for the Edge node.
- `symmetricds-cloud`: The synchronization engine for the Cloud node (Registration Server).
- `flyway-sym-config`: Initializes the SymmetricDS configuration (channels, triggers, routers) after the engine starts.

## How to Run

1.  **Start the stack**:
    ```bash
    docker compose up -d
    ```

2.  **Verify Services**:
    Check if all services are healthy:
    ```bash
    docker compose ps
    ```

3.  **Verify Sync**:
    - Connect to the Edge database and insert a record.
    - Connect to the Cloud database and verify the record exists.

    **Example**:
    ```bash
    # Connect to Edge DB
    docker compose exec timescaledb psql -U postgres -d perocube -c "INSERT INTO scientist (scientist_id, name) VALUES (gen_random_uuid(), 'Test Scientist');"

    # Check Cloud DB
    docker compose exec timescaledb-cloud psql -U postgres -d perocube -c "SELECT * FROM scientist WHERE name = 'Test Scientist';"
    ```

## Configuration Details
- **Edge Config**: `symmetricds/engines/edge.properties`
- **Cloud Config**: `symmetricds/engines/cloud.properties`
- **SymmetricDS Edge URL**: `http://localhost:8081` (Port 8081 to avoid conflict with other services)
- **SymmetricDS Cloud URL**: `http://localhost:31416`
- **Sync Rules**: `symmetricds/sql/V99__symmetricds_config.sql` (defines channels, triggers, routers)
- **Flyway History**: SymmetricDS uses a separate Flyway history table (`flyway_schema_history_sym`) to avoid conflicts with application migrations.
- **Auto-Registration**: Enabled on Cloud node (`auto.registration=true`) to allow Edge nodes to register automatically.
- **Sync URL**: Cloud node uses the **Public URL** (e.g., `http://nomad02.csn32.bessy.de:31415/sync/cloud-000`) so it is reachable by Edge nodes.

## Verification
1.  **Start Stack**: `docker compose up -d`
2.  **Verify Health**: `docker compose ps` (Ensure all services are healthy)
3.  **Check Registration**: `docker compose logs symmetricds-edge` should show successful registration.
4.  **Test Sync**:
    ```bash
    # Insert into Edge
    docker compose exec timescaledb psql -U postgres -d perocube -c "INSERT INTO scientist (scientist_id, name) VALUES (gen_random_uuid(), 'Sync Test');"
    
    # Check Cloud
    docker compose exec timescaledb-cloud psql -U postgres -d perocube -c "SELECT * FROM scientist WHERE name = 'Sync Test';"
    ```
## Monitoring Sync Status
A Grafana dashboard is pre-configured on the Edge device to monitor synchronization backlog.

1.  **Access Grafana**: Open `http://localhost:3000` (or your Edge IP).
2.  **Login**: Default credentials are `admin` / `admin` (or as set in `.env`).
3.  **View Dashboard**: Navigate to **Dashboards** -> **SymmetricDS Sync Stats**.
    -   **Pending Batches**: Shows the number of batches waiting to be pushed to the Cloud.
    -   **Pending Batch Details**: Lists specific batches in error or pending state.

## Production Deployment Guide

To transition this setup from a local development environment to a production deployment, follow these critical steps:

### 1. Splitting Docker Compose for Production
For production, we have created separate Docker Compose files for the Cloud and Edge environments. These are tracked in the repository.

#### Cloud Server (`docker-compose.cloud.yml`)
Run this on your central cloud server. It hosts the central database, the registration server, configuration management, and all analytics/visualization applications.

**Usage:**
```bash
docker compose -f docker-compose.cloud.yml up -d
```

**Services included:**
*   `timescaledb` (Central DB)
*   `flyway` (Schema Migration)
*   `symmetricds-cloud` (Sync Engine & Registration Server)
*   `flyway-sym-config` (Sync Configuration)
*   `jupyterhub` (Analytics)
*   `grafana` (Visualization)
*   `streamlit` (Metadata Ingestion)

**Configuration:**
*   Ensure `symmetricds-cloud` port `31415` is accessible from the internet (or VPN).
*   Set environment variables in `.env` (e.g., `DB_PASSWORD`, `JUPYTER_TOKEN`).

#### Edge Device (`docker-compose.edge.yml`)
Run this on each edge device. It hosts only the local database and the sync engine.

**Usage:**
```bash
docker compose -f docker-compose.edge.yml up -d
```

**Services included:**
*   `timescaledb` (Local DB)
*   `flyway` (Schema Migration)
*   `symmetricds-edge` (Sync Engine)
*   `jupyterhub` (Local Analytics)
*   `grafana` (Sync Monitoring - Port 3000)

**Configuration:**
*   **Crucial**: Set `CLOUD_REGISTRATION_URL` in your `.env` file to point to your Cloud Server.
    ```bash
    CLOUD_REGISTRATION_URL=http://sync.perocube.com:31415/sync/cloud-000
    ```
*   Set `ENGINE_NAME` to a unique value for each device (e.g., `edge-002`, `edge-003`).

### 2. Security Hardening
*   **Credentials Management**:
    *   **NEVER** hardcode passwords in `.properties` files.
    *   Use **Docker Secrets** or environment variable substitution at runtime.
    *   SymmetricDS supports encrypted passwords in properties files (use `symadmin encrypt-text`).
*   **Network Security (SSL/TLS)**:
    *   Enable **HTTPS** for synchronization traffic.
    *   Configure `https.port` and provide a valid Keystore (`keystore.file`, `keystore.password`) in `symmetric-server.properties`.
    *   Alternatively, place a **Reverse Proxy** (Nginx, Traefik, HAProxy) in front of the Cloud SymmetricDS node to handle SSL termination.
*   **Registration Security**:
    *   Disable `auto.registration=true` on the Cloud node after the initial rollout if possible, or use **Node Group Links** to restrict which nodes can register.
    *   Use `registration.url` with specific open registration windows managed via `symadmin open-registration`.

### 3. Infrastructure & Networking
*   **Cloud Node Accessibility**:
    *   The Cloud SymmetricDS node must be reachable by all Edge nodes.
    *   Assign a **Static IP** or a **DNS Hostname** (e.g., `sync.perocube.com`) to the Cloud server.
    *   Update `edge.properties` `registration.url` and `sync.url` to use this public address (e.g., `https://sync.perocube.com/sync/cloud-000`).
*   **Firewall Rules**:
    *   Allow inbound traffic on the sync port (default `31415` or `443` for HTTPS) on the Cloud server **only** from trusted Edge IP ranges if feasible, or open to 0.0.0.0/0 if Edge IPs are dynamic.
*   **Persistence**:
    *   Ensure Docker volumes for `timescaledb` and `symmetricds` (specifically `engines` and `logs`) are mounted to **persistent, backed-up storage** on the host machine.

### 4. Operational Maintenance
*   **Monitoring**:
    *   Monitor the `sym_data_gap` table. Growing gaps indicate sync lag.
    *   Monitor `sym_outgoing_batch` for batches in `ER` (Error) status.
    *   Use JMX or the SymmetricDS REST API to monitor node status.
*   **Backups**:
    *   Regularly backup the Cloud database.
    *   Backup the `symmetricds/engines` configuration directory.
*   **Scaling**:
    *   For a large number of Edge nodes, tune the Cloud node's thread pools (`job.pull.thread.count`, `job.push.thread.count`) in `cloud.properties`.

## Advanced Configuration Examples

These examples show how to modify `symmetricds/sql/V99__symmetricds_config.sql` for common advanced scenarios.

### 1. Bi-Directional Sync (Cloud to Edge)
To sync data back from the Cloud to the Edge, add a reverse router and link it to your triggers.

```sql
-- 1. Create a Router for Cloud -> Edge
INSERT INTO sym_router (router_id, source_node_group_id, target_node_group_id, router_type, create_time, last_update_time) 
VALUES('cloud_2_edge', 'cloud', 'edge', 'default', current_timestamp, current_timestamp);

-- 2. Link the Trigger to this new Router
-- This example syncs the 'scientist' table back to the edge
INSERT INTO sym_trigger_router (trigger_id, router_id, initial_load_order, last_update_time, create_time) 
VALUES('scientist_trigger', 'cloud_2_edge', 100, current_timestamp, current_timestamp);
```

### 2. Sync Specific Tables Only
Instead of using the wildcard `*` to sync all tables, define triggers for specific tables.

```sql
-- 1. Define specific triggers (Replace the 'all_tables' trigger)
INSERT INTO sym_trigger (trigger_id, source_table_name, channel_id, last_update_time, create_time) 
VALUES('scientist_trigger', 'scientist', 'default', current_timestamp, current_timestamp);

INSERT INTO sym_trigger (trigger_id, source_table_name, channel_id, last_update_time, create_time) 
VALUES('measurements_trigger', 'measurements', 'default', current_timestamp, current_timestamp);

-- 2. Link these triggers to the Edge->Cloud router
INSERT INTO sym_trigger_router (trigger_id, router_id, initial_load_order, last_update_time, create_time) 
VALUES('scientist_trigger', 'edge_2_cloud', 100, current_timestamp, current_timestamp);

INSERT INTO sym_trigger_router (trigger_id, router_id, initial_load_order, last_update_time, create_time) 
VALUES('measurements_trigger', 'edge_2_cloud', 100, current_timestamp, current_timestamp);
```
