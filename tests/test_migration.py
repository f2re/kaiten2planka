"""
Integration tests for the complete migration process.
"""

import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migrator import KaitenToPlankaMigrator
from kaiten_client import KaitenClient
from planka_client import PlankaClient


class TestMigrationIntegration(unittest.TestCase):
    
    def test_migrator_has_required_methods(self):
        """Test that KaitenToPlankaMigrator has all required methods."""
        # Create mock clients
        kaiten_client = KaitenClient("https://example.kaiten.ru/api/v1", "test-api-key")
        planka_client = PlankaClient("https://example.planka.com/api", "test-api-key")
        
        # Create migrator with mock clients
        migrator = KaitenToPlankaMigrator(kaiten_client, planka_client)
        
        required_methods = [
            'migrate_users',
            'migrate_boards', 
            'migrate_lists_and_cards',
            'migrate_tags',
            'migrate_all'
        ]
        
        for method in required_methods:
            self.assertTrue(hasattr(migrator, method), f"KaitenToPlankaMigrator missing method: {method}")


if __name__ == '__main__':
    unittest.main()