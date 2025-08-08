# Local Gateway Setup for IBM i Access

## Overview
This guide sets up a local machine as a Tailscale gateway to route traffic from Fly.io to your IBM i system at 10.0.0.7:23.

## Prerequisites
- Machine on same network as IBM i system (10.0.0.0/24)
- Administrative access to install Tailscale
- IBM i system accessible at 10.0.0.7:23

## Step 1: Install Tailscale on Local Gateway

### macOS
```bash
brew install tailscale
```

### Ubuntu/Debian
```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

### Windows
Download from https://tailscale.com/download

## Step 2: Configure Tailscale Account

1. **Create Tailscale Account**
   - Visit https://tailscale.com
   - Sign up with your preferred method (Google, Microsoft, etc.)

2. **Generate Auth Key for Fly.io**
   - Go to https://login.tailscale.com/admin/settings/keys
   - Click "Generate auth key"
   - Settings:
     - ✅ Reusable
     - ✅ Ephemeral (for containers)
     - ✅ Pre-authorized
     - Tags: Add `tag:server` (optional)
   - **SAVE THIS KEY** - you'll need it for Fly.io

## Step 3: Setup Local Gateway

### Start Tailscale with Subnet Routing
```bash
# Initial connection (follow auth URL that appears)
sudo tailscale up

# Enable subnet routing for your local network
sudo tailscale up --advertise-routes=10.0.0.0/24 --accept-routes
```

### Verify Gateway Status
```bash
# Check your Tailscale IP
tailscale ip -4

# Check status
tailscale status

# Test IBM i connectivity locally
nc -z 10.0.0.7 23 && echo "IBM i reachable" || echo "IBM i not reachable"
```

## Step 4: Approve Subnet Routes

1. Go to https://login.tailscale.com/admin/machines
2. Find your local gateway machine
3. Click on it
4. In the "Subnet routes" section, click **Enable** for `10.0.0.0/24`

## Step 5: Configure Fly.io Deployment

### Set Tailscale Auth Key
```bash
flyctl secrets set TAILSCALE_AUTHKEY="tskey-auth-YOUR-KEY-HERE" -a wc-ducomb
```

### Deploy with Tailscale
```bash
# Copy Tailscale Dockerfile
cp Dockerfile.tailscale Dockerfile

# Deploy
flyctl deploy -a wc-ducomb
```

## Step 6: Verify VPN Connectivity

### Check Fly.io Container
```bash
# SSH into container
flyctl ssh console -a wc-ducomb

# Check Tailscale status
tailscale status

# Test IBM i connectivity
python3 -c "
import socket
s = socket.socket()
s.settimeout(5)
result = s.connect_ex(('10.0.0.7', 23))
print('SUCCESS' if result == 0 else f'FAILED: {result}')
s.close()
"
```

## Troubleshooting

### Gateway Not Advertising Routes
```bash
# Check if routes are advertised
tailscale status --self

# Re-enable with force
sudo tailscale up --advertise-routes=10.0.0.0/24 --accept-routes --reset
```

### Firewall Issues
```bash
# Check if local firewall is blocking
sudo ufw status  # Ubuntu
pfctl -sr         # macOS

# Temporarily disable for testing
sudo ufw disable  # Ubuntu (re-enable with: sudo ufw enable)
```

### IBM i Not Responding
```bash
# Test from gateway machine
telnet 10.0.0.7 23

# Check if IBM i accepts external connections
# May need to configure IBM i network settings
```

## Network Topology
```
Fly.io Container → Tailscale VPN → Local Gateway → 10.0.0.0/24 → IBM i (10.0.0.7:23)
```

## Security Notes
- Tailscale uses WireGuard for encryption
- Only authorized devices can join your network
- Subnet routes must be explicitly approved
- All traffic is logged and auditable

## Expected Results
Once setup is complete:
- Fly.io container gets Tailscale IP (100.x.x.x range)
- Container can reach 10.0.0.7:23 through VPN tunnel
- 5250 protocol automation works from cloud deployment