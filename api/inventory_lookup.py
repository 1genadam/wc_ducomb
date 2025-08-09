#!/usr/bin/env python3
"""
WC Ducomb Inventory Lookup API using 5250 Protocol
Production-ready implementation with IBM i system integration
"""

import json
import time
import re
import os
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Lock
import redis
from functools import wraps

# Load environment variables from .env file if it exists (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger = logging.getLogger(__name__)  # Will be properly configured below
    if logger.handlers:  # Only log if logger is set up
        logger.info("Loaded environment variables from .env file")
except ImportError:
    # dotenv not available, use system environment variables only
    pass

# Import the 5250 automation module
try:
    from p5250 import P5250Client
    P5250_AVAILABLE = True
except ImportError:
    P5250_AVAILABLE = False
    print("Warning: p5250 module not available. Running in demo mode.")

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('inventory_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# IBM i Connection Configuration
# Load from environment variables (local .env file or Fly.io secrets)
IBM_HOST = os.getenv('IBM_HOST', '10.0.0.7')
IBM_PORT = int(os.getenv('IBM_PORT', '23'))
USER = os.getenv('IBM_USER', 'ROBERT')
PASSWORD = os.getenv('IBM_PASSWORD', 'TECH')

# Redis Configuration for caching
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
    logger.info("Redis cache connected")
except:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available - caching disabled")

# Global statistics
stats = {
    'total_lookups': 0,
    'successful_lookups': 0,
    'cache_hits': 0,
    'errors': 0,
    'avg_response_time': 0,
    'last_error': None,
    'uptime_start': datetime.now()
}

stats_lock = Lock()

def update_stats(success=True, response_time=0, error=None, cache_hit=False):
    """Update global statistics"""
    with stats_lock:
        stats['total_lookups'] += 1
        if success:
            stats['successful_lookups'] += 1
        if cache_hit:
            stats['cache_hits'] += 1
        if error:
            stats['errors'] += 1
            stats['last_error'] = {
                'message': str(error),
                'timestamp': datetime.now().isoformat()
            }
        
        # Update average response time
        if response_time > 0:
            current_avg = stats['avg_response_time']
            total_requests = stats['total_lookups']
            stats['avg_response_time'] = ((current_avg * (total_requests - 1)) + response_time) / total_requests

def cache_key(sku):
    """Generate cache key for SKU"""
    return f"inventory:sku:{sku.upper()}"

def cache_get(sku):
    """Get cached inventory data"""
    if not REDIS_AVAILABLE:
        return None
    
    try:
        cached = redis_client.get(cache_key(sku))
        if cached:
            return json.loads(cached)
    except Exception as e:
        logger.error(f"Cache get error: {e}")
    
    return None

def cache_set(sku, data, ttl=1800):  # 30 minutes TTL
    """Cache inventory data"""
    if not REDIS_AVAILABLE:
        return
    
    try:
        redis_client.setex(cache_key(sku), ttl, json.dumps(data))
    except Exception as e:
        logger.error(f"Cache set error: {e}")

# Command execution logging for debugging
command_log = []
command_log_lock = Lock()

def log_command(command, details=None, result=None, duration=None):
    """Log system commands for debugging"""
    with command_log_lock:
        entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'details': details,
            'result': result,
            'duration': duration
        }
        command_log.append(entry)
        # Keep only last 100 entries
        if len(command_log) > 100:
            command_log.pop(0)
        logger.info(f"CMD: {command} | {details} | Result: {result} | Duration: {duration}")

class InventoryLookupService:
    """Production-ready service for inventory lookups via 5250 protocol"""
    
    def __init__(self):
        self.client = None
        self.connected = False
        self.last_connection_attempt = None
        self.connection_lock = Lock()
        self.network_latency_factor = 1.0  # Adaptive timing multiplier
        self.connection_failures = 0
        
    def adaptive_sleep(self, base_seconds):
        """Sleep with network latency compensation"""
        adjusted_time = base_seconds * self.network_latency_factor
        logger.debug(f"Sleeping for {adjusted_time:.1f}s (base: {base_seconds}s, factor: {self.network_latency_factor:.1f})")
        time.sleep(adjusted_time)
        
    def adjust_network_timing(self, success=True):
        """Adjust timing based on connection success/failure patterns"""
        if success:
            # Gradually reduce latency compensation if connections are working
            self.network_latency_factor = max(1.0, self.network_latency_factor - 0.1)
            self.connection_failures = 0
        else:
            # Increase latency compensation after failures
            self.connection_failures += 1
            self.network_latency_factor = min(3.0, 1.0 + (self.connection_failures * 0.2))
            logger.info(f"Adjusted network timing factor to {self.network_latency_factor:.1f} after {self.connection_failures} failures")
        
    def connect_with_retry(self, max_retries=3):
        """Connect to IBM i with retry logic"""
        if not P5250_AVAILABLE:
            logger.warning("p5250 module not available")
            return False
        
        with self.connection_lock:
            for attempt in range(max_retries):
                try:
                    start_time = time.time()
                    log_command("P5250_CONNECT", f"Connecting to {IBM_HOST}:{IBM_PORT} (attempt {attempt + 1})")
                    logger.info(f"Connection attempt {attempt + 1} to {IBM_HOST}:{IBM_PORT}")
                    
                    # Create new client with optimized timeouts for internet connections
                    log_command("P5250_CONFIG", f"Model: 3279-2, Timeout: 60s, TLS: disabled")
                    logger.info("Using optimized P5250Client configuration for internet latency")
                    self.client = P5250Client(
                        hostName=IBM_HOST,
                        hostPort=str(IBM_PORT),
                        modelName='3279-2',
                        enableTLS='no',
                        timeoutInSec=60  # Increased from 30 to handle network latency
                    )
                    
                    # Connect with timeout protection
                    logger.info("Attempting connection with timeout wrapper...")
                    import threading
                    import signal
                    
                    # Connection result storage
                    connection_result = [False, None]
                    
                    def connect_with_timeout():
                        try:
                            self.client.connect()
                            connection_result[0] = self.client.isConnected()
                            if connection_result[0]:
                                logger.info("P5250Client connected successfully")
                            else:
                                connection_result[1] = "isConnected() returned False"
                        except Exception as e:
                            connection_result[1] = str(e)
                    
                    # Start connection in thread with timeout
                    connect_thread = threading.Thread(target=connect_with_timeout)
                    connect_thread.daemon = True
                    connect_thread.start()
                    connect_thread.join(timeout=30)  # Increased to 30 seconds for internet connections
                    
                    if connect_thread.is_alive():
                        logger.error("Connection attempt timed out after 30 seconds")
                        try:
                            self.client.disconnect()
                        except:
                            pass
                        raise Exception("Connection timed out")
                    
                    if not connection_result[0]:
                        error_msg = connection_result[1] or "Connection failed"
                        logger.error(f"Connection failed: {error_msg}")
                        # Log additional connection details for debugging
                        logger.error(f"Attempting to connect to {IBM_HOST}:{IBM_PORT}")
                        logger.error(f"P5250 timeout setting: 60 seconds")
                        raise Exception(f"Connection failed: {error_msg}")
                    
                    # Handle login sequence
                    if not self.login_sequence():
                        raise Exception("Login sequence failed")
                    
                    self.connected = True
                    self.last_connection_attempt = datetime.now()
                    logger.info("Successfully connected and logged in to IBM i")
                    return True
                    
                except Exception as e:
                    logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                    if self.client:
                        try:
                            self.client.disconnect()
                        except:
                            pass
                        self.client = None
                    
                    if attempt < max_retries - 1:
                        sleep_time = 2 ** attempt  # Exponential backoff
                        logger.info(f"Waiting {sleep_time}s before retry...")
                        time.sleep(sleep_time)
            
            self.connected = False
            return False
    
    def login_sequence(self):
        """Handle complete login sequence with proper timing and field navigation"""
        try:
            # Get initial screen with adaptive timing
            logger.info("Waiting for initial login screen...")
            self.adaptive_sleep(4)  # Use adaptive timing
            screen = self.client.getScreen()
            
            if "User" not in screen and "Sign On" not in screen:
                logger.warning("No clear login screen detected, proceeding anyway")
            
            # Clear the screen first to ensure clean state
            log_command("P5250_CLEAR", "Clearing screen for clean login")
            self.client.clearScreen()
            self.adaptive_sleep(1)
            
            # Enter credentials with improved timing and field handling
            log_command("P5250_LOGIN", f"Entering credentials for user: {USER}")
            logger.info("Entering login credentials with improved sequence")
            
            # Move to first input field and enter username
            log_command("P5250_CURSOR", "Moving to first input field")
            self.client.moveToFirstInputField()
            self.adaptive_sleep(0.8)  # Increased delay for internet connections
            
            # Alternative: Try coordinate-based positioning for username
            try:
                # Based on telnet test: username appears at position [6;53H
                log_command("P5250_POSITION", "Using exact coordinates from telnet analysis")
                self.client.moveTo(6, 53)  # Exact position from telnet output
                self.adaptive_sleep(0.3)
                log_command("P5250_POSITION_SUCCESS", "Positioned cursor at exact username coordinates")
            except Exception as e:
                log_command("P5250_POSITION_FALLBACK", f"Coordinate positioning failed: {e}")
                pass  # Fall back to moveToFirstInputField if coordinates fail
            
            log_command("P5250_INPUT", f"Sending username: {USER}")
            self.client.sendText(USER)
            self.adaptive_sleep(0.8)  # Increased processing time for username
            
            # Move to password field using cursor positioning (like 5250 emulator)
            log_command("P5250_CURSOR_DOWN", "Moving to password field with cursor down")
            
            # Method 1: Direct cursor down movement (most reliable - like 5250 emulator)
            self.client.moveCursorDown()
            self.adaptive_sleep(0.5)
            log_command("P5250_CURSOR_SUCCESS", "Cursor down movement completed")
            
            # Verify cursor position by checking screen content
            try:
                screen_check = self.client.getScreen()
                if "Password" in screen_check:
                    log_command("P5250_FIELD_VERIFY", "Confirmed cursor is at password field")
                else:
                    # If not at password field, try alternative positioning
                    log_command("P5250_ALT_POSITION", "Trying alternative password field positioning")
                    # Try common 5250 password field coordinates
                    self.client.moveTo(7, 53)  # Based on telnet output showing position 7;53
                    self.adaptive_sleep(0.5)
            except Exception as e:
                log_command("P5250_POSITION_WARNING", f"Field verification failed: {e}")
            
            # Clear any potential field contamination before password entry
            log_command("P5250_CLEAR_FIELD", "Clearing current field before password")
            try:
                # Try to clear current field in case of overwrite
                self.client.sendText("")  # Clear with empty string
                self.adaptive_sleep(0.3)
            except:
                pass
                
            # Enter password
            log_command("P5250_INPUT", "Sending password: [REDACTED]")
            self.client.sendText(PASSWORD)
            self.adaptive_sleep(0.5)  # Allow password field to process
            
            # Submit the login form
            log_command("P5250_ENTER", "Submitting login credentials")
            self.client.sendEnter()
            logger.info("Credentials sent, waiting for authentication...")
            self.adaptive_sleep(6)  # Extended wait for authentication processing
            
            # Handle post-login sequence with more steps and better timing
            for step in range(10):  # Increased from 5 to 10 steps
                screen = self.client.getScreen()
                screen_upper = screen.upper()
                
                logger.debug(f"Login step {step + 1}: {screen[:100]}...")
                
                if "MESSAGE QUEUE" in screen_upper and "ALLOCATED" in screen_upper:
                    logger.info("Handling message queue allocation")
                    self.client.sendEnter()
                    time.sleep(3)  # Increased timing
                    continue
                
                elif "BEGIN AN A+ SESSION" in screen_upper and "BASE" in screen_upper:
                    log_command("P5250_MENU", "Found Infor base selection screen")
                    logger.info("Confirming Infor base selection")
                    log_command("P5250_ENTER", "Confirming Infor base selection")
                    self.client.sendEnter()
                    time.sleep(4)  # Increased timing for menu loading
                    continue
                
                elif "ENVIRONMENT ID" in screen_upper:
                    logger.info("Confirming environment")
                    self.client.sendEnter()
                    time.sleep(4)  # Increased timing for environment setup
                    continue
                
                elif "MAIN MENU" in screen_upper and "INFOR" in screen_upper:
                    logger.info("Successfully reached Infor main menu")
                    return True
                
                elif "PRESS ENTER" in screen_upper:
                    logger.info("Handling press enter prompt")
                    self.client.sendEnter()
                    time.sleep(3)  # Increased timing
                    continue
                
                # Add more login screen patterns
                elif "SIGN ON" in screen_upper and "SYSTEM" in screen_upper:
                    logger.info("Detected sign-on screen, waiting...")
                    time.sleep(2)
                    continue
                    
                elif "LOADING" in screen_upper or "PLEASE WAIT" in screen_upper:
                    logger.info("System loading, waiting longer...")
                    time.sleep(5)
                    continue
                
                elif any(indicator in screen_upper for indicator in ["NOT VALID", "INVALID", "INCORRECT"]):
                    logger.error("Login failed - invalid credentials")
                    return False
            
            logger.error(f"Login sequence did not complete successfully after {step + 1} steps")
            logger.error(f"Final screen content: {screen[:200]}...")
            return False
            
        except Exception as e:
            logger.error(f"Login sequence error: {e}")
            return False
    
    def navigate_to_inventory_inquiry(self):
        """Navigate to inventory inquiry screen"""
        try:
            logger.info("Navigating to Inventory Accounting (Option 2)")
            self.client.sendText("2")
            self.client.sendEnter()
            time.sleep(4)  # Increased timing for menu navigation
            
            screen = self.client.getScreen()
            if "NOT CORRECT" in screen.upper():
                logger.error("Inventory Accounting option not available")
                return False
            
            logger.info("Navigating to Item Inquiry (Option 11)")
            self.client.sendText("11")
            self.client.sendEnter()
            time.sleep(4)  # Increased timing for screen loading
            
            screen = self.client.getScreen()
            if "NOT CORRECT" in screen.upper():
                logger.error("Item Inquiry option not available")
                return False
            
            logger.info("Successfully navigated to item inquiry")
            return True
            
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return False
    
    def perform_sku_lookup(self, sku):
        """Perform SKU lookup on inquiry screen"""
        try:
            logger.info(f"Looking up SKU: {sku}")
            
            # Enter SKU
            self.client.moveToFirstInputField()
            self.client.sendText(sku.upper())
            self.client.sendEnter()
            logger.info(f"SKU {sku} sent, waiting for response...")
            time.sleep(6)  # Increased from 4 to 6 seconds for query processing
            
            # Get result screen
            result_screen = self.client.getScreen()
            logger.debug(f"Lookup result screen: {result_screen[:200]}...")
            
            return result_screen
            
        except Exception as e:
            logger.error(f"SKU lookup error: {e}")
            return None
    
    def parse_inventory_screen(self, screen_content, sku):
        """Parse inventory data from 5250 screen"""
        try:
            screen_upper = screen_content.upper()
            
            # Check if SKU was found
            if sku.upper() not in screen_content:
                # Check for "not found" indicators
                not_found_indicators = ["NOT FOUND", "NOT ON FILE", "INVALID", "NO RECORD", "DOES NOT EXIST"]
                if any(indicator in screen_upper for indicator in not_found_indicators):
                    return {"found": False, "error": "SKU not found"}
                
                # If no clear indicators, assume not found
                return {"found": False, "error": "SKU not found in system"}
            
            # Initialize result
            result = {
                "found": True,
                "sku": sku.upper(),
                "timestamp": datetime.now().isoformat(),
                "description": "",
                "warehouse": "",
                "unit_of_measure": "",
                "status": "Active",
                "on_hand": 0.0,
                "allocated": 0.0,
                "net_available": 0.0,
                "on_purchase_order": 0.0,
                "on_back_order": 0.0,
                "raw_screen": screen_content
            }
            
            lines = screen_content.split('\n')
            
            # Parse inventory status screen format
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                line_upper = line.upper()
                
                # Look for item description (usually contains the SKU)
                if sku.upper() in line_upper and not result["description"]:
                    # Extract description - typically everything after the SKU
                    parts = line.split()
                    try:
                        sku_index = next(j for j, part in enumerate(parts) if sku.upper() in part.upper())
                        if sku_index + 1 < len(parts):
                            result["description"] = " ".join(parts[sku_index + 1:]).strip()
                    except:
                        result["description"] = line.replace(sku.upper(), "").strip()
                
                # Look for warehouse and quantity data (format: WH U/M S On Hand Alloc Net Avail On P/O On B/O)
                if re.match(r'\s*\d{2}\s+[A-Z]{2}\s+', line):  # Warehouse line format
                    parts = line.split()
                    if len(parts) >= 6:  # Need at least 6 parts for full data
                        try:
                            result["warehouse"] = parts[0]
                            result["unit_of_measure"] = parts[1]
                            result["on_hand"] = float(parts[3])
                            result["allocated"] = float(parts[4])
                            result["net_available"] = float(parts[5])
                            if len(parts) > 6:
                                result["on_purchase_order"] = float(parts[6])
                            if len(parts) > 7:
                                result["on_back_order"] = float(parts[7])
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Error parsing quantities from line: {line} - {e}")
                
                # Alternative parsing for different screen formats
                elif "ON HAND" in line_upper:
                    # Try to extract numeric values from the line
                    numbers = re.findall(r'(\d+(?:\.\d+)?)', line)
                    if numbers:
                        try:
                            result["on_hand"] = float(numbers[0])
                            if len(numbers) > 1:
                                result["allocated"] = float(numbers[1])
                            if len(numbers) > 2:
                                result["net_available"] = float(numbers[2])
                        except ValueError:
                            pass
            
            # If we didn't get warehouse from structured line, try to find it
            if not result["warehouse"]:
                for line in lines:
                    wh_match = re.search(r'WH\s*(\d{2})', line.upper())
                    if wh_match:
                        result["warehouse"] = wh_match.group(1)
                        break
            
            # Calculate net available if not already set
            if result["net_available"] == 0.0 and result["on_hand"] > 0:
                result["net_available"] = result["on_hand"] - result["allocated"]
            
            logger.info(f"Successfully parsed inventory for {sku}: {result['on_hand']} on hand, {result['net_available']} available")
            return result
            
        except Exception as e:
            logger.error(f"Screen parsing error: {e}")
            return {"found": False, "error": f"Parsing error: {str(e)}"}
    
    def lookup_sku(self, sku):
        """Main SKU lookup method with full error handling"""
        start_time = time.time()
        
        # Check cache first
        cached_result = cache_get(sku)
        if cached_result:
            logger.info(f"Cache hit for SKU {sku}")
            update_stats(success=True, response_time=time.time() - start_time, cache_hit=True)
            return cached_result
        
        result = {
            "sku": sku.upper(),
            "found": False,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Ensure connection with detailed logging
            if not self.connected:
                logger.info(f"Not connected, attempting connection to {IBM_HOST}:{IBM_PORT}")
                if not self.connect_with_retry():
                    error_msg = "Could not connect to inventory system"
                    logger.error(f"{error_msg} - Host: {IBM_HOST}, Port: {IBM_PORT}")
                    result["error"] = error_msg
                    update_stats(success=False, error="Connection failed")
                    return result
                else:
                    logger.info("Successfully established connection to IBM i")
            
            # Navigate to inventory inquiry with better error handling
            logger.info("Attempting to navigate to inventory inquiry screen")
            if not self.navigate_to_inventory_inquiry():
                error_msg = "Could not navigate to inventory inquiry"
                logger.error(f"{error_msg} - May need to retry connection")
                result["error"] = error_msg
                update_stats(success=False, error="Navigation failed")
                # Mark connection as failed for retry on next request
                self.connected = False
                return result
            
            # Perform lookup
            screen_data = self.perform_sku_lookup(sku)
            if not screen_data:
                result["error"] = "Failed to retrieve screen data"
                update_stats(success=False, error="Screen retrieval failed")
                return result
            
            # Parse results
            parsed_result = self.parse_inventory_screen(screen_data, sku)
            result.update(parsed_result)
            
            # Cache successful results
            if result.get("found"):
                cache_set(sku, result)
                logger.info(f"Successfully retrieved and cached inventory for SKU {sku}")
                update_stats(success=True, response_time=time.time() - start_time)
            else:
                logger.warning(f"SKU {sku} not found in inventory")
                update_stats(success=False, error="SKU not found")
            
            return result
            
        except Exception as e:
            logger.error(f"Lookup failed for SKU {sku}: {e}")
            result["error"] = str(e)
            update_stats(success=False, error=str(e))
            
            # Try to reconnect on error
            self.connected = False
            if self.client:
                try:
                    self.client.disconnect()
                except:
                    pass
                self.client = None
            
            return result
    
    def disconnect(self):
        """Safely disconnect from IBM i system"""
        with self.connection_lock:
            if self.client:
                try:
                    self.client.disconnect()
                    logger.info("Disconnected from IBM i")
                except:
                    pass
                self.client = None
            self.connected = False

# Initialize service
inventory_service = InventoryLookupService()

def require_sku(f):
    """Decorator to validate SKU parameter"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.json if request.is_json else {}
        sku = data.get('sku', '').strip()
        
        if not sku:
            return jsonify({"error": "SKU is required"}), 400
        
        # Validate SKU format
        if not re.match(r'^[A-Z0-9]{3,15}$', sku.upper()):
            return jsonify({"error": "Invalid SKU format. Use alphanumeric characters, 3-15 length."}), 400
        
        return f(sku, *args, **kwargs)
    return decorated_function

@app.route('/api/inventory/status', methods=['GET'])
def get_status():
    """Check system status"""
    return jsonify({
        "available": P5250_AVAILABLE,
        "connected": inventory_service.connected,
        "redis_available": REDIS_AVAILABLE,
        "host": IBM_HOST,
        "uptime": str(datetime.now() - stats['uptime_start']),
        "stats": stats,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/inventory/lookup', methods=['POST'])
@require_sku
def lookup_inventory(sku):
    """Look up inventory for a SKU"""
    logger.info(f"Received lookup request for SKU: {sku}")
    result = inventory_service.lookup_sku(sku)
    
    if "error" in result and not result.get("found"):
        return jsonify(result), 404
    
    return jsonify(result)

@app.route('/api/inventory/bulk', methods=['POST'])
def bulk_lookup():
    """Bulk SKU lookup"""
    data = request.json
    skus = data.get('skus', [])
    
    if not skus or not isinstance(skus, list):
        return jsonify({"error": "SKUs array is required"}), 400
    
    if len(skus) > 50:  # Limit bulk requests
        return jsonify({"error": "Maximum 50 SKUs per request"}), 400
    
    results = {}
    for sku in skus:
        sku = sku.strip().upper()
        if re.match(r'^[A-Z0-9]{3,15}$', sku):
            results[sku] = inventory_service.lookup_sku(sku)
        else:
            results[sku] = {"error": "Invalid SKU format", "found": False}
    
    return jsonify({"results": results, "count": len(results)})

@app.route('/api/inventory/cache/clear', methods=['POST'])
def clear_cache():
    """Clear inventory cache"""
    if not REDIS_AVAILABLE:
        return jsonify({"error": "Redis not available"}), 503
    
    try:
        keys = redis_client.keys("inventory:sku:*")
        if keys:
            redis_client.delete(*keys)
        return jsonify({"message": f"Cleared {len(keys)} cached entries"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/inventory/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "p5250": P5250_AVAILABLE,
            "redis": REDIS_AVAILABLE,
            "ibm_connection": inventory_service.connected
        }
    }
    
    # Check if any critical services are down
    if not P5250_AVAILABLE:
        health_status["status"] = "degraded"
        health_status["issues"] = ["p5250 module not available"]
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return jsonify(health_status), status_code

@app.route('/api/inventory/metrics', methods=['GET'])
def get_metrics():
    """Get performance metrics"""
    return jsonify({
        "metrics": stats,
        "cache_info": {
            "redis_available": REDIS_AVAILABLE,
            "cache_hit_rate": (stats['cache_hits'] / max(stats['total_lookups'], 1)) * 100
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/inventory/recent', methods=['GET'])
def get_recent_lookups():
    """Get recent lookup history from cache"""
    if not REDIS_AVAILABLE:
        return jsonify({"error": "Redis not available"}), 503
    
    try:
        keys = redis_client.keys("inventory:sku:*")
        recent_lookups = []
        
        for key in keys[:20]:  # Limit to 20 recent
            data = redis_client.get(key)
            if data:
                lookup_data = json.loads(data)
                recent_lookups.append({
                    "sku": lookup_data.get("sku"),
                    "description": lookup_data.get("description"),
                    "on_hand": lookup_data.get("on_hand"),
                    "timestamp": lookup_data.get("timestamp")
                })
        
        return jsonify({"recent_lookups": recent_lookups})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/inventory/commands', methods=['GET'])
def get_command_log():
    """Get real-time command execution log"""
    with command_log_lock:
        # Return last 50 commands with most recent first
        recent_commands = list(reversed(command_log[-50:]))
        
        return jsonify({
            'commands': recent_commands,
            'total_count': len(command_log),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/inventory/commands/clear', methods=['POST'])
def clear_command_log():
    """Clear command execution log"""
    with command_log_lock:
        command_log.clear()
        log_command("SYSTEM", "Command log cleared by admin")
        
    return jsonify({
        'success': True,
        'message': 'Command log cleared',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint for inventory queries"""
    data = request.json
    message = data.get('message', '').strip()
    
    log_command("API_CHAT", f"Processing message: {message[:50]}...")
    
    response = {
        "success": True,
        "message": "Please provide a SKU to look up inventory."
    }
    
    # Extract SKU from message
    sku_match = re.search(r'\b([A-Z0-9]{6,12})\b', message.upper())
    
    if sku_match:
        sku = sku_match.group(1)
        result = inventory_service.lookup_sku(sku)
        
        if result.get('found'):
            available_status = "✅ In Stock" if result.get('net_available', 0) > 0 else "⚠️ Out of Stock"
            response['message'] = (
                f"📦 **{sku}** - {result.get('description', 'No description')}\n\n"
                f"🏭 **Warehouse:** {result.get('warehouse', 'N/A')}\n"
                f"📊 **Status:** {available_status}\n\n"
                f"**Quantities:**\n"
                f"• On Hand: {result.get('on_hand', 0)} {result.get('unit_of_measure', 'EA')}\n"
                f"• Allocated: {result.get('allocated', 0)}\n"
                f"• Available: {result.get('net_available', 0)}\n"
                f"• On Purchase Order: {result.get('on_purchase_order', 0)}\n"
                f"• On Back Order: {result.get('on_back_order', 0)}\n\n"
                f"⏱️ *Retrieved: {datetime.now().strftime('%H:%M:%S')}*"
            )
        else:
            response['message'] = f"❌ SKU {sku} not found in inventory system."
    
    return jsonify(response)

# Cleanup on exit
import atexit
atexit.register(inventory_service.disconnect)

if __name__ == '__main__':
    # Use environment variable for port, defaulting to 5001 to avoid conflicts
    api_port = int(os.environ.get('API_PORT', '5001'))
    
    print("🚀 Starting WC Ducomb Inventory Lookup API...")
    print(f"📡 p5250 Available: {P5250_AVAILABLE}")
    print(f"💾 Redis Available: {REDIS_AVAILABLE}")
    print(f"🖥️  IBM i Host: {IBM_HOST}")
    print(f"🔗 API running at http://localhost:{api_port}")
    print(f"📊 Admin panel: http://localhost:{api_port}/admin")
    
    # Initialize the service first
    print("🔧 Initializing inventory service...")
    
    # Test connection on startup
    if P5250_AVAILABLE:
        print("🔌 Testing IBM i connection...")
        try:
            if inventory_service.connect_with_retry(max_retries=1):
                print("✅ Successfully connected to IBM i system")
            else:
                print("⚠️ Could not connect to IBM i - running in offline mode")
        except Exception as e:
            print(f"⚠️ Connection test failed: {e} - running in offline mode")
    else:
        print("⚠️ P5250 module not available - running in demo mode")
    
    print(f"🎯 Starting Flask app on 0.0.0.0:{api_port}")
    try:
        app.run(host='0.0.0.0', port=api_port, debug=False, threaded=True)
    except Exception as e:
        print(f"❌ Failed to start Flask app: {e}")
        import traceback
        traceback.print_exc()