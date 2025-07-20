#!/bin/bash

echo "🔍 Checking for available ports on your Raspberry Pi..."
echo ""

# Common ports that might be good alternatives
SUGGESTED_PORTS=(8081 8082 8090 8091 9000 9001 9080 9090 3001 3002 5000 5001)

echo "📊 Current port usage:"
echo "Port 8080: $(ss -tuln | grep :8080 >/dev/null && echo "❌ IN USE" || echo "✅ AVAILABLE")"
echo ""

echo "🔍 Checking suggested alternative ports:"
for port in "${SUGGESTED_PORTS[@]}"; do
    if ss -tuln | grep ":$port " >/dev/null 2>&1; then
        echo "Port $port: ❌ IN USE"
    else
        echo "Port $port: ✅ AVAILABLE"
    fi
done

echo ""
echo "💡 To use a different port:"
echo "1. Edit your .env file:"
echo "   nano .env"
echo "2. Add this line:"
echo "   MCP_SERVER_PORT=8081"
echo "3. Run the deployment script again:"
echo "   ./deploy-raspi.sh"
echo ""

echo "🔍 Full port scan (this may take a moment)..."
echo "All listening ports on your system:"
ss -tuln | grep LISTEN | sort -n