# Production Deployment Guide - WC Ducomb Inventory System

**Target Audience:** DevOps, System Administrators, Development Teams  
**Last Updated:** 2025-08-05  
**Status:** Production Ready ✅

## Quick Start

```bash
# Clone repository
git clone https://github.com/1genadam/wc_ducomb
cd wc_ducomb

# Deploy with direct IBM i access
./deploy.sh

# Deploy with VPN tunnel (if needed)
DIRECT_ACCESS=false ./deploy.sh
```

## Prerequisites

### **Local Development Environment**
- **Git:** Repository management and deployment pipeline
- **Fly CLI:** `brew install flyctl` (macOS) or platform equivalent
- **Node.js 18+:** Frontend server and dependency management
- **Python 3.11+:** Backend API and 5250 protocol automation

### **Production Requirements**
- **Fly.io Account:** Deployment platform with auto-scaling
- **GitHub Repository:** Source code management and CI/CD
- **IBM i Access:** Network connectivity to 10.0.0.7:23
- **Credentials:** IBM i user account (ROBERT/TECH)

## Network Access Configuration

### **Option 1: Direct Access (Recommended)**
**Requirements:** IBM i system allows Fly.io IP ranges

```bash
# Deploy with direct access (default)
./deploy.sh
```

**Benefits:**
- ✅ Faster deployment and setup
- ✅ No additional infrastructure required  
- ✅ Lower latency and complexity
- ✅ Easier monitoring and troubleshooting

### **Option 2: VPN Tunnel (Fallback)**
**Requirements:** Local network gateway with VPN capability

```bash
# Deploy with VPN tunnel
DIRECT_ACCESS=false ./deploy.sh
```

**Setup Steps:**
1. **Configure Local Gateway:** Install Tailscale on local network machine
2. **Generate Auth Key:** https://login.tailscale.com/admin/settings/keys
3. **Set Fly.io Secret:** `flyctl secrets set TAILSCALE_AUTHKEY="your-key"`
4. **Enable Subnet Routing:** `sudo tailscale up --advertise-routes=10.0.0.0/24`

## Deployment Pipeline

### **Automated Deployment Process**
The `./deploy.sh` script handles complete deployment:

1. **Git Operations**
   - Stage changes (excludes node_modules, logs)
   - Create descriptive commit with timestamp
   - Push to GitHub feature branch

2. **Access Method Configuration**
   - Detects DIRECT_ACCESS environment variable
   - Switches Dockerfile automatically
   - Configures appropriate startup scripts

3. **Fly.io Deployment**
   - Validates configuration
   - Builds Docker container
   - Deploys with rolling updates
   - Verifies health checks

4. **Post-Deployment Validation**
   - System health verification
   - Performance metrics collection
   - Error log analysis

### **Manual Deployment Steps**
If automation fails, manual deployment:

```bash
# 1. Prepare repository
git add .
git commit -m "Manual deployment - $(date)"
git push origin feature/inventory-chat-widget

# 2. Deploy to Fly.io
flyctl deploy -a wc-ducomb

# 3. Verify deployment
flyctl status -a wc-ducomb
flyctl logs -a wc-ducomb
```

## Configuration Management

### **Environment Variables**
| Variable | Purpose | Default | Required |
|----------|---------|---------|----------|
| `NODE_ENV` | Runtime environment | `production` | Yes |
| `PORT` | Frontend server port | `3000` | Yes |
| `API_PORT` | Backend API port | `5001` | Yes |
| `IBM_HOST` | IBM i system address | `10.0.0.7` | Yes |
| `IBM_USER` | IBM i username | `ROBERT` | Yes |
| `IBM_PASSWORD` | IBM i password | `TECH` | Yes |
| `TAILSCALE_AUTHKEY` | VPN authentication | - | VPN mode only |

### **Secrets Management**
```bash
# Set production secrets
flyctl secrets set IBM_PASSWORD="your-password" -a wc-ducomb
flyctl secrets set TAILSCALE_AUTHKEY="your-auth-key" -a wc-ducomb

# View configured secrets (values hidden)
flyctl secrets list -a wc-ducomb
```

### **Application Configuration**
**File:** `fly.toml`
```toml
app = "wc-ducomb"
primary_region = "ord"

[env]
  NODE_ENV = "production"
  PORT = "3000"
  API_PORT = "5001"
  IBM_HOST = "10.0.0.7"
  IBM_USER = "ROBERT"

[http_service]
  internal_port = 3000
  force_https = true
  auto_stop_machines = "suspend"
  auto_start_machines = true
  min_machines_running = 1

[[vm]]
  size = "shared-cpu-1x"
```

## Monitoring & Health Checks

### **Application Health Endpoints**
- **Frontend:** `GET https://wc-ducomb.fly.dev/health`
- **Backend API:** `GET https://wc-ducomb.fly.dev/api/inventory/health`
- **System Status:** `GET https://wc-ducomb.fly.dev/api/inventory/status`

### **Administrative Dashboard**
**URL:** https://wc-ducomb.fly.dev/admin

**Features:**
- Real-time system metrics
- Error log analysis
- Performance statistics
- Connection status monitoring

### **Fly.io Monitoring**
```bash
# Application status
flyctl status -a wc-ducomb

# Real-time logs
flyctl logs -a wc-ducomb

# Machine metrics
flyctl machine list -a wc-ducomb

# SSH into running container
flyctl ssh console -a wc-ducomb
```

## Troubleshooting Guide

### **Common Deployment Issues**

**Issue:** Machine startup failures
```bash
# Check logs for errors
flyctl logs -a wc-ducomb

# Restart machines
flyctl machine restart -a wc-ducomb
```

**Issue:** Network connectivity to IBM i
```bash
# Test from container
flyctl ssh console -a wc-ducomb
nc -z 10.0.0.7 23
```

**Issue:** VPN tunnel not connecting
```bash
# Check Tailscale status in container
flyctl ssh console -a wc-ducomb  
tailscale status
```

### **Performance Optimization**

**Slow Response Times:**
1. Check Redis cache status in admin panel
2. Monitor IBM i system load
3. Review 5250 connection pooling
4. Analyze network latency

**High Error Rates:**
1. Review error logs in admin dashboard
2. Check IBM i system availability
3. Verify credential configuration
4. Monitor rate limiting thresholds

### **Emergency Procedures**

**Complete System Failure:**
```bash
# Quick rollback to previous deployment
flyctl releases list -a wc-ducomb
flyctl releases rollback -r <release-id> -a wc-ducomb
```

**Network Access Issues:**
```bash
# Switch to VPN mode immediately
DIRECT_ACCESS=false ./deploy.sh
```

## Security Considerations

### **Access Control**
- **Network Isolation:** IBM i system behind firewall
- **Credential Security:** Environment variables, no hardcoded passwords
- **Transport Security:** TLS encryption for all HTTP traffic
- **Input Validation:** SKU format validation prevents injection attacks

### **Monitoring Security**
- **Error Sanitization:** No sensitive data in client responses
- **Audit Logging:** All 5250 operations logged
- **Rate Limiting:** Prevents abuse and DoS attacks
- **Health Check Security:** Internal endpoints not exposed

## Backup & Recovery

### **Code Repository**
- **Primary:** GitHub repository with full history
- **Deployment Automation:** Complete deployment pipeline in `deploy.sh`
- **Configuration:** All settings in version control

### **Data Backup**
- **Source of Truth:** IBM i system (no data stored in application)
- **Configuration Backup:** Fly.io secrets and environment variables
- **Log Retention:** Application logs for debugging and analysis

### **Disaster Recovery**
1. **Complete Rebuild:** Clone repository and run `./deploy.sh`
2. **Network Failover:** Switch between direct and VPN access methods
3. **Multi-Region Deployment:** Scale to additional Fly.io regions if needed

## Performance Benchmarks

### **Response Time Targets**
- **Health Check:** < 100ms
- **Cached Inventory Lookup:** < 500ms  
- **Full 5250 Inventory Lookup:** < 30 seconds
- **System Startup:** < 60 seconds

### **Scalability Metrics**
- **Concurrent Users:** 50+ simultaneous requests
- **Daily Requests:** 10,000+ inventory lookups
- **Uptime Target:** 99.9% availability
- **Error Rate:** < 1% failed requests

## Cost Management

### **Fly.io Pricing Optimization**
- **Auto-scaling:** Machines suspend when idle
- **Resource Sizing:** shared-cpu-1x sufficient for current load
- **Region Selection:** Single region (ord) minimizes costs
- **Traffic Optimization:** CDN and compression enabled

### **Monitoring Costs**
```bash
# View current usage and billing
flyctl billing status

# Monitor machine utilization
flyctl metrics -a wc-ducomb
```

## Maintenance Schedule

### **Regular Maintenance**
- **Weekly:** Review error logs and performance metrics
- **Monthly:** Update dependencies and security patches
- **Quarterly:** Performance optimization and capacity planning
- **Annually:** Security audit and access review

### **Update Procedures**
```bash
# Update application code
git pull origin main
./deploy.sh

# Update system dependencies
npm update
pip install -r requirements.txt --upgrade
./deploy.sh
```

This guide provides complete production deployment and operational procedures for the WC Ducomb Inventory System, ensuring reliable, secure, and scalable operation.