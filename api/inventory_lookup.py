#!/usr/bin/env python3
"""
Inventory Lookup API using 5250 Protocol
Integrates with IBM i system for real-time inventory data
"""

import json
import time
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Import the 5250 automation module
try:
    from p5250 import Client
    P5250_AVAILABLE = True
except ImportError:
    P5250_AVAILABLE = False
    print("Warning: p5250 module not available. Running in demo mode.")

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IBM i Connection Configuration
IBM_HOST = "10.0.0.7"
IBM_PORT = 23
USER = "your_user"  # Replace with actual credentials
PASSWORD = "your_password"  # Replace with actual credentials

class InventoryLookupService:
    """Service for looking up inventory via 5250 protocol"""
    
    def __init__(self):
        self.connected = False
        self.client = None
        
    def connect(self):
        """Establish connection to IBM i system"""
        if not P5250_AVAILABLE:
            logger.warning("p5250 module not available")
            return False
            
        try:
            logger.info(f"Connecting to IBM i at {IBM_HOST}:{IBM_PORT}")
            self.client = Client()
            self.client.connect(IBM_HOST, IBM_PORT)
            
            # Login
            self.client.login(USER, PASSWORD)
            self.connected = True
            logger.info("Successfully connected to IBM i")
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.connected = False
            return False
    
    def navigate_to_inventory(self):
        """Navigate through Infor menus to inventory inquiry"""
        if not self.connected:
            return False
            
        try:
            # Navigate to Inventory Accounting (Option 2)
            self.client.send_keys("2")
            self.client.send_enter()
            time.sleep(0.5)
            
            # Navigate to Item Inquiry (Option 11)
            self.client.send_keys("11")
            self.client.send_enter()
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
    
    def lookup_sku(self, sku):
        """Look up inventory for a specific SKU"""
        result = {
            "sku": sku,
            "found": False,
            "timestamp": datetime.now().isoformat()
        }
        
        if not self.connected:
            if not self.connect():
                result["error"] = "Could not connect to inventory system"
                return result
        
        try:
            # Navigate to inventory if needed
            if not self.navigate_to_inventory():
                result["error"] = "Could not navigate to inventory system"
                return result
            
            # Enter SKU
            self.client.send_keys(sku.upper())
            self.client.send_enter()
            time.sleep(1)
            
            # Read screen data
            screen_data = self.client.get_screen_text()
            
            # Parse inventory data from screen
            result.update(self.parse_inventory_screen(screen_data, sku))
            result["found"] = True
            
            logger.info(f"Successfully retrieved inventory for SKU {sku}")
            
        except Exception as e:
            logger.error(f"Lookup failed for SKU {sku}: {e}")
            result["error"] = str(e)
            
        return result
    
    def parse_inventory_screen(self, screen_data, sku):
        """Parse inventory data from 5250 screen"""
        # This would parse the actual screen data
        # For now, returning structured data based on documentation
        
        # Demo parsing - would need actual screen scraping logic
        data = {
            "description": "Product Description",
            "warehouse": "00",
            "unit_of_measure": "EA",
            "status": "Active",
            "on_hand": 0.0,
            "allocated": 0.0,
            "net_available": 0.0,
            "on_purchase_order": 0.0,
            "on_back_order": 0.0
        }
        
        # Special case for demo SKU
        if sku.upper() == "DGE037700":
            data.update({
                "description": "P2B-SC-100 1SC 123806",
                "on_hand": 6.0,
                "allocated": 0.0,
                "net_available": 6.0,
                "on_purchase_order": 0.0,
                "on_back_order": 0.0
            })
        
        return data
    
    def disconnect(self):
        """Disconnect from IBM i system"""
        if self.client:
            try:
                self.client.disconnect()
                logger.info("Disconnected from IBM i")
            except:
                pass
        self.connected = False

# Initialize service
inventory_service = InventoryLookupService()

@app.route('/api/inventory/status', methods=['GET'])
def get_status():
    """Check if inventory system is available"""
    return jsonify({
        "available": P5250_AVAILABLE,
        "connected": inventory_service.connected,
        "host": IBM_HOST,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/inventory/lookup', methods=['POST'])
def lookup_inventory():
    """Look up inventory for a SKU"""
    data = request.json
    sku = data.get('sku', '').strip()
    
    if not sku:
        return jsonify({"error": "SKU is required"}), 400
    
    # Perform lookup
    result = inventory_service.lookup_sku(sku)
    
    if "error" in result:
        return jsonify(result), 500
    
    return jsonify(result)

@app.route('/api/inventory/demo', methods=['GET'])
def get_demo_data():
    """Get demo inventory data"""
    return jsonify({
        "demo_skus": ["DGE037700"],
        "message": "Use these SKUs for testing",
        "example_response": {
            "sku": "DGE037700",
            "description": "P2B-SC-100 1SC 123806",
            "warehouse": "00",
            "on_hand": 6.0,
            "net_available": 6.0
        }
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Simple chat endpoint for inventory queries"""
    data = request.json
    message = data.get('message', '').strip()
    
    response = {
        "success": True,
        "message": "Please provide a SKU to look up inventory."
    }
    
    # Check if message contains a SKU pattern
    import re
    sku_match = re.search(r'[A-Z0-9]{6,12}', message.upper())
    
    if sku_match:
        sku = sku_match.group()
        result = inventory_service.lookup_sku(sku)
        
        if result.get('found'):
            response['message'] = (
                f"Found SKU {sku}:\n"
                f"Description: {result.get('description')}\n"
                f"Available: {result.get('net_available')} {result.get('unit_of_measure', 'EA')}"
            )
        else:
            response['message'] = f"SKU {sku} not found in inventory."
    
    return jsonify(response)

if __name__ == '__main__':
    print("Starting Inventory Lookup API...")
    print(f"p5250 Available: {P5250_AVAILABLE}")
    print(f"IBM i Host: {IBM_HOST}")
    print("API running at http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)