#!/bin/bash

# WC Ducomb Multi-Service Entrypoint
# Ensures both Python API and Node.js frontend start correctly and can communicate

set -e

echo "🚀 Starting WC Ducomb Inventory System..."
echo "================================================"

# Ensure proper permissions
chmod +x /app/entrypoint.sh

# Create logs directory
mkdir -p /app/logs

# Start Python API backend first
echo "🐍 Starting Python API backend on port 5001..."
export API_PORT=5001
export IBM_HOST=10.0.0.7
export IBM_USER=ROBERT  
export IBM_PASSWORD=TECH

# Start Python API in background and wait for it to be ready
python3 /app/api/inventory_lookup.py &
PYTHON_PID=$!

# Wait for Python API to start up
echo "⏳ Waiting for Python API to start..."
for i in {1..30}; do
    if curl -f http://localhost:5001/api/inventory/health >/dev/null 2>&1; then
        echo "✅ Python API is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Python API failed to start within 30 seconds"
        exit 1
    fi
    sleep 1
done

# Start Node.js frontend server
echo "🌐 Starting Node.js frontend server on port 3000..."
export PORT=3000
export API_BASE_URL=http://localhost:5001

# Start Node.js server in background
npm start &
NODE_PID=$!

# Wait for Node.js server to start up
echo "⏳ Waiting for Node.js frontend to start..."
for i in {1..20}; do
    if curl -f http://localhost:3000/health >/dev/null 2>&1; then
        echo "✅ Node.js frontend is ready!"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "❌ Node.js frontend failed to start within 20 seconds"
        kill $PYTHON_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

echo "🎉 Both services are running successfully!"
echo "📊 Python API: http://localhost:5001"
echo "🌐 Frontend: http://localhost:3000"
echo "🔗 Admin Panel: http://localhost:3000/admin"

# Set up signal handlers for graceful shutdown
cleanup() {
    echo "🛑 Shutting down services..."
    kill $PYTHON_PID $NODE_PID 2>/dev/null || true
    wait $PYTHON_PID $NODE_PID 2>/dev/null || true
    echo "✅ Services stopped gracefully"
    exit 0
}

trap cleanup SIGTERM SIGINT

# Keep the script running and monitor processes
while true; do
    # Check if Python API is still running
    if ! kill -0 $PYTHON_PID 2>/dev/null; then
        echo "❌ Python API died, exiting..."
        cleanup
    fi
    
    # Check if Node.js server is still running
    if ! kill -0 $NODE_PID 2>/dev/null; then
        echo "❌ Node.js frontend died, exiting..."
        cleanup
    fi
    
    sleep 10
done