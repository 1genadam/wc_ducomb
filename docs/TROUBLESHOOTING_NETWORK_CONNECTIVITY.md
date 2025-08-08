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

## Troubleshooting Steps Performed

### Step 1: Verify Network Connectivity
```bash
# Test from local network
telnet 10.0.0.7 23  # Works - IBM i is accessible internally

# Test from Fly.io
curl https://wc-ducomb.fly.dev/api/inventory/health
# Result: {"ibm_connection": false}
```

### Step 2: Check Fly.io IP Addresses
```bash
# Check what IPs Fly.io is using
flyctl ips list -a wc_ducomb
# Shows: 66.241.125.125 (inbound only)

# SSH into Fly.io container
flyctl ssh console -a wc_ducomb

# Check actual outbound IP
curl -4 ifconfig.me
# Result: 69.31.3.78
```

### Step 3: Investigate IBM i Configuration

Searched extensively on IBM i system but found NO IP filtering configured there:

#### Commands Used on IBM i:
```
WRKTCPSTS         # Work with TCP/IP Status
CFGTCP            # Configure TCP/IP
GO TCPADM         # TCP/IP Administration menu
WRKREGINF         # Work with Registration Information
WRKTCPPTKR        # (Command not found - packet rules not available)
```

#### Checked IBM i Components:
- TCP/IP configuration
- TELNET server settings (CHGTELSVR)
- Exit programs (QIBM_QTG_DEVINIT, QIBM_QTG_DEVTERM)
- System values (QRMTSIGN)
- Data areas in AKTSUPPORT library
- Startup programs (WCOSTRUP)

**Result**: No IP filtering found on IBM i system

### Step 4: Investigate ASUS Router Configuration

#### SSH Access to Router:
```bash
# Enable SSH in router (Admin → System → Service)
# SSH Port: 1024, Allow Password Login: Yes

# Connect to router
ssh -p 1024 sducomb@10.0.0.1
```

#### Key iptables Discovery:
```bash
# Check NAT rules
iptables -t nat -L VSERVER -n -v --line-numbers

# Found:
Chain VSERVER (1 references)
num   pkts bytes target     prot opt in     out     source               destination
1        0     0 DNAT       tcp  --  *      *       66.230.69.194        0.0.0.0/0            tcp dpt:4433 to:10.0.0.7:4433
4        0     0 DNAT       tcp  --  *      *       69.31.3.78           0.0.0.0/0            tcp dpt:23 to:10.0.0.7
```

The rule shows port 23 is restricted to connections FROM source IP `69.31.3.78` only!

### Step 5: Check Router WAN IP
```bash
# On router
ip addr show eth0
# Result: inet 216.176.21.86/30

# The WAN IP had changed from 66.230.69.194 to 216.176.21.86!
```

---

## The Solution

### Problem Identified:
The ASUS router's port forwarding rule for port 23 (ISERIES) had a **Source IP restriction** set to the old Fly.io IP (`69.31.3.73`), which had been automatically updated to `69.31.3.78` but still restricted connections to only that specific IP.

### Fix Applied:

1. **Navigate to Router Port Forwarding**:
   - Go to: WAN → Virtual Server / Port Forwarding
   - Find the ISERIES rule (Port 23)

2. **Edit the Rule**:
   - Click Edit (pencil icon) on ISERIES row
   - **Clear the Source IP field** (was: 69.31.3.78, now: empty)
   - Leave other settings:
     - External Port: 23
     - Internal Port: (blank/auto)
     - Internal IP Address: 10.0.0.7
     - Protocol: TCP

3. **Apply Changes**:
   - Click OK
   - Click Apply

### Result:
- Port 23 now accepts connections from ANY IP address
- Prevents future issues when Fly.io's IP changes
- Allows testing from any location

---

## Application Configuration Updates Required

### Update IBM i Host Address:
The application needs to be updated to use the correct WAN IP:
- **Old**: `66.230.69.194` (no longer valid)
- **New**: `216.176.21.86` (current router WAN IP)

### Environment Variables to Update:
Check and update these in your Fly.io configuration:
```bash
flyctl secrets list -a wc_ducomb
# Update any that reference the old IP
flyctl secrets set IBM_HOST=216.176.21.86 -a wc_ducomb
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
- Administration → System (for SSH access)
- System Log (for connection attempts)

### 4. Troubleshooting Tools

#### From Mac/Linux:
```bash
telnet <ip> <port>           # Test TCP connectivity
nc -zv <ip> <port>           # Test port connectivity
curl -v telnet://<ip>:<port> # Test with timeout
```

#### From Router (via SSH):
```bash
iptables -L -n -v            # List all firewall rules
iptables -t nat -L -n -v     # List NAT/port forwarding rules
ip addr show                 # Show all IP addresses
```

#### From Fly.io:
```bash
flyctl ssh console -a <app-name>
curl -4 ifconfig.me          # Check IPv4 address
curl ifconfig.me             # Check IPv6 address
```

---

## Preventive Measures

### 1. Remove Source IP Restrictions
Unless absolutely necessary for security, don't restrict port forwarding rules to specific source IPs.

### 2. Use Dynamic DNS
Set up DDNS to handle WAN IP changes:
- Configure in router: WAN → DDNS
- Use the DDNS hostname instead of IP in applications

### 3. Monitor Connectivity
Add monitoring to detect connection failures:
```javascript
// In your application
setInterval(async () => {
  const health = await checkIBMConnection();
  if (!health) {
    console.error('IBM i connection lost');
    // Send alert
  }
}, 60000); // Check every minute
```

### 4. Document Network Configuration
Maintain a network diagram showing:
- All IP addresses (internal and external)
- Port forwarding rules
- Firewall rules
- Which components can change

---

## Quick Reference Commands

### Test IBM i Connection:
```bash
# From anywhere
telnet 216.176.21.86 23

# From Fly.io app
curl https://wc-ducomb.fly.dev/api/inventory/health
```

### Access Router:
```bash
# Web interface
http://10.0.0.1

# SSH
ssh -p 1024 sducomb@10.0.0.1
```

### Check Current IPs:
```bash
# Router WAN IP
ssh -p 1024 sducomb@10.0.0.1 'ip addr show eth0'

# Fly.io outbound IP
flyctl ssh console -a wc_ducomb -C 'curl -4 ifconfig.me'
```

---

## Contact Information

- **Router Admin**: sducomb
- **IBM i System**: 10.0.0.7 (WCDUCOMB)
- **Fly.io App**: wc-ducomb.fly.dev

---

*Document created: August 8, 2025*
*Last updated: August 8, 2025*