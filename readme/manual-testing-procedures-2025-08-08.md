# Manual Testing Procedures - Production System Validation

## 📅 **Document Date:** 2025-08-08
## 🎯 **Purpose:** Complete manual testing procedures for WC Ducomb Inventory System validation

---

## 🚀 **System Status Overview**

### **Current Production State**
- **Frontend**: ✅ Fully operational at https://wc-ducomb.fly.dev/
- **Backend API**: ✅ Healthy and responsive 
- **Architecture**: ✅ All components deployed and stable
- **Network**: ❌ IP `69.31.3.78` blocked by IBM i firewall
- **Action Required**: Update firewall to allow new outbound IP

### **IP Address Change Summary**
- **Previous Working IP**: `69.31.3.73` (confirmed working 2025-08-07)
- **Current Blocked IP**: `69.31.3.78` (needs firewall approval)
- **Root Cause**: Machine recreation during service stability improvements
- **Evidence**: Network connectivity test shows connection error 11 (blocked)

---

## 📋 **STEP-BY-STEP TESTING PROCEDURES**

### **Step 1: Update IBM i Firewall Configuration**
**⚠️ PREREQUISITE ACTION REQUIRED**

**Firewall Rule Update:**
```
REMOVE: 69.31.3.73 (old working IP)
ADD:    69.31.3.78 (new outbound IP from Fly.io)
```

**Network Details:**
- **Target System**: IBM i at 10.0.0.7:23
- **Protocol**: TCP (5250/Telnet)
- **Direction**: Inbound to IBM i from Fly.io cloud
- **Fly.io Inbound IP**: 66.241.125.125 (unchanged)
- **Fly.io Outbound IP**: 69.31.3.78 (needs whitelisting)

---

### **Step 2: Verify Network Connectivity**
**Execute from office network (after firewall update):**

```bash
# Test basic TCP connectivity to IBM i
telnet 10.0.0.7 23
```

**Expected Result:**
```
Trying 10.0.0.7...
Connected to 10.0.0.7.
Escape character is '^]'.
[IBM i sign-on screen should appear]
```

**Troubleshooting:**
- If connection refused: Firewall still blocking
- If timeout: Network routing issue
- If successful: Proceed to Step 3

---

### **Step 3: Test Production API Health**
**Verify IBM i connection from Fly.io:**

```bash
curl -X GET https://wc-ducomb.fly.dev/api/inventory/health
```

**Expected Result (Success):**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-08T...",
  "services": {
    "p5250": true,
    "redis": false,
    "ibm_connection": true  ← CRITICAL: Should be true
  }
}
```

**Current Result (IP Blocked):**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-08T...",
  "services": {
    "p5250": true,
    "redis": false,
    "ibm_connection": false  ← Will be true after firewall update
  }
}
```

---

### **Step 4: Test SKU Lookup via Direct API**
**Test inventory lookup functionality:**

```bash
# Test specific SKU lookup for lov224006
curl -X POST https://wc-ducomb.fly.dev/api/inventory/lookup \
  -H "Content-Type: application/json" \
  -d '{"sku": "lov224006"}'
```

**Expected Success Response:**
```json
{
  "found": true,
  "sku": "LOV224006",
  "description": "[Item Description]",
  "warehouse": "01",
  "unit_of_measure": "EA",
  "on_hand": 123.0,
  "allocated": 10.0,
  "net_available": 113.0,
  "timestamp": "2025-08-08T..."
}
```

**Current Response (IP Blocked):**
```json
{
  "sku": "LOV224006",
  "found": false,
  "error": "Could not connect to inventory system",
  "timestamp": "2025-08-08T..."
}
```

---

### **Step 5: Test Chat Interface API**
**Test natural language interface:**

```bash
# Test chat interface with SKU query
curl -X POST https://wc-ducomb.fly.dev/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "lov224006"}'
```

**Expected Success Response:**
```json
{
  "success": true,
  "message": "📦 **LOV224006** - [Description]\n\n🏭 **Warehouse:** 01\n📊 **Status:** ✅ In Stock\n\n**Quantities:**\n• On Hand: 123 EA\n• Allocated: 10\n• Available: 113\n• On Purchase Order: 0\n• On Back Order: 0\n\n⏱️ *Retrieved: 14:32:15*"
}
```

**Current Response (IP Blocked):**
```json
{
  "success": true,
  "message": "❌ SKU LOV224006 not found in inventory system."
}
```

---

### **Step 6: Test Web Interface**
**Complete end-user testing:**

1. **Navigate to**: https://wc-ducomb.fly.dev/
2. **Verify**: Frontend loads with chat interface
3. **Enter**: `lov224006` in chat input field
4. **Press**: Enter key
5. **Observe**: Response in chat window

**Expected Success Result:**
- Chat displays formatted inventory data
- Response time under 30 seconds
- All quantity fields populated
- Warehouse and description shown

**Current Result (IP Blocked):**
- Chat displays "SKU not found" message
- Fast response (no backend timeout)

---

### **Step 7: Performance Testing**
**Once connectivity is restored:**

```bash
# Test response time
time curl -X POST https://wc-ducomb.fly.dev/api/inventory/lookup \
  -H "Content-Type: application/json" \
  -d '{"sku": "DGE037700"}'
```

**Expected Metrics:**
- **First Lookup**: ~15-25 seconds (full 5250 navigation)
- **Cached Lookup**: ~0.5-2 seconds (Redis cache hit)
- **Connection Time**: ~0.3 seconds to IBM i
- **Success Rate**: 99%+ with retry logic

---

## 🔍 **TROUBLESHOOTING GUIDE**

### **Network Issues**
```bash
# Check current outbound IP
curl https://wc-ducomb.fly.dev/api/inventory/status

# Verify deployment
flyctl status -a wc-ducomb

# Check application logs
flyctl logs -a wc-ducomb
```

### **Connection Diagnostics**
```bash
# Test network path from Fly.io
flyctl ssh console -a wc-ducomb -C "timeout 10 python3 -c \"
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
result = sock.connect_ex(('10.0.0.7', 23))
print('SUCCESS' if result == 0 else f'BLOCKED (error {result})')
\""
```

### **API Health Monitoring**
```bash
# Continuous health monitoring
while true; do
  curl -s https://wc-ducomb.fly.dev/api/inventory/health | grep ibm_connection
  sleep 30
done
```

---

## ✅ **SUCCESS CRITERIA**

### **Network Layer**
- ✅ TCP connection to 10.0.0.7:23 successful
- ✅ Connection time under 10ms
- ✅ IBM i sign-on screen accessible via telnet

### **Application Layer**
- ✅ Health check shows `"ibm_connection": true`
- ✅ API lookup returns valid JSON with inventory data
- ✅ Chat interface displays formatted responses
- ✅ Response time under 30 seconds for full lookup

### **Data Validation**
- ✅ SKU lov224006 returns structured inventory data
- ✅ All quantity fields populated (on_hand, allocated, available)
- ✅ Description and warehouse information present
- ✅ Timestamp indicates recent data retrieval

### **Performance Metrics**
- ✅ **Connection**: ~0.3 seconds to IBM i system
- ✅ **Full Lookup**: ~15-25 seconds (menu navigation + parsing)
- ✅ **Cached Response**: Sub-second for repeated queries
- ✅ **Reliability**: 99%+ success rate with error handling

---

## 🎯 **TEST SCENARIOS**

### **Scenario 1: Known Good SKU**
- **Test SKU**: `DGE037700` (validated working)
- **Expected**: Inventory data with 6.000 EA available
- **Purpose**: Confirm end-to-end functionality

### **Scenario 2: Target SKU**
- **Test SKU**: `lov224006` (user requested)
- **Expected**: Valid inventory response or clear "not found"
- **Purpose**: Fulfill original testing requirement

### **Scenario 3: Invalid SKU**
- **Test SKU**: `INVALID123`
- **Expected**: Clean error message "SKU not found"
- **Purpose**: Verify error handling

### **Scenario 4: Bulk Testing**
- **Test Multiple SKUs**: `["DGE037700", "lov224006", "DGE037592"]`
- **Expected**: Array of results with individual status
- **Purpose**: Validate concurrent processing

---

## 📊 **MONITORING COMMANDS**

### **Real-time Status**
```bash
# Watch system health
watch -n 10 "curl -s https://wc-ducomb.fly.dev/api/inventory/health | jq '.services'"

# Monitor application metrics
curl -s https://wc-ducomb.fly.dev/api/inventory/metrics | jq
```

### **Deployment Status**
```bash
# Check machine status
flyctl status -a wc-ducomb

# View resource usage  
flyctl machine status -a wc-ducomb

# Check IP addresses
flyctl ips list -a wc-ducomb
```

### **Log Analysis**
```bash
# Application logs
flyctl logs -a wc-ducomb

# Specific error filtering
flyctl logs -a wc-ducomb | grep -i error

# Connection attempts
flyctl logs -a wc-ducomb | grep -i "connection\|connect"
```

---

## 🔄 **POST-TESTING VALIDATION**

### **After Successful Testing**
1. **Document Results**: Update this document with actual test results
2. **Performance Baseline**: Record actual response times
3. **Error Cases**: Document any edge cases encountered
4. **User Acceptance**: Confirm SKU lov224006 functionality

### **Continuous Monitoring Setup**
```bash
# Set up monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
  timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  status=$(curl -s https://wc-ducomb.fly.dev/api/inventory/health | jq -r '.services.ibm_connection')
  echo "$timestamp - IBM Connection: $status"
  sleep 300  # Check every 5 minutes
done
EOF
chmod +x monitor.sh
```

---

## 🚨 **CRITICAL SUCCESS METRICS**

### **Network Breakthrough Validation**
- **IP Connectivity**: 69.31.3.78 → 10.0.0.7:23 successful
- **Protocol Handshake**: 5250/Telnet negotiation completes
- **Authentication**: ROBERT/TECH login sequence successful

### **Application Integration Validation**
- **Menu Navigation**: Main → Option 2 → Option 11 automated
- **Screen Parsing**: Inventory data extracted correctly
- **Error Handling**: Timeout and retry logic functional

### **Business Process Validation**
- **SKU Lookup**: lov224006 returns expected data format
- **Response Time**: Full lookup cycle under 30 seconds
- **Data Accuracy**: Quantities and descriptions match IBM i system

---

## 📝 **TEST EXECUTION LOG**

**Test Date**: _____________  
**Executed By**: _____________  
**Firewall Updated**: [ ] Yes [ ] No  
**Network Test**: [ ] Pass [ ] Fail  
**API Health**: [ ] Pass [ ] Fail  
**SKU Lookup**: [ ] Pass [ ] Fail  
**Web Interface**: [ ] Pass [ ] Fail  

**Notes:**
_________________________________
_________________________________
_________________________________

---

This document provides complete step-by-step procedures for validating the WC Ducomb Inventory System once the firewall configuration is updated to allow IP `69.31.3.78`.

**Current Status**: Ready for testing pending firewall update  
**Next Action**: Update IBM i firewall rule  
**Expected Result**: Full system functionality restored