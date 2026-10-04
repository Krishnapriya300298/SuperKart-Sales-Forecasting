#!/bin/bash
# Builds the backend and frontend images and runs them on a shared Docker network
set -e
cd "$(dirname "$0")"

docker build -t superkart-backend ./backend_files
docker build -t superkart-frontend ./frontend_files

docker network create superkart-app-network 2>/dev/null || true
docker rm -f backend frontend 2>/dev/null || true

docker run -d --name backend  --network superkart-app-network -p 7860:7860 --restart unless-stopped superkart-backend
docker run -d --name frontend --network superkart-app-network -p 8501:8501 --restart unless-stopped superkart-frontend

docker ps
