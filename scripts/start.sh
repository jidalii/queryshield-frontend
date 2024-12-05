#!/bin/sh

APP_NAME="queryshield-app-1"
APP_IMAGE="queryshield-app"

ENV_FILE="../.env"
docker_compose_path="../docker-compose.yml"

echo "=== Starting Cleanup Process for $APP_NAME ==="

echo "Stopping and removing app containers and images..."
docker stop $APP_NAME && echo "Stopped container: $APP_NAME" || echo "Failed to stop container or it doesn't exist"
docker container rm $APP_NAME && echo "Removed container: $APP_NAME" || echo "Failed to remove container or it doesn't exist"
docker rmi $APP_IMAGE -f && echo "Removed image: $APP_IMAGE" || echo "Failed to remove image or it doesn't exist"

echo "Rebuilding and starting containers using Docker Compose..."
docker-compose --env-file $ENV_FILE -f $docker_compose_path up --build -d && \
    echo "Containers rebuilt and started successfully." || echo "Failed to start containers."

sleep 1

echo "Removing dangling volumes and images..."
docker image prune -f && echo "Dangling images removed." || echo "Failed to prune dangling images."

echo "Starting Docker Compose services..."
docker-compose -f $docker_compose_path up -d && echo "Docker Compose services started." || echo "Failed to start services."

echo "=== Cleanup and Restart Process Complete ==="
