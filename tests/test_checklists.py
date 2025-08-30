"""
Tests for checklist migration functionality.
"""

import unittest
import sys
import os
from unittest.mock import patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migrator import KaitenToPlankaMigrator
from kaiten_client import KaitenClient
from planka_client import PlankaClient


class TestChecklistMigration(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock clients
        self.kaiten_client = KaitenClient("https://test.kaiten.ru", "test-key")
        self.planka_client = PlankaClient("https://test.planka.ru", "test-key")
        
        # Create migrator with mock clients
        self.migrator = KaitenToPlankaMigrator(self.kaiten_client, self.planka_client)
    
    @patch('kaiten_client.client.KaitenClient.get_checklists')
    @patch('kaiten_client.client.KaitenClient.get_checklist_details')
    @patch('planka_client.client.PlankaClient.create_checklist')
    @patch('planka_client.client.PlankaClient.create_checklist_item')
    def test_migrate_checklists_with_details(self, mock_create_item, mock_create_checklist, 
                                           mock_get_details, mock_get_checklists):
        """Test migrating checklists with detailed information."""
        # Mock Kaiten checklists response
        mock_get_checklists.return_value = [
            {
                "id": 4526413,
                "name": "Чек-лист",
                "checked_items": 12,
                "total_items": 12
            }
        ]
        
        # Mock Kaiten checklist details response
        mock_get_details.return_value = {
            "items": [
                {
                    "text": "Item 1",
                    "checked": True
                },
                {
                    "text": "Item 2",
                    "checked": False
                }
            ]
        }
        
        # Mock Planka checklist creation response
        mock_create_checklist.return_value = {
            "id": "task-1",
            "name": "Чек-лист"
        }
        
        # Mock Planka checklist item creation response
        mock_create_item.return_value = {
            "id": "item-1",
            "name": "Item 1",
            "isCompleted": True
        }
        
        # Run the migration
        self.migrator.migrate_checklists(23136662, "card-1")
        
        # Verify calls were made
        mock_get_checklists.assert_called_once_with(23136662)
        mock_get_details.assert_called_once_with(23136662, 4526413)
        mock_create_checklist.assert_called_once_with(card_id="card-1", name="Чек-лист")
        self.assertEqual(mock_create_item.call_count, 2)


if __name__ == '__main__':
    unittest.main()