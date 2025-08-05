#!/bin/bash

# SSH Tunnel Alternative (simpler but less secure)
# Run this in your Fly.io container

# Create SSH tunnel to local gateway
ssh -N -L 5250:10.0.0.7:23 user@your-public-ip &

# Your application can now connect to localhost:5250
# which will be forwarded to 10.0.0.7:23

# For persistent connection, use autossh:
# autossh -M 20000 -N -L 5250:10.0.0.7:23 user@your-public-ip

echo "SSH tunnel established. Connect to localhost:5250"