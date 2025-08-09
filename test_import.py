#!/usr/bin/env python3
"""
Test P5250 module imports correctly
"""

import sys
import os

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

try:
    print("Testing p5250 module import...")
    from p5250 import P5250Client
    print("✅ p5250 module imported successfully")
    
    print("Testing P5250Client instantiation...")
    client = P5250Client("test.host", "23")
    print("✅ P5250Client created successfully")
    
    print("Testing inventory_lookup import...")
    from inventory_lookup import InventoryLookupService
    print("✅ inventory_lookup imported successfully")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Other error: {e}")
    sys.exit(1)

print("🎉 All imports working correctly!")