#!/bin/bash

# WC Ducomb Inventory System - Robust Startup Script
# Enhanced startup with better error handling and monitoring

set -e  # Exit on any error

echo "🚀 Starting WC Ducomb Inventory System (Robust Mode)..."
echo "=============================================="

# Environment variables with defaults
export NODE_ENV="${NODE_ENV:-production}"
export PORT="${PORT:-3000}"
export API_PORT="${API_PORT:-5001}"
export IBM_HOST="${IBM_HOST:-10.0.0.7}"

echo "📊 Configuration:"
echo "  NODE_ENV: $NODE_ENV"
echo "  Frontend Port: $PORT"
echo "  API Port: $API_PORT" 
echo "  IBM Host: $IBM_HOST"

# Create logs directory
mkdir -p logs

# Function to check if a port is available
check_port_available() {
    local port=$1
    if ! command -v netstat >/dev/null 2>&1; then
        return 0  # Assume available if netstat not available
    fi
    if netstat -ln | grep -q ":$port "; then
        echo "⚠️ Port $port is already in use"
        return 1
    fi
    return 0
}

# Function to wait for service to be ready
wait_for_service() {
    local port=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service_name on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if command -v curl >/dev/null 2>&1; then
            if curl -sf "http://localhost:$port/health" >/dev/null 2>&1 || curl -sf "http://localhost:$port" >/dev/null 2>&1; then
                echo "✅ $service_name is ready on port $port"
                return 0
            fi
        else
            # Fallback: check if process is listening on port
            if netstat -ln 2>/dev/null | grep -q ":$port "; then
                echo "✅ $service_name appears to be listening on port $port"
                return 0
            fi
        fi
        
        echo "  Attempt $attempt/$max_attempts - waiting for $service_name..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to start on port $port after $max_attempts attempts"
    return 1
}

# Cleanup function
cleanup() {
    echo "🛑 Shutting down services..."
    if [ ! -z "$PYTHON_PID" ]; then
        kill -TERM $PYTHON_PID 2>/dev/null || true
        wait $PYTHON_PID 2>/dev/null || true
    fi
    if [ ! -z "$NODE_PID" ]; then
        kill -TERM $NODE_PID 2>/dev/null || true
        wait $NODE_PID 2>/dev/null || true
    fi
    echo "✅ Cleanup completed"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT EXIT

# Start Python API backend
echo "🐍 Starting Python API backend..."

# Check if API port is available
if ! check_port_available $API_PORT; then
    echo "❌ API port $API_PORT is not available"
    exit 1
fi

# Start Python backend with explicit environment
env API_PORT=$API_PORT python3 api/inventory_lookup.py > logs/api.log 2>&1 &
PYTHON_PID=$!
echo "  Started with PID $PYTHON_PID"

# Wait for Python API to be ready
if ! wait_for_service $API_PORT "Python API"; then
    echo "❌ Python API failed to start properly"
    echo "--- API Log Output ---"
    cat logs/api.log 2>/dev/null || echo "No API log available"
    exit 1
fi

# Start Node.js frontend server
echo "🌐 Starting Node.js frontend server..."

# Check if frontend port is available
if ! check_port_available $PORT; then
    echo "❌ Frontend port $PORT is not available"
    exit 1
fi

# Start Node.js frontend
env PORT=$PORT npm start > logs/frontend.log 2>&1 &
NODE_PID=$!
echo "  Started with PID $NODE_PID"

# Wait for frontend to be ready
if ! wait_for_service $PORT "Node.js Frontend"; then
    echo "❌ Node.js frontend failed to start properly"
    echo "--- Frontend Log Output ---"
    cat logs/frontend.log 2>/dev/null || echo "No frontend log available"
    exit 1
fi

echo "🎉 Both services started successfully!"
echo "📡 API Backend: http://localhost:$API_PORT"
echo "🌐 Frontend: http://localhost:$PORT"

# Keep the script running and monitor processes
echo "🔍 Monitoring services..."
while true; do
    # Check if Python backend is still running
    if ! kill -0 $PYTHON_PID 2>/dev/null; then
        echo "❌ Python backend died, checking logs..."
        tail -n 10 logs/api.log 2>/dev/null || echo "No API log available"
        echo "🔄 Attempting to restart Python backend..."
        env API_PORT=$API_PORT python3 api/inventory_lookup.py > logs/api.log 2>&1 &
        PYTHON_PID=$!
        echo "  Restarted with PID $PYTHON_PID"
    fi
    
    # Check if Node.js frontend is still running
    if ! kill -0 $NODE_PID 2>/dev/null; then
        echo "❌ Node.js frontend died, checking logs..."
        tail -n 10 logs/frontend.log 2>/dev/null || echo "No frontend log available"
        echo "🔄 Attempting to restart Node.js frontend..."
        env PORT=$PORT npm start > logs/frontend.log 2>&1 &
        NODE_PID=$!
        echo "  Restarted with PID $NODE_PID"
    fi
    
    # Log status every 10 minutes
    echo "📊 Services status - Python PID: $PYTHON_PID, Node PID: $NODE_PID ($(date))"
    
    sleep 600  # Check every 10 minutes
done