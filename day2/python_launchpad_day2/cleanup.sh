#!/bin/bash
# Stop all containers and remove unused Docker resources, containers, and images.
# Also stops local dashboard (port 5000).
set -e

echo "Stopping all running containers..."
docker stop $(docker ps -aq) 2>/dev/null || true

echo "Removing all containers..."
docker rm $(docker ps -aq) 2>/dev/null || true

echo "Removing unused images..."
docker image prune -af 2>/dev/null || true

echo "Removing unused build cache..."
docker builder prune -af 2>/dev/null || true

echo "Removing unused networks..."
docker network prune -f 2>/dev/null || true

echo "Removing unused volumes and full system prune..."
docker system prune -af --volumes 2>/dev/null || true

# Stop dashboard if running on port 5000
if command -v lsof &>/dev/null; then
  PID=$(lsof -ti:5000 2>/dev/null) && kill "$PID" 2>/dev/null && echo "Stopped process on port 5000 (PID $PID)." || true
elif command -v fuser &>/dev/null; then
  fuser -k 5000/tcp 2>/dev/null && echo "Stopped process on port 5000." || true
fi

echo "Docker and local services cleanup complete."
