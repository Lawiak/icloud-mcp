#!/bin/bash

echo "🔧 Quick Docker Build Fix for Raspberry Pi"
echo "======================================="

# Check if we have the files we need
if [ ! -f "icloud_email_server_docker.py" ]; then
    echo "❌ icloud_email_server_docker.py not found!"
    echo "Make sure you're in the correct directory."
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Copy .env.example to .env and configure your credentials."
    exit 1
fi

echo "📦 Building with simplified Dockerfile..."

# Create a minimal Dockerfile on the fly if needed
cat > Dockerfile.minimal << 'EOF'
FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir fastmcp mcp email-validator

# Create user
RUN useradd --create-home mcpuser

# Copy app
WORKDIR /app
COPY icloud_email_server_docker.py ./
RUN chown mcpuser:mcpuser /app

# Run as non-root
USER mcpuser
EXPOSE 8080
CMD ["python", "icloud_email_server_docker.py"]
EOF

echo "Building Docker image..."
docker build -f Dockerfile.minimal -t icloud-mcp-server:latest .

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "🚀 Starting container..."
    
    # Load environment variables
    source .env
    MCP_SERVER_PORT=${MCP_SERVER_PORT:-8081}
    
    # Stop existing container
    docker stop icloud-mcp-server 2>/dev/null || true
    docker rm icloud-mcp-server 2>/dev/null || true
    
    # Start new container
    docker run -d \
        --name icloud-mcp-server \
        --restart unless-stopped \
        --env-file .env \
        -p $MCP_SERVER_PORT:8080 \
        icloud-mcp-server:latest
    
    echo "✅ Container started successfully!"
    echo "🌐 Server running on port $MCP_SERVER_PORT"
    echo ""
    echo "📋 Check logs with: docker logs -f icloud-mcp-server"
    
    # Clean up
    rm -f Dockerfile.minimal
else
    echo "❌ Build failed!"
    rm -f Dockerfile.minimal
    exit 1
fi