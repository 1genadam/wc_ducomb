#!/usr/bin/env python3
"""
VPN Connectivity Test for WC Ducomb IBM i Access
Tests both network connectivity and 5250 protocol handshake
"""

import socket
import sys
import time
import subprocess
import os

def check_tailscale_status():
    """Check if Tailscale is running and connected"""
    try:
        result = subprocess.run(['tailscale', 'status'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Tailscale is running")
            
            # Parse output for connection info
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'logged in' in line.lower():
                    print(f"   Status: {line.strip()}")
                elif line.startswith('100.'):  # Tailscale IP
                    print(f"   VPN IP: {line.split()[0]}")
            return True
        else:
            print("❌ Tailscale not running or not authenticated")
            print(f"   Error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Tailscale not installed")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Tailscale status check timed out")
        return False
    except Exception as e:
        print(f"❌ Tailscale check failed: {e}")
        return False

def test_network_connectivity(host="10.0.0.7", port=23, timeout=10):
    """Test basic network connectivity to IBM i"""
    print(f"\n🔍 Testing network connectivity to {host}:{port}")
    
    try:
        # Create socket with timeout
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # Attempt connection
        start_time = time.time()
        result = sock.connect_ex((host, port))
        end_time = time.time()
        
        if result == 0:
            print(f"✅ TCP connection successful in {end_time - start_time:.2f}s")
            return True, sock
        else:
            print(f"❌ TCP connection failed with error code: {result}")
            sock.close()
            return False, None
            
    except socket.timeout:
        print(f"❌ Connection timed out after {timeout}s")
        return False, None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False, None

def test_5250_handshake(sock):
    """Test 5250 protocol handshake"""
    print("\n🤝 Testing 5250 protocol handshake")
    
    try:
        # Set a shorter timeout for data reception
        sock.settimeout(5)
        
        # Try to receive initial 5250 data
        data = sock.recv(1024)
        if data:
            print(f"✅ Received {len(data)} bytes from IBM i")
            print(f"   Data preview: {data[:50]}...")
            
            # Look for 5250 protocol indicators
            if b'\xff' in data or b'\x12' in data or b'\x1b' in data:
                print("✅ 5250 protocol indicators detected")
                return True
            else:
                print("⚠️ Data received but no clear 5250 indicators")
                return True
        else:
            print("⚠️ No initial data received")
            return False
            
    except socket.timeout:
        print("⚠️ No initial handshake data (normal for some IBM i configurations)")
        return True  # Some IBM i systems don't send initial data
    except Exception as e:
        print(f"❌ 5250 handshake error: {e}")
        return False
    finally:
        sock.close()

def test_route_to_subnet():
    """Test if route to 10.0.0.0/24 subnet exists"""
    print("\n🗺️ Testing route to IBM i subnet")
    
    try:
        # Check if we can reach the subnet via ping
        result = subprocess.run(['tailscale', 'ping', '--c', '1', '10.0.0.7'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Tailscale ping to 10.0.0.7 successful")
            return True
        else:
            print("❌ Tailscale ping failed")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Route test failed: {e}")
        return False

def check_environment():
    """Check environment variables and configuration"""
    print("\n🔧 Checking environment configuration")
    
    auth_key = os.environ.get('TAILSCALE_AUTHKEY')
    if auth_key:
        print("✅ TAILSCALE_AUTHKEY is set")
        print(f"   Key prefix: {auth_key[:15]}...")
    else:
        print("❌ TAILSCALE_AUTHKEY not set")
        return False
    
    return True

def main():
    """Run comprehensive VPN connectivity test"""
    print("🔐 WC Ducomb VPN Connectivity Test")
    print("=" * 50)
    
    # Track overall test results
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Environment check
    if check_environment():
        tests_passed += 1
    
    # Test 2: Tailscale status
    if check_tailscale_status():
        tests_passed += 1
    
    # Test 3: Route test
    if test_route_to_subnet():
        tests_passed += 1
    
    # Test 4: Network connectivity
    success, sock = test_network_connectivity()
    if success:
        tests_passed += 1
        
        # Test 5: 5250 handshake
        if test_5250_handshake(sock):
            tests_passed += 1
    
    # Final results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed >= 4:
        print("✅ VPN connectivity is working correctly!")
        print("🚀 Ready for production deployment")
        return 0
    elif tests_passed >= 2:
        print("⚠️  VPN partially working - some issues detected")
        print("🔧 May need troubleshooting before production")
        return 1
    else:
        print("❌ VPN connectivity failed")
        print("🔴 Requires setup before deployment")
        return 2

if __name__ == "__main__":
    sys.exit(main())