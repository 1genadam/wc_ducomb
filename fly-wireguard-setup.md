# Fly.io WireGuard VPN Setup (Easiest Solution)

## Overview
Fly.io has built-in WireGuard support that makes this extremely simple. No Docker modifications needed!

## Step 1: Install Fly.io WireGuard on Your Local Network

### On your local machine/server:
```bash
# Install WireGuard peer for your Fly.io organization
flyctl wireguard create personal wc-ducomb-gateway

# This will output a configuration file
# Example: ~/.fly/flyctl_wg_personal_wc-ducomb-gateway.conf
```

### Start the WireGuard connection:
```bash
# macOS/Linux
sudo wg-quick up ~/.fly/flyctl_wg_personal_wc-ducomb-gateway.conf

# Or use Fly.io's helper
flyctl wireguard websockets enable
```

## Step 2: Configure Your Network

### Enable IP Forwarding (on your local gateway):
```bash
# Temporary
sudo sysctl -w net.ipv4.ip_forward=1

# Permanent (add to /etc/sysctl.conf)
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf
```

### Set up routing to IBM i system:
```bash
# Add route for your local network through the WireGuard interface
sudo ip route add 10.0.0.0/24 dev wg-flyio
```

## Step 3: Update IBM i Host Configuration

No Docker changes needed! Just update the IBM i host in your Fly.io app:

```bash
# Set the IBM i host to use Fly.io's internal network
flyctl secrets set IBM_HOST="fdaa:c:91cc:a7b:YOUR_FLY_NETWORK_IP" -a wc-ducomb
```

## Step 4: Test the Connection

```bash
# From your Fly.io app, test connectivity
flyctl ssh console -a wc-ducomb
# Inside the container:
nc -z 10.0.0.7 23
```

## Advantages
- ✅ No Docker modifications required
- ✅ Built into Fly.io platform
- ✅ Automatic encryption and authentication  
- ✅ No additional services to manage
- ✅ Works with existing deployment

## Network Flow
```
Internet → Fly.io App → Fly.io WireGuard → Your Local Gateway → IBM i (10.0.0.7:23)
```

This is the **recommended approach** as it requires minimal changes to your existing setup.