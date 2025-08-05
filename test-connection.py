#!/usr/bin/env python3

import socket
import sys
import time

def test_ibm_connection(host="10.0.0.7", port=23, timeout=10):
    """Test connection to IBM i system via VPN"""
    
    print(f"Testing connection to {host}:{port}")
    
    try:
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # Attempt connection
        start_time = time.time()
        result = sock.connect_ex((host, port))
        end_time = time.time()
        
        if result == 0:
            print(f"✓ Connection successful in {end_time - start_time:.2f}s")
            
            # Try to receive initial 5250 handshake
            try:
                data = sock.recv(1024)
                print(f"✓ Received {len(data)} bytes from IBM i")
                print(f"Data preview: {data[:50]}...")
            except:
                print("! No initial data received (normal for some 5250 implementations)")
                
            return True
        else:
            print(f"✗ Connection failed with error code: {result}")
            return False
            
    except socket.timeout:
        print(f"✗ Connection timed out after {timeout}s")
        return False
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False
    finally:
        sock.close()

def check_network_route():
    """Check if route to IBM i network exists"""
    import subprocess
    
    try:
        result = subprocess.run(['ip', 'route', 'get', '10.0.0.7'], 
                              capture_output=True, text=True)
        print(f"Route to IBM i: {result.stdout.strip()}")
        return 'wg0' in result.stdout
    except:
        print("Could not check routing table")
        return False

if __name__ == "__main__":
    print("IBM i 5250 Connection Test via VPN")
    print("=" * 40)
    
    # Check VPN route
    if check_network_route():
        print("✓ VPN route detected")
    else:
        print("! No VPN route found - check WireGuard status")
    
    # Test connection
    success = test_ibm_connection()
    
    if success:
        print("\n✓ VPN tunnel is working correctly")
        sys.exit(0)
    else:
        print("\n✗ VPN tunnel needs troubleshooting")
        sys.exit(1)