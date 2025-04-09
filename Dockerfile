# Base image with TimescaleDB (PostgreSQL extension for time-series data)
FROM timescale/timescaledb:latest-pg15

# Environment variables for PostgreSQL
ENV POSTGRES_DB=perocube
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

# Copy TimescaleDB configuration
COPY ./db/config/timescaledb.conf /etc/postgresql/postgresql.conf

# Copy initialization scripts
COPY ./db/sql/schema/ /docker-entrypoint-initdb.d/
COPY ./db/migrations/ /docker-entrypoint-initdb.d/

# Make sure the scripts run in the correct order
RUN mv /docker-entrypoint-initdb.d/init.sql /docker-entrypoint-initdb.d/1_init.sql && \
    mv /docker-entrypoint-initdb.d/tables.sql /docker-entrypoint-initdb.d/2_tables.sql && \
    mv /docker-entrypoint-initdb.d/indexes.sql /docker-entrypoint-initdb.d/3_indexes.sql && \
    mv /docker-entrypoint-initdb.d/V1__initial_schema.sql /docker-entrypoint-initdb.d/4_V1__initial_schema.sql

# Expose PostgreSQL port
EXPOSE 5432

# Set the default command
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]