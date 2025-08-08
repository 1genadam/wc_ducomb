# Tailscale Auth Key Setup Instructions

## Step 1: Create Tailscale Account and Auth Key

1. Go to https://tailscale.com and create a free account
2. Navigate to https://login.tailscale.com/admin/settings/keys
3. Click "Generate auth key" with these settings:
   - **Reusable**: Yes (allows multiple container deployments)
   - **Ephemeral**: Yes (devices auto-remove when disconnected)
   - **Pre-authorized**: Yes (no manual approval needed)
   - **Tags**: Leave empty or add "server"

## Step 2: Configure Fly.io Secrets

Once you have the auth key (starts with `tskey-auth-`), run:

```bash
flyctl secrets set TAILSCALE_AUTHKEY="your-auth-key-here" -a wc-ducomb
```

## Step 3: Set Up Local Gateway

On a machine in your local network (same network as 10.0.0.7):

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start and authenticate
sudo tailscale up --advertise-routes=10.0.0.0/24 --accept-routes

# Follow the authentication URL that appears
```

## Step 4: Deploy and Test

```bash
# Deploy the updated container
./deploy.sh

# Test the connection
flyctl ssh console -a wc-ducomb
# Inside container:
ping 10.0.0.7
nc -z 10.0.0.7 23
```

## Network Flow

```
Internet → Fly.io App → Tailscale VPN → Local Gateway → IBM i (10.0.0.7:23)
```