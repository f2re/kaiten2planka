"""
Kaiten API client for fetching data.
Uses the official kaiten package.
"""

import logging
from typing import Dict, Any, List, Optional
from kaiten import KaitenClient as KaitenAPIClient

logger = logging.getLogger(__name__)


class KaitenClient:
    def __init__(self, api_url: str, api_key: str):
        # Remove trailing slash and adjust URL if needed
        clean_url = api_url.rstrip('/')
        if clean_url.endswith('/api/v1'):
            clean_url = clean_url[:-8]  # Remove '/api/v1'
            
        self.api_url = clean_url
        self.api_key = api_key
        self.client = KaitenAPIClient(self.api_url, self.api_key)

    def get_spaces(self) -> List[Dict[str, Any]]:
        """Get all spaces from Kaiten."""
        try:
            spaces = self.client.list_of().spaces()
            # Convert Space objects to dictionaries
            return [space.__dict__ for space in spaces]
        except Exception as e:
            logger.error(f"Error getting spaces: {e}")
            return []

    def get_boards(self) -> List[Dict[str, Any]]:
        """Get all boards from Kaiten."""
        try:
            # Get spaces first, then boards within each space
            spaces = self.client.list_of().spaces()
            boards = []
            
            for space in spaces:
                # Get boards for each space using direct API call
                # The kaiten package doesn't seem to have a direct method for this
                import requests
                space_boards_url = f"{self.client.base_api_url}/spaces/{space.id}/boards"
                response = requests.get(space_boards_url, headers=self.client.headers)
                if response.status_code == 200:
                    space_boards = response.json()
                    boards.extend(space_boards)
                    
            return boards
        except Exception as e:
            logger.error(f"Error getting boards: {e}")
            return []

    def get_cards(self, board_id: int) -> List[Dict[str, Any]]:
        """Get all cards from a specific board."""
        try:
            # Use the list_of.cards method with board_id filter
            cards = self.client.list_of().cards(board_id=board_id)
            # Convert Card objects to dictionaries
            return [card.__dict__ for card in cards]
        except Exception as e:
            logger.error(f"Error getting cards for board {board_id}: {e}")
            return []

    def get_card_details(self, card_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific card."""
        try:
            card = self.client.get_card(card_id)
            return card.__dict__
        except Exception as e:
            logger.error(f"Error getting card details for card {card_id}: {e}")
            return {}

    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users from Kaiten."""
        try:
            users = self.client.list_of().users()
            # Convert User objects to dictionaries
            return [user.__dict__ for user in users]
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []

    def get_tags(self) -> List[Dict[str, Any]]:
        """Get all tags from Kaiten."""
        try:
            tags = self.client.list_of().tags()
            # Convert Tag objects to dictionaries
            return [tag.__dict__ for tag in tags]
        except Exception as e:
            logger.error(f"Error getting tags: {e}")
            return []

    def get_checklists(self, card_id: int) -> List[Dict[str, Any]]:
        """Get all checklists for a specific card."""
        try:
            # Checklists are not directly available in the kaiten package
            # We need to make a direct API call
            import requests
            checklists_url = f"{self.client.base_api_url}/cards/{card_id}/checklists"
            response = requests.get(checklists_url, headers=self.client.headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting checklists for card {card_id}: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting checklists for card {card_id}: {e}")
            return []

    def get_attachments(self, card_id: int) -> List[Dict[str, Any]]:
        """Get all attachments for a specific card."""
        try:
            # Attachments are not directly available in the kaiten package
            # We need to make a direct API call
            import requests
            attachments_url = f"{self.client.base_api_url}/cards/{card_id}/files"
            response = requests.get(attachments_url, headers=self.client.headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting attachments for card {card_id}: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting attachments for card {card_id}: {e}")
            return []