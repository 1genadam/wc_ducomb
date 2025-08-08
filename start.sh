#!/bin/sh

# WC Ducomb Inventory System - Multi-Service Startup Script
# Starts both Python API backend and Node.js frontend server

echo "🚀 Starting WC Ducomb Inventory System..."
echo "=========================================="

# Function to handle shutdown
cleanup() {
    echo "🛑 Shutting down services..."
    kill -TERM $PYTHON_PID 2>/dev/null
    kill -TERM $NODE_PID 2>/dev/null
    wait $PYTHON_PID 2>/dev/null
    wait $NODE_PID 2>/dev/null
    echo "✅ Services stopped gracefully"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Create logs directory if it doesn't exist
mkdir -p logs

# Start Python API backend
echo "🐍 Starting Python API backend on port ${API_PORT:-5001}..."
API_PORT=${API_PORT:-5001} python3 api/inventory_lookup.py > logs/api.log 2>&1 &
PYTHON_PID=$!

# Wait a moment for Python backend to start
sleep 5

# Check if Python backend started successfully
if ! kill -0 $PYTHON_PID 2>/dev/null; then
    echo "❌ Python backend failed to start"
    cat logs/api.log
    exit 1
fi

echo "✅ Python backend started with PID $PYTHON_PID"

# Start Node.js frontend server
echo "🌐 Starting Node.js frontend server on port 3000..."
npm start > logs/frontend.log 2>&1 &
NODE_PID=$!

# Wait a moment for Node.js frontend to start
sleep 3

# Check if Node.js frontend started successfully
if ! kill -0 $NODE_PID 2>/dev/null; then
    echo "❌ Node.js frontend failed to start"
    cat logs/frontend.log
    cleanup
    exit 1
fi

echo "✅ Node.js frontend started with PID $NODE_PID"

# Health check loop
echo "🔍 Starting health monitoring..."
while true; do
    # Check if both processes are still running
    if ! kill -0 $PYTHON_PID 2>/dev/null; then
        echo "❌ Python backend died, restarting..."
        python3 api/inventory_lookup.py > logs/api.log 2>&1 &
        PYTHON_PID=$!
        sleep 5
    fi
    
    if ! kill -0 $NODE_PID 2>/dev/null; then
        echo "❌ Node.js frontend died, restarting..."
        npm start > logs/frontend.log 2>&1 &
        NODE_PID=$!
        sleep 3
    fi
    
    # Log status every 5 minutes
    echo "📊 Services running - Python PID: $PYTHON_PID, Node PID: $NODE_PID"
    
    sleep 300  # Check every 5 minutes
done