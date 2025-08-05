# WC Ducomb Inventory Chat Widget - Deployment Guide

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Redis Server** (optional but recommended for caching)
- **Access to IBM i system** at 10.0.0.7 with credentials

### Installation

1. **Clone and setup:**
   ```bash
   git clone https://github.com/1genadam/wc_ducomb.git
   cd wc_ducomb
   git checkout feature/inventory-chat-widget
   ```

2. **Install dependencies:**
   ```bash
   # Python dependencies
   pip install -r requirements.txt
   
   # Node.js dependencies  
   npm install
   ```

3. **Configure credentials:**
   Edit `api/inventory_lookup.py` and update:
   ```python
   USER = "ROBERT"      # Your IBM i username
   PASSWORD = "TECH"    # Your IBM i password
   IBM_HOST = "10.0.0.7"  # Confirm IP address
   ```

4. **Start services:**
   ```bash
   # Terminal 1: Start Python API backend
   python api/inventory_lookup.py
   
   # Terminal 2: Start Node.js frontend server
   npm start
   ```

5. **Test the system:**
   ```bash
   # Open browser to:
   http://localhost:3000        # Chat widget demo
   http://localhost:3000/admin  # Admin dashboard
   
   # Or run API tests:
   python test_live_api.py
   ```

## 📋 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │───▶│  Node.js Server  │───▶│  Python API     │
│  (Chat Widget)  │    │  (Port 3000)     │    │  (Port 5000)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                            ┌─────────────────┐    ┌─────────────────┐
                            │  Redis Cache    │    │   IBM i System  │
                            │  (Optional)     │    │   (10.0.0.7)    │
                            └─────────────────┘    └─────────────────┘
```

## 🛠️ Production Deployment

### Option 1: Systemd Service (Recommended for Linux)

1. **Create inventory user:**
   ```bash
   sudo useradd -r -m -s /bin/bash inventory
   sudo mkdir -p /opt/wc_ducomb
   sudo chown inventory:inventory /opt/wc_ducomb
   ```

2. **Deploy application:**
   ```bash
   sudo cp -r . /opt/wc_ducomb/
   sudo chown -R inventory:inventory /opt/wc_ducomb
   
   # Create Python virtual environment
   cd /opt/wc_ducomb
   sudo -u inventory python -m venv venv
   sudo -u inventory ./venv/bin/pip install -r requirements.txt
   ```

3. **Install systemd service:**
   ```bash
   sudo cp systemd/inventory-api.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable inventory-api
   sudo systemctl start inventory-api
   ```

4. **Setup Nginx reverse proxy:**
   ```nginx
   # /etc/nginx/sites-available/inventory-chat
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:3000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
       
       location /api/ {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_connect_timeout 60s;
           proxy_send_timeout 60s;
           proxy_read_timeout 60s;
       }
   }
   ```

### Option 2: Docker Deployment

1. **Create Dockerfile:**
   ```dockerfile
   # Production Dockerfile
   FROM python:3.11-slim as backend
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY api/ ./api/
   
   FROM node:18-slim as frontend
   
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci --only=production
   COPY public/ ./public/
   COPY server.js .
   
   EXPOSE 3000 5000
   CMD ["npm", "start"]
   ```

2. **Docker Compose setup:**
   ```yaml
   # docker-compose.yml
   version: '3.8'
   services:
     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"
       volumes:
         - redis_data:/data
   
     inventory-api:
       build: .
       ports:
         - "5000:5000"
       depends_on:
         - redis
       environment:
         - REDIS_URL=redis://redis:6379/0
       volumes:
         - ./logs:/app/logs
   
     inventory-frontend:
       build: .
       ports:
         - "3000:3000"
       depends_on:
         - inventory-api
       environment:
         - API_BASE_URL=http://inventory-api:5000
   
   volumes:
     redis_data:
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `IBM_HOST` | IBM i system IP address | `10.0.0.7` |
| `IBM_PORT` | IBM i telnet port | `23` |
| `IBM_USER` | IBM i username | `ROBERT` |
| `IBM_PASSWORD` | IBM i password | `TECH` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `FLASK_ENV` | Flask environment | `production` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `API_BASE_URL` | Backend API URL for frontend | `http://localhost:5000` |

### Redis Setup (Optional but Recommended)

1. **Install Redis:**
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install redis-server
   
   # CentOS/RHEL
   sudo yum install redis
   
   # macOS
   brew install redis
   ```

2. **Configure Redis:**
   ```bash
   # Edit /etc/redis/redis.conf
   maxmemory 256mb
   maxmemory-policy allkeys-lru
   save 900 1
   save 300 10
   save 60 10000
   ```

3. **Start Redis:**
   ```bash
   sudo systemctl enable redis
   sudo systemctl start redis
   ```

## 📊 Monitoring and Maintenance

### Health Checks

- **API Health:** `GET /api/inventory/health`
- **Frontend Health:** `GET /health`
- **System Status:** `GET /api/inventory/status`

### Log Files

- **API Logs:** `inventory_api.log`
- **System Logs:** `journalctl -u inventory-api`
- **Access Logs:** Check Nginx/Apache logs

### Performance Monitoring

1. **Check metrics endpoint:**
   ```bash
   curl http://localhost:5000/api/inventory/metrics
   ```

2. **Monitor cache performance:**
   ```bash
   redis-cli info stats
   ```

3. **View recent lookups:**
   ```bash
   curl http://localhost:5000/api/inventory/recent
   ```

### Maintenance Tasks

1. **Clear cache:**
   ```bash
   curl -X POST http://localhost:5000/api/inventory/cache/clear
   ```

2. **Restart services:**
   ```bash
   sudo systemctl restart inventory-api
   sudo systemctl restart nginx
   ```

3. **Update application:**
   ```bash
   cd /opt/wc_ducomb
   git pull origin feature/inventory-chat-widget
   sudo systemctl restart inventory-api
   ```

## 🚨 Troubleshooting

### Common Issues

1. **Connection Refused (5250)**
   - Check IBM i system is accessible: `telnet 10.0.0.7 23`
   - Verify credentials are correct
   - Check firewall settings

2. **Login Failures**
   - Verify username/password in `inventory_lookup.py`
   - Check IBM i user profile is active
   - Ensure user has proper permissions

3. **Navigation Errors**
   - Check if menu options have changed
   - Verify Infor Distribution A+ is available
   - Review application logs for details

4. **Screen Parsing Issues**
   - Update parsing logic in `parse_inventory_screen()`
   - Check screen format hasn't changed
   - Test with known good SKUs

5. **Performance Issues**
   - Enable Redis caching
   - Check connection pool settings
   - Monitor system resources

### Debug Mode

Enable detailed logging:
```python
# In inventory_lookup.py
logging.basicConfig(level=logging.DEBUG)
```

### Testing Connectivity

```bash
# Test 5250 connection
python -c "
from p5250 import P5250Client
client = P5250Client(hostName='10.0.0.7', hostPort='23')
client.connect()
print('Connected:', client.isConnected())
"
```

## 📈 Performance Tuning

### Recommended Settings

- **Connection Pool:** 3-5 persistent connections
- **Cache TTL:** 30 minutes for inventory data
- **Request Timeout:** 30 seconds for lookups
- **Max Concurrent Requests:** 10 per backend instance

### Scaling

1. **Horizontal Scaling:**
   - Run multiple API instances behind load balancer
   - Use shared Redis cache
   - Implement session affinity if needed

2. **Vertical Scaling:**
   - Increase memory allocation
   - Optimize database queries
   - Enable connection pooling

## 🔒 Security Considerations

1. **Credentials Management:**
   - Use environment variables for secrets
   - Implement credential rotation
   - Use secure credential storage

2. **Network Security:**
   - Implement HTTPS in production
   - Restrict API access to known IPs
   - Use VPN for IBM i connectivity

3. **Application Security:**
   - Validate all SKU inputs
   - Implement rate limiting
   - Log all access attempts

## 📞 Support

For issues and questions:

1. **Check logs:** `inventory_api.log` and system logs
2. **Test connectivity:** Use provided test scripts
3. **Review documentation:** This guide and code comments
4. **Contact support:** Create GitHub issue with logs and error details

---

**Version:** 1.0.0  
**Last Updated:** August 2025  
**Maintainer:** WC Ducomb Development Team