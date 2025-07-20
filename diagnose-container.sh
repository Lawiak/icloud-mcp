#!/bin/bash

echo "🔍 Docker Container Restart Diagnostic Script"
echo "============================================="
echo ""

CONTAINER_NAME=${CONTAINER_NAME:-icloud-mcp-server}

echo "📊 CONTAINER STATUS:"
echo "==================="
docker ps -a | grep $CONTAINER_NAME
echo ""

echo "📋 CONTAINER LOGS (last 50 lines):"
echo "==================================="
docker logs --tail 50 $CONTAINER_NAME
echo ""

echo "🔍 CONTAINER INSPECT (restart info):"
echo "===================================="
docker inspect $CONTAINER_NAME | grep -A 10 -B 5 "RestartCount\|State\|ExitCode\|Error"
echo ""

echo "💾 SYSTEM RESOURCES:"
echo "==================="
echo "Memory usage:"
free -h
echo ""
echo "Disk space:"
df -h
echo ""
echo "Docker system info:"
docker system df
echo ""

echo "🔧 ENVIRONMENT VARIABLES CHECK:"
echo "==============================="
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    echo "Contents (credentials hidden):"
    cat .env | sed 's/=.*/=***HIDDEN***/'
else
    echo "❌ .env file missing!"
fi
echo ""

echo "🐳 DOCKER DAEMON LOGS:"
echo "======================"
echo "Recent Docker daemon messages:"
sudo journalctl -u docker --no-pager --lines 20
echo ""

echo "⚡ QUICK HEALTH CHECKS:"
echo "======================"
echo "1. Docker version:"
docker --version
echo ""

echo "2. Container exit code:"
docker inspect $CONTAINER_NAME --format='{{.State.ExitCode}}'
echo ""

echo "3. Last restart time:"
docker inspect $CONTAINER_NAME --format='{{.State.StartedAt}}'
echo ""

echo "4. Restart count:"
docker inspect $CONTAINER_NAME --format='{{.RestartCount}}'
echo ""

echo "🔄 RESTART POLICY:"
echo "=================="
docker inspect $CONTAINER_NAME --format='{{.HostConfig.RestartPolicy.Name}}'
echo ""

echo "📁 IMAGE INFO:"
echo "=============="
docker images | grep icloud-mcp-server
echo ""

echo "🔍 RUNNING PROCESSES IN CONTAINER:"
echo "=================================="
docker exec $CONTAINER_NAME ps aux 2>/dev/null || echo "Container not running or exec failed"
echo ""

echo "🌐 NETWORK CONNECTIVITY TEST:"
echo "============================="
docker exec $CONTAINER_NAME ping -c 2 8.8.8.8 2>/dev/null || echo "Container not running or network test failed"
echo ""

echo "📤 SAVE FULL LOGS TO FILE:"
echo "=========================="
LOG_FILE="container-debug-$(date +%Y%m%d-%H%M%S).log"
docker logs $CONTAINER_NAME > $LOG_FILE 2>&1
echo "Full container logs saved to: $LOG_FILE"
echo ""

echo "🆘 COMMON ISSUES TO CHECK:"
echo "=========================="
echo "1. Out of memory (check 'free -h' above)"
echo "2. Permission issues (check logs for 'Permission denied')"
echo "3. Network connectivity (check ping test above)"
echo "4. Missing environment variables (check .env above)"
echo "5. Python import errors (check container logs above)"
echo "6. Port conflicts (check if port is already in use)"
echo ""

echo "📋 COMMANDS TO RUN MANUALLY:"
echo "============================"
echo "# Stop the problematic container:"
echo "docker stop $CONTAINER_NAME"
echo ""
echo "# Run container interactively to debug:"
echo "docker run -it --rm --env-file .env icloud-mcp-server:latest /bin/bash"
echo ""
echo "# Test the Python script directly:"
echo "docker run -it --rm --env-file .env icloud-mcp-server:latest python -c 'import icloud_email_server_docker; print(\"Import successful\")'"
echo ""
echo "# Check container resource limits:"
echo "docker stats $CONTAINER_NAME --no-stream"
echo ""

echo "✅ Diagnostic complete! Check the output above for clues."
echo "📎 Share the container logs and any error messages you see."