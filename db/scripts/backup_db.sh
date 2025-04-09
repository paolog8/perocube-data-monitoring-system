#!/bin/bash

# Script to backup the Perocube PostgreSQL database

echo "Starting Perocube database backup..."

# Define variables
DB_NAME="perocube"
DB_USER="postgres"  # Or specify your PostgreSQL username
BACKUP_DIR="$HOME/perocube_backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/perocube_backup_${TIMESTAMP}.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if PostgreSQL is running
pg_isready
if [ $? -ne 0 ]; then
    echo "Error: PostgreSQL is not running. Please start PostgreSQL and try again."
    exit 1
fi

# Perform backup
echo "Backing up database to ${BACKUP_FILE}..."
pg_dump -U "$DB_USER" -d "$DB_NAME" -F p -f "$BACKUP_FILE"

if [ $? -ne 0 ]; then
    echo "Error: Failed to backup database."
    exit 1
fi

# Compress the backup
gzip "$BACKUP_FILE"

echo "Database backup completed successfully!"
echo "Backup file: ${BACKUP_FILE}.gz"