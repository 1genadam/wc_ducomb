# Tailscale VPN Setup for IBM i Access

## Overview
Tailscale provides zero-config VPN that will allow your Fly.io application to securely access your IBM i system at 10.0.0.7:23.

## Step 1: Local Network Setup

### Install Tailscale on a machine in your local network:

```bash
# macOS
brew install tailscale

# Ubuntu/Debian
curl -fsSL https://tailscale.com/install.sh | sh

# Windows
# Download from https://tailscale.com/download
```

### Start Tailscale and authenticate:
```bash
sudo tailscale up
# Follow the authentication URL that appears
```

### Enable subnet routing for your local network:
```bash
sudo tailscale up --advertise-routes=10.0.0.0/24 --accept-routes
```

### Note your Tailscale IP:
```bash
tailscale ip -4
# Example output: 100.64.0.1
```

## Step 2: Fly.io Integration

### Get Tailscale Auth Key:
1. Go to https://login.tailscale.com/admin/settings/keys
2. Generate a new auth key with these settings:
   - Reusable: Yes
   - Ephemeral: Yes (for containers)
   - Pre-authorized: Yes

### Add to Fly.io secrets:
```bash
flyctl secrets set TAILSCALE_AUTHKEY="tskey-auth-your-key-here" -a wc-ducomb
```

## Step 3: Update IBM i IP Address

Your IBM i system will be accessible via the Tailscale gateway IP instead of 10.0.0.7.

The new connection path will be:
- Fly.io App → Tailscale VPN → Your Local Gateway → 10.0.0.7:23

## Security Benefits
- End-to-end encryption
- Zero-config networking
- Access logs and monitoring
- Device identity verification
- Automatic key rotation