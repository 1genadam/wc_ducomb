# Network Connectivity Troubleshooting Guide
## WC Ducomb Inventory System - IBM i Connection Issues

### Date: August 8, 2025
### Issue: Fly.io application unable to connect to IBM i system after outbound IP change

---

## Executive Summary

The WC Ducomb inventory system running on Fly.io lost connectivity to the IBM i system (AS/400) when Fly.io's outbound IP address changed from `69.31.3.73` to `69.31.3.78`. The root cause was identified as IP-based source filtering in the ASUS router's port forwarding configuration, combined with an outdated WAN IP address in the application configuration.

## Key Discoveries

### 1. Fly.io Networking Architecture
- **Inbound IP**: `66.241.125.125` (what users use to reach the app)
- **Outbound IP**: `69.31.3.78` (what external services see when the app makes connections)
- **Important**: Fly.io uses DIFFERENT IPs for inbound vs outbound traffic
- **Warning**: Fly.io outbound IPs are NOT stable and can change when instances are recreated

### 2. Network Topology
```
Internet → ASUS Router (216.176.21.86) → IBM i System (10.0.0.7)
         ↑
    Fly.io App (69.31.3.78)
```

### 3. IP Address Changes Discovered
- **Old WAN IP**: `66.230.69.194` (no longer valid)
- **Current WAN IP**: `216.176.21.86` (actual router WAN IP)
- **Old Fly.io Outbound**: `69.31.3.73`
- **New Fly.io Outbound**: `69.31.3.78`

---

## Terminal-Specific Command Sequences

### Terminal 1: Local Mac (Your Computer)
```bash
# Test connection to old IP (this will timeout)
robertsher@MacBookPro ~ % telnet 66.230.69.194 23
# Result: Timeout - IP no longer valid

# Test connection to current router IP (WORKS after fix)
robertsher@MacBookPro ~ % telnet 216.176.21.86 23
# Result: Connected! Shows IBM i login screen

# After security hardening with custom port (should FAIL from Mac)
robertsher@MacBookPro ~ % telnet 216.176.21.86 52323
# Result: Connection refused (good - security working)

# Test internal connection (only works on local network)
robertsher@MacBookPro ~ % telnet 10.0.0.7 23
# Result: Connected if on local network

# Test Fly.io app health
robertsher@MacBookPro ~ % curl https://wc-ducomb.fly.dev/api/inventory/health
# Result: {"ibm_connection": false} before fix, true after

# Check Fly.io configuration
robertsher@MacBookPro ~ % flyctl ips list -a wc-ducomb
# Result: Shows 66.241.125.125 (inbound only)

# Connect to Fly.io container
robertsher@MacBookPro ~ % flyctl ssh console -a wc-ducomb
```

### Terminal 2: Inside Fly.io Container
```bash
# After running: flyctl ssh console -a wc-ducomb
root@185e777a160128:/app# 

# Check outbound IPv4 address
root@185e777a160128:/app# curl -4 ifconfig.me
# Result: 69.31.3.78

# Check IPv6 address (if curious)
root@185e777a160128:/app# curl ifconfig.me
# Result: 2605:4c40:118:603b:0:d6e2:3f4:1

# Check environment variables
root@185e777a160128:/app# echo $IBM_HOST
216.176.21.86
root@185e777a160128:/app# echo $IBM_PORT
52323

# Install telnet for testing (may fail due to memory)
root@185e777a160128:/app# apt-get update && apt-get install -y telnet

# Alternative: Test with Python
root@185e777a160128:/app# python3 -c "import socket; s=socket.socket(); s.settimeout(5); s.connect(('216.176.21.86', 52323)); print('Connected!'); s.close()"

# Check app code for hardcoded ports
root@185e777a160128:/app# grep -r "port\|23\|5250" api/

# Exit container
root@185e777a160128:/app# exit
```

### Terminal 3: ASUS Router SSH Session
```bash
# Connect to router (from Mac terminal)
robertsher@MacBookPro ~ % ssh -p 1024 sducomb@10.0.0.1
# Enter password when prompted

# Once connected:
sducomb@wcd_router:/tmp/home/root# 

# Check router's WAN IP
sducomb@wcd_router:/tmp/home/root# ip addr show eth0 | grep inet
# Result: inet 216.176.21.86/30

# View all NAT rules
sducomb@wcd_router:/tmp/home/root# iptables -t nat -L -n -v

# View port forwarding rules specifically
sducomb@wcd_router:/tmp/home/root# iptables -t nat -L VSERVER -n -v --line-numbers
# Should show:
# DNAT tcp -- * * 69.31.3.78 0.0.0.0/0 tcp dpt:52323 to:10.0.0.7

# Check if packets are hitting rules (clear counters first)
sducomb@wcd_router:/tmp/home/root# iptables -t nat -Z VSERVER
# Then test connection from Fly.io, then check counters again:
sducomb@wcd_router:/tmp/home/root# iptables -t nat -L VSERVER -n -v --line-numbers

# Exit router SSH
sducomb@wcd_router:/tmp/home/root# exit
```

### Terminal 4: IBM i Green Screen (via telnet)
```bash
# Connect from Mac (works when Source IP unrestricted)
robertsher@MacBookPro ~ % telnet 216.176.21.86 23
# OR with custom port
robertsher@MacBookPro ~ % telnet 216.176.21.86 52323

# You'll see:
Connected to 216.176.21.86.
Escape character is '^]'.

                      **             Sign On             ** 
                                               System  . . . . . :   S7891490 
                                               Subsystem . . . . :   QINTER     
                                               Display . . . . . :   QPADEV0024 

# Exit telnet session: Ctrl+] then type 'quit'
```

---

## The Solution (Complete Process)

### Phase 1: Initial Fix (Wide Open - INSECURE)
Via ASUS Router Web Interface:

1. **Navigate to Port Forwarding**:
   - Go to: WAN → Virtual Server / Port Forwarding
   - Find the ISERIES rule (Port 23)

2. **Remove Source IP Restriction**:
   - Click Edit (pencil icon) on ISERIES row
   - **Clear the Source IP field** (was: 69.31.3.78, now: empty)
   - Click OK, then Apply

3. **Update Fly.io Application**:
```bash
flyctl secrets set IBM_HOST=216.176.21.86 -a wc-ducomb
flyctl apps restart wc-ducomb
```

### Phase 2: Security Hardening (RECOMMENDED)
After confirming connectivity works:

1. **Change to Non-Standard Port**:
   - Edit ISERIES rule again
   - Change External Port: 52323 (or any high port)
   - Add Source IP: 69.31.3.78 (Fly.io only)
   - Internal Port: leave blank (will use 23)
   - Click OK, then Apply

2. **Update Fly.io Environment**:
```bash
flyctl secrets set IBM_PORT=52323 -a wc-ducomb
flyctl apps restart wc-ducomb
```

3. **Update Application Code** (if hardcoded):
   - The app must use IBM_PORT environment variable
   - Or construct connection as: `${IBM_HOST}:${IBM_PORT}`

---

## Current Issues & Solutions

### Problem: App Still Using Port 23
**Symptom**: After setting IBM_PORT=52323, health check shows `"ibm_connection": false`

**Root Cause**: Application code is hardcoded to use port 23

**Solution Required**:
1. Update application code to read IBM_PORT environment variable
2. Modify connection string in the code from:
   - `telnet ${IBM_HOST} 23` 
   - To: `telnet ${IBM_HOST} ${IBM_PORT}`

**Files to Check**:
```bash
# In Fly.io container
grep -r "23\|port" /app/api/
cat /app/api/inventory_lookup.py
```

### Temporary Workaround Options:

**Option 1: Keep Port 23 (Less Secure)**
- Change router back to External Port: 23
- Keep Source IP: 69.31.3.78
- Accept the lower security of standard port

**Option 2: Port in Host Variable**
```bash
flyctl secrets set IBM_HOST=216.176.21.86:52323 -a wc-ducomb
```
Only works if app parses host:port format

**Option 3: Fix the Code**
The proper solution - update the application to use IBM_PORT variable

---

## Security Considerations

### Current Configuration (Secure)
- **External Port**: 52323 (non-standard, harder to find)
- **Source IP**: 69.31.3.78 (only Fly.io can connect)
- **Internal Port**: 23 (IBM i telnet)

### Risks with Current Setup
1. If Fly.io IP changes, connection breaks
2. Telnet is unencrypted (credentials sent in plain text)
3. Single IP restriction is fragile

### Better Long-term Solutions
1. **VPN Connection**: Most secure, encrypted tunnel
2. **SSH Tunneling**: Encrypted, key-based authentication
3. **API Gateway**: HTTPS frontend with authentication
4. **Stable Proxy**: Use a fixed-IP proxy service

---

## Quick Reference

### Key IP Addresses:
```
Router WAN IP:        216.176.21.86
Router LAN IP:        10.0.0.1
IBM i Internal IP:    10.0.0.7
Fly.io Inbound IP:    66.241.125.125
Fly.io Outbound IP:   69.31.3.78 (can change!)
Custom Telnet Port:   52323 (was 23)
Old WAN IP (dead):    66.230.69.194
```

### Test Commands:
```bash
# Test IBM i from anywhere (when unrestricted)
telnet 216.176.21.86 52323

# Test from Fly.io
curl https://wc-ducomb.fly.dev/api/inventory/health

# SSH to router
ssh -p 1024 sducomb@10.0.0.1

# SSH to Fly.io
flyctl ssh console -a wc-ducomb

# Update Fly.io secrets
flyctl secrets set IBM_HOST=216.176.21.86 -a wc-ducomb
flyctl secrets set IBM_PORT=52323 -a wc-ducomb
flyctl apps restart wc-ducomb
```

### Router iptables Commands:
```bash
# View all NAT rules
iptables -t nat -L -n -v

# View port forwarding rules
iptables -t nat -L VSERVER -n -v --line-numbers

# Clear packet counters
iptables -t nat -Z VSERVER

# Check router's WAN IP
ip addr show eth0 | grep inet

# Add temporary rule (for testing)
iptables -t nat -I VSERVER 5 -p tcp --dport 52323 -j DNAT --to-destination 10.0.0.7:23

# Remove temporary rule
iptables -t nat -D VSERVER 5
```

---

## Troubleshooting Checklist

When IBM i connection fails:

1. **Check Fly.io Outbound IP**:
```bash
flyctl ssh console -a wc-ducomb -C 'curl -4 ifconfig.me'
```

2. **Check Router WAN IP**:
```bash
ssh -p 1024 sducomb@10.0.0.1 'ip addr show eth0 | grep inet'
```

3. **Verify Port Forwarding Rule**:
   - WAN → Virtual Server / Port Forwarding
   - Check External Port, Source IP, Internal IP

4. **Test Connection Path**:
```bash
# From Mac (should fail with Source IP restriction)
telnet [ROUTER_WAN_IP] [PORT]

# From Fly.io container
python3 -c "import socket; s=socket.socket(); s.settimeout(5); s.connect(('[ROUTER_WAN_IP]', [PORT])); print('Connected!'); s.close()"
```

5. **Check Environment Variables**:
```bash
flyctl ssh console -a wc-ducomb
echo $IBM_HOST
echo $IBM_PORT
```

6. **Review Application Logs**:
```bash
flyctl logs -a wc-ducomb
```

---

## Lessons Learned

1. **Document ALL IP addresses and ports in use**
2. **Fly.io IPs are unstable** - plan for changes
3. **Security vs Convenience tradeoff** - restricted IPs break when providers change
4. **Application should use environment variables** - never hardcode IPs or ports
5. **Test from multiple locations** - local, external, and from the actual app
6. **Router shows source/destination differently** - understand NAT rules
7. **Keep security in mind** - don't leave ports wide open

---

## Contact Information

- **Router Admin**: sducomb
- **Router SSH Port**: 1024
- **IBM i System**: 10.0.0.7 (WCDUCOMB)
- **System Name**: S7891490
- **Fly.io App**: wc-ducomb.fly.dev
- **GitHub Repo**: 1genadam/wc_ducomb

---

*Document created: August 8, 2025*
*Last updated: August 8, 2025 - Added security hardening with custom port 52323 and troubleshooting for hardcoded port issue*