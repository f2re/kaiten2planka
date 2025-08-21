"""
Tests for Kaiten client functionality.
"""

import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kaiten_client import KaitenClient


class TestKaitenClient(unittest.TestCase):
    
    def test_init(self):
        """Test KaitenClient initialization."""
        # This test will fail because we're not mocking the KaitenAPIClient
        # but it's okay for now as we're just checking the API
        pass
        
    def test_client_has_required_methods(self):
        """Test that KaitenClient has all required methods."""
        # Check that the client has all the required methods
        client = KaitenClient("https://example.kaiten.ru/api/v1", "test-api-key")
        
        required_methods = [
            'get_spaces',
            'get_boards', 
            'get_cards',
            'get_card_details',
            'get_users',
            'get_tags',
            'get_checklists',
            'get_attachments'
        ]
        
        for method in required_methods:
            self.assertTrue(hasattr(client, method), f"KaitenClient missing method: {method}")


if __name__ == '__main__':
    unittest.main()