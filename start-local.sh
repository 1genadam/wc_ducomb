#!/bin/bash
# Local Development Server for WC Ducomb Inventory System
# This runs the exact same setup as production but locally

set -e

echo "🚀 Starting WC Ducomb Inventory System - Local Development"
echo "=================================================="

# Check if we're on the office network (10.0.0.0/24)
if ping -c 1 -W 1000 10.0.0.7 >/dev/null 2>&1; then
    echo "✅ Office network detected - IBM i system accessible"
    NETWORK_STATUS="OFFICE"
else
    echo "⚠️  Not on office network - IBM i system not accessible"
    echo "   Connect to office network for full functionality"
    NETWORK_STATUS="REMOTE"
fi

echo ""

# Set environment variables for local development
export PORT=2000
export API_PORT=5001
export API_BASE_URL="http://localhost:5001"
export FLASK_ENV=development
export FLASK_DEBUG=true

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    if [ ! -z "$PYTHON_PID" ]; then
        kill $PYTHON_PID 2>/dev/null || true
    fi
    if [ ! -z "$NODE_PID" ]; then
        kill $NODE_PID 2>/dev/null || true
    fi
    echo "✅ Cleanup complete"
    exit 0
}

# Trap cleanup on script exit
trap cleanup EXIT INT TERM

echo "🐍 Starting Python API server (port 5001)..."
cd api
python inventory_lookup.py &
PYTHON_PID=$!
cd ..

# Wait a moment for Python server to start
sleep 2

echo "🟢 Starting Node.js frontend server (port 2000)..."
node simple-server.js &
NODE_PID=$!

# Wait a moment for Node server to start
sleep 2

echo ""
echo "✅ Local development servers are running:"
echo "   📱 Frontend: http://localhost:2000"
echo "   🔧 API:      http://localhost:5001"
echo "   📊 Health:   http://localhost:2000/health"
echo ""
echo "🎯 Test URLs:"
echo "   • 💬 Local Chat:     http://localhost:2000/local"
echo "   • 📱 Chat Widget:    http://localhost:2000/inventory-chat-demo.html"
echo "   • 📊 Admin Panel:    http://localhost:2000/admin.html"
echo ""

if [ "$NETWORK_STATUS" = "OFFICE" ]; then
    echo "💡 Network Status: OFFICE - Full inventory lookups available"
    echo "   Try searching for: DGE037592, DGE037700, or any other SKU"
else
    echo "💡 Network Status: REMOTE - Limited functionality"
    echo "   Connect to office network (10.0.0.0/24) for live inventory data"
fi

echo ""
echo "Press Ctrl+C to stop all servers"
echo "=================================================="

# Keep script running and wait for user interrupt
wait