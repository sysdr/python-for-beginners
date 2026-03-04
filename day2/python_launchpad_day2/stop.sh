#!/bin/bash
# Stop Docker container and dashboard (port 5000).
PROJECT_NAME="python_launchpad_day2"
DOCKER_CONTAINER_NAME="${PROJECT_NAME}_container"
DOCKER_IMAGE_NAME="${PROJECT_NAME}_app"
docker stop "$DOCKER_CONTAINER_NAME" 2>/dev/null || true
docker rm "$DOCKER_CONTAINER_NAME" 2>/dev/null || true
docker rmi "$DOCKER_IMAGE_NAME" 2>/dev/null || true
if command -v lsof &>/dev/null; then
  PID=$(lsof -ti:5000 2>/dev/null) && kill "$PID" 2>/dev/null && echo "Stopped dashboard (PID $PID)." || true
elif command -v fuser &>/dev/null; then
  fuser -k 5000/tcp 2>/dev/null && echo "Stopped process on port 5000." || true
fi
echo "Cleaned up Docker and dashboard."
