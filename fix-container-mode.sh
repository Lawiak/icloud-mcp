#!/bin/bash

echo "🔧 Fixing Container STDIO Issue"
echo "==============================="

# Load environment variables
if [ -f .env ]; then
    source .env
fi

CONTAINER_NAME=${CONTAINER_NAME:-icloud-mcp-server}
MCP_SERVER_PORT=${MCP_SERVER_PORT:-8081}

echo "🛑 Stopping existing container..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

echo ""
echo "🚀 Option 1: Run with STDIO kept open (for MCP clients)"
echo "This keeps container running for MCP client connections:"
echo ""

echo "docker run -d \\"
echo "    --name $CONTAINER_NAME \\"
echo "    --restart unless-stopped \\"
echo "    --env-file .env \\"
echo "    -p $MCP_SERVER_PORT:8080 \\"
echo "    -i \\"
echo "    icloud-mcp-server:latest"
echo ""

echo "🌐 Option 2: Run with HTTP server mode (recommended for testing)"
echo "This will keep running and you can test via HTTP:"

# Create a modified server that runs HTTP instead of STDIO
cat > temp_http_server.py << 'EOF'
#!/usr/bin/env python3

import os
from fastmcp import FastMCP
from icloud_email_server_docker import *

# Override the server to use HTTP instead of STDIO
if __name__ == "__main__":
    print("Starting iCloud Email MCP Server in HTTP mode...")
    print(f"Username: {USERNAME}")
    print(f"Server will run on port 8080")
    
    # Keep the server running with HTTP transport
    import uvicorn
    from fastmcp.server import create_server_app
    
    app = create_server_app(mcp)
    uvicorn.run(app, host="0.0.0.0", port=8080)
EOF

echo ""
echo "🔄 Starting container with HTTP mode..."
docker run -d \
    --name $CONTAINER_NAME \
    --restart unless-stopped \
    --env-file .env \
    -p $MCP_SERVER_PORT:8080 \
    -v $(pwd)/temp_http_server.py:/app/temp_http_server.py \
    icloud-mcp-server:latest python temp_http_server.py

sleep 3

echo ""
echo "📊 Container status:"
docker ps | grep $CONTAINER_NAME

echo ""
echo "📋 Container logs:"
docker logs $CONTAINER_NAME

echo ""
echo "🧪 Test the server:"
echo "curl http://localhost:$MCP_SERVER_PORT"
echo ""

# Clean up
rm -f temp_http_server.py

echo "✅ Done! Container should now stay running."
echo ""
echo "💡 For MCP client use, you may need STDIO mode:"
echo "   docker run -i --env-file .env icloud-mcp-server:latest"