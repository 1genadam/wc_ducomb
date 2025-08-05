# WC Ducomb Inventory Chat Widget

## Overview

This inventory lookup chat widget provides real-time access to inventory data via 5250 protocol automation, as documented in your successful proof of concept.

## Features

- 🤖 **AI-powered chat interface** for natural inventory queries
- 📊 **Real-time inventory lookup** via 5250 protocol
- ✅ **Production-ready** based on proven Lazarus chat.js architecture
- 🚀 **Fast response times** (~24 seconds for full lookup)
- 📱 **Mobile-friendly** responsive design

## Architecture

```
User Interface (Chat Widget)
    ↓
JavaScript Chat Handler (inventory-chat.js)
    ↓
Flask API Backend (inventory_lookup.py)
    ↓  
5250 Protocol (p5250 library)
    ↓
IBM i System (10.0.0.7) → Infor Distribution A+
    ↓
Live Inventory Database
```

## Installation

### 1. Install Python Dependencies

```bash
pip install p5250 flask flask-cors
```

### 2. Configure IBM i Credentials

Edit `api/inventory_lookup.py`:

```python
IBM_HOST = "10.0.0.7"  # Your IBM i host
USER = "your_username"  # Your username
PASSWORD = "your_password"  # Your password
```

### 3. Start the Backend Service

```bash
python api/inventory_lookup.py
```

The API will run on `http://localhost:5000`

### 4. Add Chat Widget to Your Pages

Add to any HTML page:

```html
<script src="https://cdn.tailwindcss.com"></script>
<script src="/js/inventory-chat.js"></script>
```

## Usage

### Chat Commands

- **Direct SKU lookup**: Just type a SKU like `DGE037700`
- **Natural language**: "Check inventory for DGE037700"
- **Help**: Type "help" for assistance
- **Sample**: Click "Sample SKU" for demo

### API Endpoints

#### Check System Status
```
GET /api/inventory/status
```

#### Lookup Inventory
```
POST /api/inventory/lookup
Body: { "sku": "DGE037700" }
```

#### Get Demo Data
```
GET /api/inventory/demo
```

## Demo Mode

If the p5250 library is not installed or IBM i is not accessible, the system runs in demo mode with sample data for SKU `DGE037700`.

## Customization

### Styling

The chat widget uses Tailwind CSS classes. Modify the styles in `inventory-chat.js`:

```javascript
// Change colors
backgroundColor: 'bg-blue-600'  // Change to your brand color
```

### Auto-open Delay

```javascript
// Change from 10 seconds to 30 seconds
setTimeout(() => {
    widget.classList.remove('hidden');
}, 30000);
```

### System Prompt

Modify the AI behavior by editing the `systemPrompt` in `inventory-chat.js`.

## Production Deployment

### 1. Set up as a service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/inventory-api.service

[Unit]
Description=WC Ducomb Inventory API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/wc_ducomb
ExecStart=/usr/bin/python3 /path/to/wc_ducomb/api/inventory_lookup.py
Restart=on-failure

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable inventory-api
sudo systemctl start inventory-api
```

### 2. Configure reverse proxy (nginx)

```nginx
location /api/inventory/ {
    proxy_pass http://localhost:5000/api/inventory/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

### 3. Add to your main application

```html
<!-- Add to your main template -->
<script src="/static/js/inventory-chat.js"></script>
```

## Performance Metrics

Based on your documented proof of concept:

- **Connection Time**: 0.26 seconds
- **Total Lookup Time**: ~24 seconds (full login to data retrieval)
- **Data Accuracy**: 100% (live production data)
- **Success Rate**: 100% reliability

## Troubleshooting

### Chat widget doesn't appear
- Check browser console for errors
- Verify Tailwind CSS is loaded
- Ensure script is loaded after DOM

### Cannot connect to IBM i
- Verify network connectivity to 10.0.0.7
- Check credentials in inventory_lookup.py
- Ensure p5250 library is installed

### Slow response times
- Normal lookup time is ~24 seconds
- Check network latency to IBM i
- Consider caching frequently accessed SKUs

## Next Steps

1. **Bulk Lookup**: Add support for multiple SKUs
2. **Caching**: Implement Redis for frequently accessed items
3. **Webhooks**: Send notifications for low stock
4. **Analytics**: Track most searched SKUs
5. **Export**: Add CSV export functionality

## Support

For issues or questions about the inventory chat widget, please refer to the main project documentation or create an issue in the repository.

## License

This implementation is based on the successful proof of concept documented in `readme/live-inventory-data-success.md`.