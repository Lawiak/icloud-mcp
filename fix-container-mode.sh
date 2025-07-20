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

echo ""
echo "🔄 Starting container with HTTP mode..."
docker run -d \
    --name $CONTAINER_NAME \
    --restart unless-stopped \
    --env-file .env \
    -p $MCP_SERVER_PORT:8080 \
    -v $(pwd)/icloud_email_server_http.py:/app/icloud_email_server_http.py \
    icloud-mcp-server:latest python icloud_email_server_http.py

echo ""
echo "🔄 Alternative: Run with persistent STDIO mode (for MCP clients):"
echo "docker run -d \\"
echo "    --name ${CONTAINER_NAME}-stdio \\"
echo "    --restart unless-stopped \\"
echo "    --env-file .env \\"
echo "    -v \$(pwd)/icloud_email_server_stdio_persistent.py:/app/icloud_email_server_stdio_persistent.py \\"
echo "    icloud-mcp-server:latest python icloud_email_server_stdio_persistent.py"

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

echo "✅ Done! Container should now stay running."
echo ""
echo "🧪 Test the HTTP server:"
echo "   curl http://localhost:$MCP_SERVER_PORT/"
echo "   curl http://localhost:$MCP_SERVER_PORT/health"
echo "   curl http://localhost:$MCP_SERVER_PORT/test"
echo ""
echo "💡 For MCP client use, run the STDIO version above"