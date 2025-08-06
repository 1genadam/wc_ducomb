# Local Development Setup

## Quick Start

### Option 1: Simple Command
```bash
npm run local
```

### Option 2: Manual Start
```bash
./start-local.sh
```

## What This Does

The local development environment runs the **exact same code** as production:
- ✅ Same Node.js frontend server (port 3000)
- ✅ Same Python Flask API (port 5001)  
- ✅ Same 5250 protocol automation
- ✅ Same inventory chat widget
- ✅ Same admin panel

## Network Requirements

### On Office Network (10.0.0.0/24)
- ✅ **Full functionality** - Live inventory lookups from IBM i system
- ✅ All SKUs searchable (DGE037592, DGE037700, etc.)
- ✅ Real-time data from 10.0.0.7:23

### Remote Network  
- ⚠️ **Limited functionality** - Cannot reach IBM i system
- 💡 Connect to office network for full testing

## Development URLs

Once started, access:
- **Frontend**: http://localhost:2000
- **API**: http://localhost:5001
- **Health Check**: http://localhost:2000/health

### Chat Interfaces:
- **💬 Local Dev Chat**: http://localhost:2000/local (Enhanced dev interface)
- **📱 Widget Demo**: http://localhost:2000/inventory-chat-demo.html
- **📊 Admin Panel**: http://localhost:2000/admin.html

The **Local Dev Chat** provides the best development experience with:
- Real-time network status detection
- Quick test SKU buttons
- Matches production result formatting
- System status monitoring

## Testing

### Quick API Test
```bash
curl http://localhost:5001/api/lookup/DGE037592
```

### Integration Test
```bash
npm run test
```

### Live API Test (requires office network)
```bash
npm run test-api
```

## Stopping

Press `Ctrl+C` in the terminal running the local servers.

## Troubleshooting

### "Connection refused" errors
- Ensure you're on office network (10.0.0.0/24)
- Check if IBM i system (10.0.0.7:23) is accessible

### Port conflicts
- Default ports: 2000 (frontend), 5001 (API)
- Change with: `PORT=3001 API_PORT=5002 npm run local`

### Python/Node not found
```bash
npm run install-deps
```

## Production Deployment

This local setup is identical to production. When ready:
```bash
npm run deploy
```

The system will work the same way in production once the Tailscale VPN tunnel is configured.

## Documentation References

- **[Local Development Stabilization Guide](readme/local-development-stabilization.md)** - Complete technical details and improvements made
- **[Tailscale VPN Configuration](readme/tailscale-vpn-configuration.md)** - VPN setup for remote IBM i access
- **[Production Deployment Guide](readme/production-deployment-guide.md)** - Full production deployment instructions

## Recent Improvements (2025-08-06)

### ✅ Server Stability
- Replaced complex proxy architecture with simple direct API calls
- Eliminated frequent crashes and restart requirements
- Improved response times from 45+ seconds to 15-25 seconds
- Added automatic server health monitoring

### ✅ Enhanced Chat Interface  
- Real-time network status detection (Office vs Remote)
- Pre-loaded test SKUs for rapid development
- Better error handling and user feedback
- Production-identical result formatting

### ✅ Development Experience
- One-command startup with `npm run local`
- Automatic IBM i connectivity detection
- Clear troubleshooting guides and status monitoring
- Reliable local development environment