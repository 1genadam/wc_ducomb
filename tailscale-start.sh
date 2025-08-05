#!/bin/bash

echo "🔐 Starting WC Ducomb with Tailscale VPN..."

# Start Tailscale daemon
tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &
sleep 2

# Authenticate with Tailscale
if [ -n "$TAILSCALE_AUTHKEY" ]; then
    echo "🔑 Connecting to Tailscale network..."
    tailscale up --authkey=$TAILSCALE_AUTHKEY --accept-routes
    
    # Wait for connection
    echo "⏳ Waiting for Tailscale connection..."
    for i in {1..30}; do
        if tailscale status | grep -q "logged in"; then
            echo "✅ Tailscale connected successfully!"
            tailscale ip -4
            break
        fi
        sleep 1
    done
else
    echo "❌ TAILSCALE_AUTHKEY environment variable not set"
    exit 1
fi

# Test IBM i connectivity through Tailscale
echo "🔍 Testing IBM i connectivity..."
TAILSCALE_IP=$(tailscale ip -4 | head -n 1)
echo "Tailscale IP: $TAILSCALE_IP"

# Test route to IBM i network
echo "Testing route to IBM i network..."
if tailscale ping --c 1 10.0.0.7 2>/dev/null; then
    echo "✅ IBM i system reachable via Tailscale"
else
    echo "⚠️ IBM i not responding to ping - checking subnet routes..."
    tailscale status --peers
fi

# Update IBM i host in environment for the Python app
export IBM_HOST="10.0.0.7"  # This will now route through Tailscale
echo "IBM i system configured at: $IBM_HOST"

# Test 5250 port connectivity
echo "Testing 5250 port connectivity..."
timeout 5 python3 -c "
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    result = s.connect_ex(('10.0.0.7', 23))
    if result == 0:
        print('✅ Port 23 (5250) is accessible')
    else:
        print(f'❌ Port 23 connection failed: {result}')
    s.close()
except Exception as e:
    print(f'❌ Connection test failed: {e}')
" || echo "❌ Connection test timed out"

# Start services
echo "🚀 Starting application services..."
mkdir -p logs

# Start Python API backend
echo "🐍 Starting Python API backend on port 5001..."
export API_PORT=5001
python3 api/inventory_lookup.py > logs/api.log 2>&1 &
PYTHON_PID=$!

# Wait for Python API to start
sleep 10

# Start Node.js frontend server
echo "🌐 Starting Node.js frontend server on port 3000..."
export PORT=3000
npm start > logs/frontend.log 2>&1 &
NODE_PID=$!

# Set up signal handlers for graceful shutdown
cleanup() {
    echo "🛑 Shutting down services..."
    kill $PYTHON_PID $NODE_PID 2>/dev/null || true
    tailscale down 2>/dev/null || true
    exit 0
}

trap cleanup SIGTERM SIGINT

# Keep running and monitor processes
while true; do
    if ! kill -0 $PYTHON_PID 2>/dev/null; then
        echo "❌ Python API died, restarting..."
        python3 api/inventory_lookup.py > logs/api.log 2>&1 &
        PYTHON_PID=$!
    fi
    
    if ! kill -0 $NODE_PID 2>/dev/null; then
        echo "❌ Node.js frontend died, restarting..."
        npm start > logs/frontend.log 2>&1 &
        NODE_PID=$!
    fi
    
    sleep 30
done