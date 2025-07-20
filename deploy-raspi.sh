#!/bin/bash

# Deployment script for Raspberry Pi
set -e

echo "🚀 Deploying iCloud Email MCP Server to Raspberry Pi"

# Load environment variables first
if [ -f .env ]; then
    source .env
fi

# Configuration
DOCKER_TAG=${DOCKER_TAG:-latest}
CONTAINER_NAME=${CONTAINER_NAME:-icloud-mcp-server}
MCP_SERVER_PORT=${MCP_SERVER_PORT:-8081}

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure your settings."
    exit 1
fi

# Load environment variables
source .env

# Check required variables
if [ -z "$ICLOUD_USERNAME" ] || [ -z "$ICLOUD_APP_PASSWORD" ]; then
    echo "❌ Missing required environment variables. Please check your .env file."
    exit 1
fi

echo "📦 Building Docker image for ARM64 architecture..."
# Try simple Dockerfile first, fallback to complex one
if [ -f "Dockerfile.simple" ]; then
    echo "Using simplified Dockerfile..."
    docker buildx build --platform linux/arm64 -f Dockerfile.simple -t icloud-mcp-server:$DOCKER_TAG .
else
    echo "Using standard Dockerfile..."
    docker buildx build --platform linux/arm64 -t icloud-mcp-server:$DOCKER_TAG .
fi

echo "🛑 Stopping existing container (if running)..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

echo "🏃 Starting new container..."
docker run -d \
    --name $CONTAINER_NAME \
    --restart unless-stopped \
    --env-file .env \
    -p $MCP_SERVER_PORT:8080 \
    icloud-mcp-server:$DOCKER_TAG

echo "✅ Container started successfully!"

# Wait a moment for container to start
sleep 5

echo "🔍 Checking container status..."
docker ps | grep $CONTAINER_NAME

echo "📋 Container logs:"
docker logs $CONTAINER_NAME

echo "🎉 Deployment complete! Your iCloud Email MCP Server is running on port $MCP_SERVER_PORT."
echo ""
echo "Access your server at: http://your-pi-ip:$MCP_SERVER_PORT"
echo ""
echo "To check logs: docker logs -f $CONTAINER_NAME"
echo "To stop: docker stop $CONTAINER_NAME"
echo "To restart: docker restart $CONTAINER_NAME"