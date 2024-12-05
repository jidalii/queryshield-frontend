#!/bin/bash

# Exit the script if any command fails
set -e

# Define the project name (same as in the `name` field in your docker-compose.yml)
PROJECT_NAME="queryshield"
APP_IMAGE="queryshield-app"

echo "Stopping and removing containers, networks, and volumes for project: $PROJECT_NAME"

# Stop and remove all containers, networks, and volumes associated with the compose file
docker-compose down --volumes --remove-orphans

echo "Removing all volumes for the project if exist..."
docker volume inspect "${PROJECT_NAME}_pg_data_queryshield" >/dev/null 2>&1 && \
    docker volume rm "${PROJECT_NAME}_pg_data_queryshield" || \
    echo "Volume ${PROJECT_NAME}_pg_data_queryshield does not exist, skipping..."

docker volume inspect "${PROJECT_NAME}_pg_data_verification" >/dev/null 2>&1 && \
    docker volume rm "${PROJECT_NAME}_pg_data_verification" || \
    echo "Volume ${PROJECT_NAME}_pg_data_verification does not exist, skipping..."

echo "Removing app image..."
docker rmi $APP_IMAGE

echo "Removing dangling volumes..."
docker volume prune -f

echo "Removing dangling images..."
docker image prune -f

echo "Cleanup complete!"
