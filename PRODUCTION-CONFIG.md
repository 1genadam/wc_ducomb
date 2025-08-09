# WC Ducomb Production Configuration Documentation

## 🚀 Fly.io Production Environment

### **Critical Production Settings**
These settings are configured as Fly.io secrets and will persist through deployments:

```bash
# IBM i Connection Settings (Production)
IBM_HOST=216.176.21.86      # Working production IP (verified via telnet)
IBM_USER=ROBERT             # IBM i username
IBM_PASSWORD=TECH           # IBM i password  
IBM_PORT=23                 # Standard telnet port
```

### **Deployment Safety**
- ✅ **Code deployments are safe**: `./deploy.sh` updates application code only
- ✅ **Secrets persist**: Fly.io secrets are NOT overwritten by deployments
- ✅ **Configuration maintained**: Production settings remain intact

### **Authentication Fix Applied**
- **Date**: 2025-08-09 (23:45:50)
- **Issue**: P5250 authentication credential corruption (`TECHRT` instead of `ROBERT`/`TECH`)
- **Solution**: Real P5250 library (v0.1.0) + p3270 dependency + improved login sequence
- **Status**: ✅ **FIXED** - System successfully connects to IBM i

### **System Architecture**
```
Browser → Fly.io (ORD) → Node.js Proxy → Python Flask → P5250 Library → IBM i (216.176.21.86:23)
```

### **Monitoring URLs**
- **Main App**: https://wc-ducomb.fly.dev
- **Admin Dashboard**: https://wc-ducomb.fly.dev/admin  
- **API Status**: https://wc-ducomb.fly.dev/api/inventory/status
- **System Commands**: https://wc-ducomb.fly.dev/api/inventory/commands

### **Local Development**
For local development, use different settings:
```bash
# Local Development (.env file)
IBM_HOST=localhost          # Or your local test system
IBM_USER=TESTUSER          # Local test credentials
IBM_PASSWORD=TESTPASS      # Local test credentials
IBM_PORT=23                # Standard port
```

### **Deployment History**
```bash
# Latest deployment with P5250 authentication fix
[feature/inventory-chat-widget b8a4b1f] Deploy WC Ducomb Inventory System - 2025-08-08 23:45:50
 3 files changed, 42 insertions(+), 221 deletions(-)
 - Removed custom P5250 implementation (api/p5250.py)
 - Added real P5250 library dependencies (p5250==0.1.0, p3270)
 - Enhanced authentication sequence with proper timing
```

### **Testing Status**
- **P5250 Library**: ✅ Working (v0.1.0 + p3270 v0.1.6)
- **IBM i Connection**: ✅ Connecting to 216.176.21.86:23
- **Authentication**: ✅ Fixed credential sequence 
- **Admin Dashboard**: ✅ Dual-terminal command visibility
- **Ready for SKU Lookup**: ✅ Test with DGE037700

---
**⚠️ IMPORTANT**: Never commit IBM i credentials to git. Production secrets are managed via `flyctl secrets`.