#!/bin/bash

# Simple script to manage the PostgreSQL/TimescaleDB container

function show_help() {
    echo "Usage: $0 [command]"
    echo "Commands:"
    echo "Database Control:"
    echo "  start    - Start the PostgreSQL/TimescaleDB container"
    echo "  stop     - Stop the container"
    echo "  restart  - Restart the container"
    echo "  status   - Check container status"
    echo "  logs     - View container logs"
    echo "  psql     - Open psql CLI in the container"
    
    echo -e "\nMigrations (Flyway):"
    echo "  migrate  - Apply pending database migrations"
    echo "  info     - Show current migration status"
    echo "  validate - Validate applied migrations"
    echo "  repair   - Repair migration history table"
    
    echo -e "\nMaintenance:"
    echo "  backup   - Run the backup script inside the container"
    echo "  clean    - Remove containers and volumes (WARNING: DESTROYS ALL DATA)"
    echo "  reset    - Clean, start, and initialize with migrations (WARNING: DESTROYS ALL DATA)"
}

case "$1" in
    start)
        echo "Starting PostgreSQL/TimescaleDB container..."
        docker compose up -d
        ;;
    stop)
        echo "Stopping container..."
        docker compose down
        ;;
    restart)
        echo "Restarting container..."
        docker compose restart
        ;;
    status)
        echo "Container status:"
        docker compose ps
        ;;
    logs)
        docker compose logs -f
        ;;
    psql)
        docker compose exec timescaledb psql -U postgres
        ;;
    migrate|info|validate|repair)
        echo "Running Flyway $1..."
        ./db/scripts/migrate.sh $1
        ;;
    backup)
        echo "Running backup script inside container..."
        docker compose exec timescaledb bash /scripts/backup_db.sh
        ;;
    clean)
        echo "WARNING: This will remove all containers and volumes, including all database data!"
        read -p "Are you sure you want to proceed? (y/N): " confirm
        if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
            docker compose down -v
            echo "Containers and volumes removed."
        else
            echo "Operation cancelled."
        fi
        ;;
    reset)
        echo "WARNING: This will remove all containers and volumes, then recreate and initialize the database!"
        read -p "Are you sure you want to proceed? (y/N): " confirm
        if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
            docker compose down -v
            docker compose up -d
            echo "Waiting for database to start..."
            sleep 5
            echo "Applying all migrations..."
            ./db/scripts/migrate.sh migrate
            echo "Database reset complete."
        else
            echo "Operation cancelled."
        fi
        ;;
    *)
        show_help
        ;;
esac