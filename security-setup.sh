#!/bin/bash

# Firewall rules for WireGuard server (local network)

# Allow WireGuard port
sudo ufw allow 51820/udp comment "WireGuard VPN"

# Allow forwarding from VPN to IBM i
sudo ufw route allow in on wg0 out on eth0 to 10.0.0.7 port 23 comment "VPN to IBM i 5250"

# Restrict VPN client access to only IBM i system
sudo iptables -I FORWARD -i wg0 -d 10.0.0.7 -p tcp --dport 23 -j ACCEPT
sudo iptables -I FORWARD -i wg0 -j DROP

# Log VPN connections
sudo iptables -I INPUT -p udp --dport 51820 -j LOG --log-prefix "WireGuard: "

# Save iptables rules (Ubuntu/Debian)
sudo iptables-save | sudo tee /etc/iptables/rules.v4

echo "Security rules applied successfully"