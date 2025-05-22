#!/bin/bash

# Script to run Flyway migrations

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Default values if not set in .env
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-password}
DB_NAME=${DB_NAME:-perocube}
DB_PORT=${DB_PORT:-5432}

# Function to display usage
usage() {
    echo "Usage: $0 [info|migrate|clean|validate|repair]"
    echo "Commands:"
    echo "  info      Show the status of all migrations"
    echo "  migrate   Apply all pending migrations"
    echo "  clean     Remove all objects from the schema"
    echo "  validate  Validate applied migrations against available ones"
    echo "  repair    Repair the schema history table"
    exit 1
}

# Check if command is provided
if [ $# -eq 0 ]; then
    usage
fi

# Execute Flyway command
docker compose run --rm flyway \
    -url=jdbc:postgresql://timescaledb:5432/$DB_NAME \
    -user=$DB_USER \
    -password=$DB_PASSWORD \
    $1
