#!/bin/bash

# Script to initialize the PostgreSQL database with TimescaleDB for the Perocube project

echo "Starting Perocube database initialization..."

# Define variables
DB_NAME="perocube"
DB_USER="postgres"  # Or specify your PostgreSQL username
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
SQL_DIR="${SCRIPT_DIR}/../sql"

# Check if PostgreSQL is running
pg_isready
if [ $? -ne 0 ]; then
    echo "Error: PostgreSQL is not running. Please start PostgreSQL and try again."
    exit 1
fi

# Create database and enable TimescaleDB extension
echo "Creating database and enabling TimescaleDB extension..."
psql -U "$DB_USER" -f "${SQL_DIR}/schema/init.sql"

if [ $? -ne 0 ]; then
    echo "Error: Failed to create database or enable TimescaleDB extension."
    exit 1
fi

# Create tables
echo "Creating tables..."
psql -U "$DB_USER" -d "$DB_NAME" -f "${SQL_DIR}/schema/tables.sql"

if [ $? -ne 0 ]; then
    echo "Error: Failed to create tables."
    exit 1
fi

# Create indexes
echo "Creating indexes..."
psql -U "$DB_USER" -d "$DB_NAME" -f "${SQL_DIR}/schema/indexes.sql"

if [ $? -ne 0 ]; then
    echo "Error: Failed to create indexes."
    exit 1
fi

echo "Database initialization completed successfully!"