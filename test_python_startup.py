#!/usr/bin/env python3
"""
Test Python API startup independently
"""

import os
import sys
import traceback

# Set environment for testing
os.environ['IBM_HOST'] = '216.176.21.86'  # Use the correct IP from your telnet test
os.environ['IBM_PORT'] = '23'
os.environ['IBM_USER'] = 'ROBERT'
os.environ['IBM_PASSWORD'] = 'TECH'

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

print("🧪 Testing Python API startup...")

try:
    print("1. Testing imports...")
    from inventory_lookup import app, inventory_service, P5250_AVAILABLE
    print("✅ Imports successful")
    print(f"   P5250_AVAILABLE: {P5250_AVAILABLE}")
    
    print("2. Testing Flask app creation...")
    print(f"   Flask app: {app}")
    print("✅ Flask app created successfully")
    
    print("3. Testing inventory service...")
    print(f"   Service connected: {inventory_service.connected}")
    print("✅ Inventory service initialized")
    
    print("🎉 Python API startup test passed!")
    
except Exception as e:
    print(f"❌ Startup test failed: {e}")
    traceback.print_exc()
    sys.exit(1)