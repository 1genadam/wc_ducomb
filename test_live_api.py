#!/usr/bin/env python3
"""
Live API Test for WC Ducomb Inventory System
Tests the production-ready implementation with real 5250 connection
"""

import requests
import json
import time

def test_api_endpoints():
    """Test all API endpoints"""
    
    base_url = "http://localhost:5000/api/inventory"
    
    print("🧪 Testing WC Ducomb Inventory API")
    print("="*50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: System Status
    print("\n2. Testing System Status...")
    try:
        response = requests.get(f"{base_url}/status", timeout=10)
        if response.status_code == 200:
            print("✅ Status check passed")
            status_data = response.json()
            print(f"   p5250 Available: {status_data.get('available')}")
            print(f"   IBM i Connected: {status_data.get('connected')}")
            print(f"   Redis Available: {status_data.get('redis_available')}")
            print(f"   Host: {status_data.get('host')}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status check error: {e}")
    
    # Test 3: SKU Lookup - DGE037700
    print("\n3. Testing SKU Lookup (DGE037700)...")
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/lookup",
            json={"sku": "DGE037700"},
            timeout=60
        )
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ SKU lookup successful ({response_time:.2f}s)")
            lookup_data = response.json()
            
            if lookup_data.get('found'):
                print(f"   SKU: {lookup_data.get('sku')}")
                print(f"   Description: {lookup_data.get('description')}")
                print(f"   Warehouse: {lookup_data.get('warehouse')}")
                print(f"   On Hand: {lookup_data.get('on_hand')} {lookup_data.get('unit_of_measure', 'EA')}")
                print(f"   Available: {lookup_data.get('net_available')}")
                print(f"   Allocated: {lookup_data.get('allocated')}")
                print(f"   On P/O: {lookup_data.get('on_purchase_order')}")
                print(f"   On B/O: {lookup_data.get('on_back_order')}")
            else:
                print("   SKU not found in system")
                if 'error' in lookup_data:
                    print(f"   Error: {lookup_data['error']}")
        else:
            print(f"❌ SKU lookup failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ SKU lookup error: {e}")
    
    # Test 4: Invalid SKU
    print("\n4. Testing Invalid SKU...")
    try:
        response = requests.post(
            f"{base_url}/lookup",
            json={"sku": "INVALID123"},
            timeout=30
        )
        
        if response.status_code == 404:
            print("✅ Invalid SKU handled correctly (404)")
        elif response.status_code == 200:
            data = response.json()
            if not data.get('found'):
                print("✅ Invalid SKU handled correctly (not found)")
            else:
                print("⚠️ Invalid SKU returned data unexpectedly")
        else:
            print(f"❌ Invalid SKU test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid SKU test error: {e}")
    
    # Test 5: Chat Endpoint
    print("\n5. Testing Chat Endpoint...")
    try:
        response = requests.post(
            f"http://localhost:5000/api/chat",
            json={"message": "What is the inventory for DGE037700?"},
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ Chat endpoint successful")
            chat_data = response.json()
            print(f"   Success: {chat_data.get('success')}")
            print(f"   Message: {chat_data.get('message')[:100]}...")
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
    
    # Test 6: Metrics
    print("\n6. Testing Metrics...")
    try:
        response = requests.get(f"{base_url}/metrics", timeout=10)
        if response.status_code == 200:
            print("✅ Metrics endpoint successful")
            metrics_data = response.json()
            metrics = metrics_data.get('metrics', {})
            print(f"   Total Lookups: {metrics.get('total_lookups', 0)}")
            print(f"   Successful: {metrics.get('successful_lookups', 0)}")
            print(f"   Cache Hits: {metrics.get('cache_hits', 0)}")
            print(f"   Errors: {metrics.get('errors', 0)}")
            print(f"   Avg Response: {metrics.get('avg_response_time', 0):.3f}s")
        else:
            print(f"❌ Metrics failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Metrics error: {e}")
    
    print("\n🏁 API Testing Complete!")
    print("="*50)

if __name__ == "__main__":
    print("Starting API test suite...")
    print("Make sure the inventory API is running at http://localhost:5000")
    print()
    
    # Wait a moment for user to start the API if needed
    try:
        test_api_endpoints()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")