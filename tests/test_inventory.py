#!/usr/bin/env python3
"""
Unit tests for WC Ducomb Inventory Lookup System
Tests the 5250 protocol integration and screen parsing logic
"""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from inventory_lookup import InventoryLookupService, cache_key, cache_get, cache_set

class TestInventoryLookupService(unittest.TestCase):
    """Test the main inventory lookup service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = InventoryLookupService()
        self.test_sku = "DGE037700"
        self.sample_screen_content = """
                               INVENTORY STATUS                                 
                                                                                
 WH U/M S      On Hand         Alloc     Net Avail         On P/O        On B/O 
 00 EA           6.000          .000         6.000           .000          .000 
                                                                                
ITEM:                    P2B-SC-100 1SC 123806                                  
        """
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        key = cache_key("DGE037700")
        self.assertEqual(key, "inventory:sku:DGE037700")
        
        # Test lowercase conversion
        key = cache_key("dge037700")
        self.assertEqual(key, "inventory:sku:DGE037700")
    
    def test_parse_inventory_screen_success(self):
        """Test successful screen parsing"""
        result = self.service.parse_inventory_screen(self.sample_screen_content, self.test_sku)
        
        self.assertTrue(result["found"])
        self.assertEqual(result["sku"], "DGE037700")
        self.assertEqual(result["warehouse"], "00")
        self.assertEqual(result["unit_of_measure"], "EA")
        self.assertEqual(result["on_hand"], 6.0)
        self.assertEqual(result["allocated"], 0.0)
        self.assertEqual(result["net_available"], 6.0)
        self.assertEqual(result["on_purchase_order"], 0.0)
        self.assertEqual(result["on_back_order"], 0.0)
        self.assertIn("P2B-SC-100 1SC 123806", result["description"])
    
    def test_parse_inventory_screen_not_found(self):
        """Test screen parsing when SKU not found"""
        not_found_screen = "Item not found in inventory system"
        result = self.service.parse_inventory_screen(not_found_screen, "INVALID123")
        
        self.assertFalse(result["found"])
        self.assertIn("error", result)
    
    def test_parse_inventory_screen_invalid_format(self):
        """Test screen parsing with invalid format"""
        invalid_screen = "Some random text that doesn't match expected format"
        result = self.service.parse_inventory_screen(invalid_screen, "TEST123")
        
        # Should still return found=False since SKU not in screen
        self.assertFalse(result["found"])
    
    @patch('inventory_lookup.P5250Client')
    def test_login_sequence_success(self, mock_p5250_client):
        """Test successful login sequence"""
        # Mock client
        mock_client = Mock()
        mock_p5250_client.return_value = mock_client
        
        # Mock screen responses for login sequence
        login_screens = [
            "User  . . . . . . . . . . . . . .",  # Initial login
            "Message queue ROBERT is allocated to another job.",  # Message queue
            "BEGIN AN A+ SESSION Base?  13  Aplus V10.03.01",  # Base selection
            "Environment ID?  DC  A+ LIVE AT V10.03.01",  # Environment
            "COMMAND Infor Distribution A+ - Main Menu"  # Success
        ]
        
        mock_client.getScreen.side_effect = login_screens
        mock_client.isConnected.return_value = True
        
        self.service.client = mock_client
        result = self.service.login_sequence()
        
        self.assertTrue(result)
        
        # Verify login sequence calls
        mock_client.moveToFirstInputField.assert_called_once()
        mock_client.sendText.assert_any_call("ROBERT")
        mock_client.sendTab.assert_called_once()
        mock_client.sendText.assert_any_call("TECH")
        self.assertGreaterEqual(mock_client.sendEnter.call_count, 4)
    
    @patch('inventory_lookup.P5250Client')
    def test_login_sequence_failure(self, mock_p5250_client):
        """Test failed login sequence"""
        mock_client = Mock()
        mock_p5250_client.return_value = mock_client
        
        # Mock failed login
        mock_client.getScreen.return_value = "Password not valid for user ROBERT"
        mock_client.isConnected.return_value = True
        
        self.service.client = mock_client
        result = self.service.login_sequence()
        
        self.assertFalse(result)
    
    @patch('inventory_lookup.P5250Client')
    def test_navigate_to_inventory_inquiry_success(self, mock_p5250_client):
        """Test successful navigation to inventory inquiry"""
        mock_client = Mock()
        self.service.client = mock_client
        
        # Mock navigation responses
        mock_client.getScreen.side_effect = [
            "Inventory Accounting Menu",  # After option 2
            "Item Inquiry Screen"  # After option 11
        ]
        
        result = self.service.navigate_to_inventory_inquiry()
        
        self.assertTrue(result)
        mock_client.sendText.assert_any_call("2")
        mock_client.sendText.assert_any_call("11")
        self.assertEqual(mock_client.sendEnter.call_count, 2)
    
    @patch('inventory_lookup.P5250Client')
    def test_navigate_to_inventory_inquiry_failure(self, mock_p5250_client):
        """Test failed navigation to inventory inquiry"""
        mock_client = Mock()
        self.service.client = mock_client
        
        # Mock navigation failure
        mock_client.getScreen.return_value = "Specified menu selection is not correct."
        
        result = self.service.navigate_to_inventory_inquiry()
        
        self.assertFalse(result)
    
    @patch('inventory_lookup.P5250Client')
    def test_perform_sku_lookup_success(self, mock_p5250_client):
        """Test successful SKU lookup"""
        mock_client = Mock()
        self.service.client = mock_client
        
        mock_client.getScreen.return_value = self.sample_screen_content
        
        result = self.service.perform_sku_lookup(self.test_sku)
        
        self.assertEqual(result, self.sample_screen_content)
        mock_client.moveToFirstInputField.assert_called_once()
        mock_client.sendText.assert_called_with("DGE037700")
        mock_client.sendEnter.assert_called_once()
    
    @patch('inventory_lookup.cache_get')
    @patch('inventory_lookup.cache_set')
    @patch.object(InventoryLookupService, 'connect_with_retry')
    @patch.object(InventoryLookupService, 'navigate_to_inventory_inquiry')
    @patch.object(InventoryLookupService, 'perform_sku_lookup')
    @patch.object(InventoryLookupService, 'parse_inventory_screen')
    def test_lookup_sku_cache_hit(self, mock_parse, mock_perform, mock_navigate, mock_connect, mock_cache_set, mock_cache_get):
        """Test SKU lookup with cache hit"""
        # Mock cache hit
        cached_result = {
            "sku": "DGE037700",
            "found": True,
            "description": "Cached item",
            "on_hand": 5.0
        }
        mock_cache_get.return_value = cached_result
        
        result = self.service.lookup_sku(self.test_sku)
        
        self.assertEqual(result, cached_result)
        # Should not call connect or navigate since cache hit
        mock_connect.assert_not_called()
        mock_navigate.assert_not_called()
        mock_perform.assert_not_called()
    
    @patch('inventory_lookup.cache_get')
    @patch('inventory_lookup.cache_set')
    @patch.object(InventoryLookupService, 'connect_with_retry')
    @patch.object(InventoryLookupService, 'navigate_to_inventory_inquiry')
    @patch.object(InventoryLookupService, 'perform_sku_lookup')
    @patch.object(InventoryLookupService, 'parse_inventory_screen')
    def test_lookup_sku_cache_miss_success(self, mock_parse, mock_perform, mock_navigate, mock_connect, mock_cache_set, mock_cache_get):
        """Test SKU lookup with cache miss but successful lookup"""
        # Mock cache miss
        mock_cache_get.return_value = None
        
        # Mock successful operations
        mock_connect.return_value = True
        mock_navigate.return_value = True
        mock_perform.return_value = self.sample_screen_content
        mock_parse.return_value = {
            "found": True,
            "sku": "DGE037700",
            "on_hand": 6.0
        }
        
        self.service.connected = False  # Force connection
        
        result = self.service.lookup_sku(self.test_sku)
        
        self.assertTrue(result["found"])
        self.assertEqual(result["sku"], "DGE037700")
        
        # Verify all steps were called
        mock_connect.assert_called_once()
        mock_navigate.assert_called_once()
        mock_perform.assert_called_once_with(self.test_sku)
        mock_parse.assert_called_once()
        mock_cache_set.assert_called_once()
    
    @patch('inventory_lookup.cache_get')
    @patch.object(InventoryLookupService, 'connect_with_retry')
    def test_lookup_sku_connection_failure(self, mock_connect, mock_cache_get):
        """Test SKU lookup with connection failure"""
        mock_cache_get.return_value = None
        mock_connect.return_value = False
        
        self.service.connected = False
        
        result = self.service.lookup_sku(self.test_sku)
        
        self.assertFalse(result["found"])
        self.assertIn("error", result)
        self.assertIn("Could not connect", result["error"])

class TestScreenParsing(unittest.TestCase):
    """Test screen parsing edge cases"""
    
    def setUp(self):
        self.service = InventoryLookupService()
    
    def test_parse_multiple_warehouses(self):
        """Test parsing screen with multiple warehouses"""
        multi_warehouse_screen = """
                               INVENTORY STATUS                                 
                                                                                
 WH U/M S      On Hand         Alloc     Net Avail         On P/O        On B/O 
 00 EA           6.000          .000         6.000           .000          .000 
 01 EA           3.000          1.000        2.000           .000          .000 
 02 EA           0.000          .000         0.000          10.000         .000 
                                                                                
ITEM: DGE037700                    P2B-SC-100 1SC 123806                                  
        """
        
        result = self.service.parse_inventory_screen(multi_warehouse_screen, "DGE037700")
        
        self.assertTrue(result["found"])
        # Should parse first warehouse line
        self.assertEqual(result["warehouse"], "00")
        self.assertEqual(result["on_hand"], 6.0)
    
    def test_parse_zero_inventory(self):
        """Test parsing screen with zero inventory"""
        zero_inventory_screen = """
                               INVENTORY STATUS                                 
                                                                                
 WH U/M S      On Hand         Alloc     Net Avail         On P/O        On B/O 
 00 EA           0.000          .000         0.000           .000          5.000 
                                                                                
ITEM: TEST123                    Test Product                                  
        """
        
        result = self.service.parse_inventory_screen(zero_inventory_screen, "TEST123")
        
        self.assertTrue(result["found"])
        self.assertEqual(result["on_hand"], 0.0)
        self.assertEqual(result["net_available"], 0.0)
        self.assertEqual(result["on_back_order"], 5.0)
    
    def test_parse_allocated_inventory(self):
        """Test parsing screen with allocated inventory"""
        allocated_screen = """
                               INVENTORY STATUS                                 
                                                                                
 WH U/M S      On Hand         Alloc     Net Avail         On P/O        On B/O 
 00 EA          10.000          3.000        7.000           .000          .000 
                                                                                
ITEM: ALLOC123                    Allocated Product                                  
        """
        
        result = self.service.parse_inventory_screen(allocated_screen, "ALLOC123")
        
        self.assertTrue(result["found"])
        self.assertEqual(result["on_hand"], 10.0)
        self.assertEqual(result["allocated"], 3.0)
        self.assertEqual(result["net_available"], 7.0)

class TestAPIValidation(unittest.TestCase):
    """Test API validation functions"""
    
    def test_sku_validation_valid(self):
        """Test valid SKU formats"""
        valid_skus = ["DGE037700", "ABC123", "XYZ789DEF", "A1B2C3"]
        
        import re
        pattern = r'^[A-Z0-9]{3,15}$'
        
        for sku in valid_skus:
            self.assertTrue(re.match(pattern, sku.upper()), f"SKU {sku} should be valid")
    
    def test_sku_validation_invalid(self):
        """Test invalid SKU formats"""
        invalid_skus = ["AB", "TOOLONGTOBEVALIDSKU123456", "ABC-123", " ABC123 ", ""]
        
        import re
        pattern = r'^[A-Z0-9]{3,15}$'
        
        for sku in invalid_skus:
            self.assertFalse(re.match(pattern, sku.upper()), f"SKU '{sku}' should be invalid")

class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios"""
    
    def setUp(self):
        self.service = InventoryLookupService()
    
    @patch('inventory_lookup.P5250Client')
    def test_connection_timeout(self, mock_p5250_client):
        """Test connection timeout handling"""
        mock_client = Mock()
        mock_p5250_client.return_value = mock_client
        
        # Mock connection timeout
        mock_client.connect.side_effect = Exception("Connection timeout")
        
        result = self.service.connect_with_retry(max_retries=1)
        
        self.assertFalse(result)
        self.assertFalse(self.service.connected)
    
    def test_parse_screen_exception(self):
        """Test screen parsing with exception"""
        # This should not raise an exception but return error result
        result = self.service.parse_inventory_screen(None, "TEST123")
        
        self.assertFalse(result["found"])
        self.assertIn("error", result)

class TestIntegration(unittest.TestCase):
    """Integration tests (require actual connection)"""
    
    @unittest.skipUnless(os.getenv('INTEGRATION_TEST'), "Integration tests disabled")
    def test_real_connection(self):
        """Test real connection to IBM i system"""
        service = InventoryLookupService()
        
        # This test requires actual system access
        result = service.connect_with_retry(max_retries=1)
        
        if result:
            # Test actual SKU lookup
            lookup_result = service.lookup_sku("DGE037700")
            self.assertIn("found", lookup_result)
            
            service.disconnect()

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)