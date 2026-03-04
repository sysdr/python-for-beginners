#!/bin/bash
# Stop and remove Docker container/image created by setup
PROJECT_NAME="day1_project"
DOCKER_IMAGE_NAME="${PROJECT_NAME}_app"
DOCKER_CONTAINER_NAME="${PROJECT_NAME}_container"
docker stop "$DOCKER_CONTAINER_NAME" 2>/dev/null || true
docker rm "$DOCKER_CONTAINER_NAME" 2>/dev/null || true
docker rmi "$DOCKER_IMAGE_NAME" 2>/dev/null || true
# Stop dashboard if running (port 5000)
if command -v lsof &>/dev/null; then
  PID=$(lsof -ti:5000 2>/dev/null) && kill "$PID" 2>/dev/null && echo "Stopped dashboard (PID $PID)." || true
elif command -v fuser &>/dev/null; then
  fuser -k 5000/tcp 2>/dev/null && echo "Stopped process on port 5000." || true
fi
echo "Cleaned up Docker resources."
