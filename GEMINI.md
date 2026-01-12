# Perocube Data Monitoring System

## Project Overview

This project is a comprehensive data monitoring system for Perocube solar cell data. It is built on a microservices architecture using Docker and Docker Compose. The system is designed to collect, store, process, and visualize time-series data from solar cell experiments.

### Key Technologies

*   **Backend:** Python with FastAPI for the main API.
*   **Frontend:** Streamlit for metadata ingestion and simple data interaction.
*   **Database:** PostgreSQL with the TimescaleDB extension for efficient time-series data storage.
*   **Database Migrations:** Flyway for managing database schema evolution.
*   **Data Analysis & Notebooks:** JupyterLab for data exploration and analysis.
*   **Dashboards & Visualization:** Grafana for creating and displaying dashboards.
*   **Data Synchronization:** SymmetricDS for replicating data between edge and cloud instances.
*   **Containerization:** Docker and Docker Compose for service orchestration.

### Architecture

The system is composed of several services defined in `docker-compose.yml`:

*   `timescaledb`: The primary PostgreSQL/TimescaleDB database for data storage.
*   `flyway`: Applies database migrations to the `timescaledb` service.
*   `streamlit`: A Python web application for metadata ingestion.
*   `jupyterhub`: Provides a Jupyter notebook environment for data analysis.
*   `grafana`: A visualization platform for creating dashboards from the database.
*   `symmetricds-edge` & `symmetricds-cloud`: Services for data synchronization between a local (edge) and a remote (cloud) database.

## Building and Running the Project

### Prerequisites

*   Docker
*   Docker Compose

### Running the System

The entire application stack can be started using Docker Compose.

1.  **Environment Variables:** Create a `.env` file in the project root and populate it with the required environment variables. Key variables can be found in the `docker-compose.yml` file (e.g., `DB_PASSWORD`, `JUPYTER_TOKEN`).

2.  **Start Services:**
    ```bash
    docker-compose up -d
    ```

### Key Services and Ports

*   **Streamlit UI:** http://localhost:8501
*   **Grafana:** http://localhost:3000
*   **JupyterHub:** http://localhost:8888
*   **PostgreSQL/TimescaleDB:** Accessible on port `${DB_PORT}` (defined in `.env`).
*   **FastAPI (if run locally):** The `src/api` directory contains a FastAPI application, but it is not defined as a service in the main `docker-compose.yml`. It appears the streamlit app contains the UI.

## Development Conventions

### Code Style

The project uses a standard set of Python code formatting and linting tools.

*   **Formatter:** `black`
*   **Linter:** `flake8`
*   **Import Sorting:** `isort`
*   **Type Checking:** `mypy`

To format and lint the code, you can run these tools from the project root.

### Testing

The project uses `pytest` for unit and integration tests. Tests are located in the `tests/` directory.

To run the tests:

```bash
pytest
```

### Database Migrations

Database schema changes are managed by Flyway. SQL migration scripts are located in the `db/migrations` directory. When the `flyway` service starts, it automatically applies any new migrations to the database.

To create a new migration, add a new SQL file to the `db/migrations` directory following the Flyway naming convention (e.g., `V4__my_new_feature.sql`).
