#!/usr/bin/env python3
"""
Test the fixed P5250 login sequence
"""

import sys
import os
sys.path.insert(0, 'api')

from p5250 import P5250Client
import time

# Configuration
HOST = os.environ.get('IBM_HOST', '216.176.21.86')
PORT = os.environ.get('IBM_PORT', '23')
USER = os.environ.get('IBM_USER', 'ROBERT')
PASSWORD = os.environ.get('IBM_PASSWORD', 'TECH')

print(f"🔌 Testing P5250 Login Fix")
print(f"🎯 Host: {HOST}:{PORT}")
print(f"👤 User: {USER}")
print(f"🔑 Password: [REDACTED]")
print("=" * 50)

try:
    # Create client
    client = P5250Client(
        hostName=HOST,
        hostPort=PORT,
        timeoutInSec=30
    )
    
    # Connect
    print("🔗 Connecting...")
    client.connect()
    
    if not client.isConnected():
        print("❌ Connection failed")
        exit(1)
    
    print("✅ Connected successfully")
    
    # Wait for initial screen
    print("⏳ Waiting for login screen...")
    time.sleep(3)
    initial_screen = client.getScreen()
    print(f"📺 Initial screen: {initial_screen[:100]}...")
    
    # Perform login
    print("🔐 Attempting login...")
    login_result = client.login(USER, PASSWORD)
    
    if login_result:
        print("✅ Login successful!")
        
        # Get post-login screen
        time.sleep(2)
        post_login_screen = client.getScreen()
        print("📺 Post-login screen:")
        print("=" * 50)
        print(post_login_screen[:500])
        print("=" * 50)
        
    else:
        print("❌ Login failed")
    
    # Disconnect
    client.disconnect()
    print("🔌 Disconnected")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()