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

# Test internal connection (only works on local network)
robertsher@MacBookPro ~ % telnet 10.0.0.7 23
# Result: Connected if on local network

# Test Fly.io app health
robertsher@MacBookPro ~ % curl https://wc-ducomb.fly.dev/api/inventory/health
# Result: {"ibm_connection": false} before fix, true after

# Check Fly.io configuration
robertsher@MacBookPro ~ % flyctl ips list -a wc_ducomb
# Result: Shows 66.241.125.125 (inbound only)

# Connect to Fly.io container
robertsher@MacBookPro ~ % flyctl ssh console -a wc_ducomb
```

### Terminal 2: Inside Fly.io Container
```bash
# After running: flyctl ssh console -a wc_ducomb
root@185e777a160128:/app# 

# Check outbound IPv4 address
root@185e777a160128:/app# curl -4 ifconfig.me
# Result: 69.31.3.78

# Check IPv6 address (if curious)
root@185e777a160128:/app# curl ifconfig.me
# Result: 2605:4c40:118:603b:0:d6e2:3f4:1

# Install telnet for testing (if needed)
root@185e777a160128:/app# apt-get update && apt-get install -y telnet

# Test connection to IBM i (after updating to correct IP)
root@185e777a160128:/app# telnet 216.176.21.86 23
# Should connect after fix

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

# Check if packets are hitting rules (clear counters first)
sducomb@wcd_router:/tmp/home/root# iptables -t nat -Z VSERVER
# Then test connection from Mac, then check counters again:
sducomb@wcd_router:/tmp/home/root# iptables -t nat -L VSERVER -n -v --line-numbers

# Exit router SSH
sducomb@wcd_router:/tmp/home/root# exit
```

### Terminal 4: IBM i Green Screen (via telnet)
```bash
# Connect from Mac
robertsher@MacBookPro ~ % telnet 216.176.21.86 23

# You'll see:
Connected to 216.176.21.86.
Escape character is '^]'.

                      **             Sign On             ** 
                                               System  . . . . . :   S7891490 
                                               Subsystem . . . . :   QINTER     
                                               Display . . . . . :   QPADEV0024 

# IBM i Commands used during investigation:
WRKTCPSTS         # Work with TCP/IP Status
CFGTCP            # Configure TCP/IP  
GO TCPADM         # TCP/IP Administration menu
WRKREGINF         # Work with Registration Information
WRKMBRPDM FILE(QGPL/QCLSRC)  # Check startup programs
WRKOBJ *ALL/IP* *FILE         # Search for IP-related files
WRKOBJ *ALL/IP* *DTAARA       # Search for IP-related data areas
DSPDTAARA DTAARA(AKTSUPPORT/REMOTIP)  # Display data area contents

# Exit telnet session: Ctrl+] then type 'quit'
```

---

## Troubleshooting Steps Performed (Detailed)

### Step 1: Initial Problem Discovery
```bash
# FROM MAC TERMINAL:
robertsher@MacBookPro ~ % curl https://wc-ducomb.fly.dev/api/inventory/health
{"services":{"ibm_connection":false,"p5250":true,"redis":false},"status":"healthy"}
# Problem confirmed: ibm_connection is false
```

### Step 2: Check Fly.io Configuration
```bash
# FROM MAC TERMINAL:
robertsher@MacBookPro ~ % flyctl ssh console -a wc_ducomb
Connecting to fdaa:c:91cc:a7b:1cb:d6e2:3f4:2... complete

# NOW IN FLY.IO CONTAINER:
root@185e777a160128:/app# curl -4 ifconfig.me
69.31.3.78
# This is the NEW outbound IP (was 69.31.3.73)
```

### Step 3: Investigate Router Configuration
```bash
# FROM MAC TERMINAL:
robertsher@MacBookPro ~ % ssh -p 1024 sducomb@10.0.0.1

# NOW IN ROUTER:
sducomb@wcd_router:/tmp/home/root# iptables -t nat -L VSERVER -n -v --line-numbers
Chain VSERVER (1 references)
num   pkts bytes target     prot opt in     out     source               destination
4        0     0 DNAT       tcp  --  *      *       69.31.3.78           0.0.0.0/0            tcp dpt:23 to:10.0.0.7
# Found the rule! It only accepts from 69.31.3.78

sducomb@wcd_router:/tmp/home/root# ip addr show eth0 | grep inet
    inet 216.176.21.86/30 brd 216.176.21.87 scope global eth0
# Router WAN IP is 216.176.21.86, NOT 66.230.69.194!
```

---

## The Solution (Step-by-Step)

### Via ASUS Router Web Interface:

1. **Access Router Web Interface**:
   - Open browser to: http://10.0.0.1
   - Login with credentials

2. **Navigate to Port Forwarding**:
   - Click: WAN → Virtual Server / Port Forwarding
   - Find the ISERIES rule (Port 23)
   - Note the Source IP field shows: 69.31.3.78

3. **Edit the Rule**:
   - Click Edit (pencil icon) on ISERIES row
   - **Clear the Source IP field completely** (delete 69.31.3.78)
   - Leave all other settings:
     - Service Name: ISERIES
     - Protocol: TCP
     - External Port: 23
     - Internal Port: (leave blank)
     - Internal IP Address: 10.0.0.7

4. **Save Changes**:
   - Click OK in the dialog
   - Click Apply on the main page
   - Wait for router to apply changes

5. **Verify Fix**:
```bash
# FROM MAC TERMINAL:
robertsher@MacBookPro ~ % telnet 216.176.21.86 23
Trying 216.176.21.86...
Connected to 216.176.21.86.
# SUCCESS! IBM i login screen appears
```

---

## Application Updates Required

### Update Fly.io Environment Variables:
```bash
# FROM MAC TERMINAL:
# Check current secrets
robertsher@MacBookPro ~ % flyctl secrets list -a wc_ducomb

# Update IBM i host IP
robertsher@MacBookPro ~ % flyctl secrets set IBM_HOST=216.176.21.86 -a wc_ducomb

# Verify the change
robertsher@MacBookPro ~ % flyctl ssh console -a wc_ducomb
root@185e777a160128:/app# echo $IBM_HOST
216.176.21.86

# Test the connection
root@185e777a160128:/app# telnet $IBM_HOST 23
# Should connect successfully
```

### Update Application Code:
If the IP is hardcoded anywhere in the application, update it:
- Search for: `66.230.69.194`
- Replace with: `216.176.21.86`
- Or better: Use environment variable `$IBM_HOST`

---

## Verification Tests

### After applying the fix, run these tests:

```bash
# 1. FROM MAC - Test direct connection
robertsher@MacBookPro ~ % telnet 216.176.21.86 23
# Expected: Connected, shows IBM i login

# 2. FROM MAC - Test Fly.io health check
robertsher@MacBookPro ~ % curl https://wc-ducomb.fly.dev/api/inventory/health
# Expected: {"ibm_connection": true}

# 3. FROM MAC - Test inventory lookup
robertsher@MacBookPro ~ % curl -X POST https://wc-ducomb.fly.dev/api/inventory/lookup \
  -H "Content-Type: application/json" \
  -d '{"sku": "lov224006"}'
# Expected: Returns inventory data

# 4. FROM FLY.IO CONTAINER - Test connection
robertsher@MacBookPro ~ % flyctl ssh console -a wc_ducomb
root@185e777a160128:/app# telnet 216.176.21.86 23
# Expected: Connected to IBM i
```

---

## Lessons Learned

### 1. Document IP Dependencies
- Keep track of all IP addresses in the system
- Document which IPs can change and which are static
- Note the difference between inbound and outbound IPs

### 2. Avoid IP-Based Security When Possible
- IP restrictions are fragile with cloud providers
- Consider alternatives:
  - VPN connections
  - API keys/authentication
  - Stable proxy servers

### 3. Router Configuration Locations
Key places to check in ASUS routers:
- WAN → Virtual Server / Port Forwarding (for port rules)
- Firewall → General (for IP filtering)
- Administration → System → Service (for SSH access)
- System Log (for connection attempts)

### 4. Always Test From Multiple Locations
- Local network (proves IBM i is working)
- External network (proves port forwarding)
- From the actual application (proves end-to-end)

---

## Quick Reference

### Key IP Addresses:
```
Router WAN IP:        216.176.21.86
Router LAN IP:        10.0.0.1
IBM i Internal IP:    10.0.0.7
Fly.io Inbound IP:    66.241.125.125
Fly.io Outbound IP:   69.31.3.78 (can change!)
Old WAN IP (dead):    66.230.69.194
```

### Test Commands:
```bash
# Test IBM i from anywhere
telnet 216.176.21.86 23

# Test from Fly.io
curl https://wc-ducomb.fly.dev/api/inventory/health

# SSH to router
ssh -p 1024 sducomb@10.0.0.1

# SSH to Fly.io
flyctl ssh console -a wc_ducomb
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
```

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
*Last updated: August 8, 2025 - Added terminal-specific command sequences and verification tests*