#!/bin/bash

# Simple script to manage the PostgreSQL/TimescaleDB container

function show_help() {
    echo "Usage: $0 [command]"
    echo "Commands:"
    echo "  start    - Start the PostgreSQL/TimescaleDB container"
    echo "  stop     - Stop the container"
    echo "  restart  - Restart the container"
    echo "  status   - Check container status"
    echo "  logs     - View container logs"
    echo "  psql     - Open psql CLI in the container"
    echo "  init     - Run the init_db script inside the container"
    echo "  backup   - Run the backup script inside the container"
    echo "  clean    - Remove containers and volumes (WARNING: DESTROYS ALL DATA)"
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
        docker compose exec postgres psql -U postgres
        ;;
    init)
        echo "Running initialization script inside container..."
        docker compose exec postgres bash /scripts/init_db.sh
        ;;
    backup)
        echo "Running backup script inside container..."
        docker compose exec postgres bash /scripts/backup_db.sh
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
    *)
        show_help
        ;;
esac