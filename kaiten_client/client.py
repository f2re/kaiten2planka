"""
Kaiten API client for fetching data.
Uses the official kaiten package.
"""

import logging
import time
from typing import Dict, Any, List
from kaiten import KaitenClient as KaitenAPIClient

logger = logging.getLogger(__name__)


class KaitenClient:
    def __init__(self, api_url: str, api_key: str):
        # Remove trailing slash and adjust URL if needed
        clean_url = api_url.rstrip('/')
        if '/api/v1' in clean_url:
            clean_url = clean_url.replace('/api/v1', '')
            
        self.api_url = clean_url
        self.api_key = api_key
        self.client = KaitenAPIClient(self.api_url, self.api_key)

    def get_spaces(self) -> List[Dict[str, Any]]:
        """Get all spaces from Kaiten."""
        try:
            # The underlying library does not expose the request, so we do it manually
            # to get more details on errors.
            import requests
            spaces_url = f"{self.api_url}/api/v1/spaces"
            logger.info(f"Fetching spaces from {spaces_url}")
            response = requests.get(spaces_url, headers=self.client.headers)
            if response.status_code != 200:
                logger.error(f"Error fetching spaces. Status: {response.status_code}, Body: {response.text}")
                return []
            
            spaces_data = response.json()
            return spaces_data
        except Exception as e:
            logger.error(f"An exception occurred while getting spaces: {e}")
            return []

    def get_columns(self, board_id: int) -> List[Dict[str, Any]]:
        """Get all columns (lists) for a specific board from Kaiten."""
        try:
            import requests
            columns_url = f"{self.api_url}/api/v1/boards/{board_id}/columns"
            logger.info(f"Fetching columns from URL: {columns_url}")
            response = requests.get(columns_url, headers=self.client.headers)
            logger.info(f"Received response with status code: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Error response from server: {response.text}")
                return []
            return response.json()
        except Exception as e:
            logger.error(f"Error getting columns for board {board_id}: {e}")
            return []

    def get_boards_for_space(self, space_id: int) -> List[Dict[str, Any]]:
        """Get all boards for a specific space from Kaiten."""
        try:
            import requests
            space_boards_url = f"{self.api_url}/api/v1/spaces/{space_id}/boards"
            logger.info(f"Fetching boards from URL: {space_boards_url}")
            response = requests.get(space_boards_url, headers=self.client.headers)
            logger.info(f"Received response with status code: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Error response from server: {response.text}")
                return []
            return response.json()
        except Exception as e:
            logger.error(f"Error getting boards for space {space_id}: {e}")
            return []

    def get_boards(self) -> List[Dict[str, Any]]:
        """Get all boards from all spaces in Kaiten."""
        logger.info("Attempting to fetch all boards from Kaiten.")
        all_boards = []
        spaces = self.get_spaces()
        for space in spaces:
            time.sleep(0.2)  # Add a small delay to avoid rate limiting
            boards = self.get_boards_for_space(space['id'])
            if boards:
                all_boards.extend(boards)
        return all_boards

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
            import requests
            card_url = f"{self.api_url}/api/v1/cards/{card_id}"
            response = requests.get(card_url, headers=self.client.headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting card details for card {card_id}: {response.status_code} - {response.text}")
                return {}
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

    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """Get a specific user by ID from Kaiten."""
        try:
            import requests
            user_url = f"{self.api_url}/api/v1/users/{user_id}"
            response = requests.get(user_url, headers=self.client.headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting user {user_id}: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return {}

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
            # Checklists are included in the card details
            card_details = self.get_card_details(card_id)
            return card_details.get('checklists', [])
        except Exception as e:
            logger.error(f"Error getting checklists for card {card_id}: {e}")
            return []

    def get_checklist_details(self, card_id: int, checklist_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific checklist."""
        try:
            import requests
            checklist_url = f"{self.api_url}/api/v1/cards/{card_id}/checklists/{checklist_id}"
            response = requests.get(checklist_url, headers=self.client.headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting checklist details for checklist {checklist_id} on card {card_id}: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            logger.error(f"Error getting checklist details for checklist {checklist_id} on card {card_id}: {e}")
            return {}

    def get_attachments(self, card_id: int) -> List[Dict[str, Any]]:
        """Get all attachments for a specific card."""
        try:
            # Attachments are not directly available in the kaiten package
            # We need to make a direct API call
            import requests
            # Use the original URL with /api/v1 prefix
            attachments_url = f"{self.api_url}/api/v1/cards/{card_id}/files"
            response = requests.get(attachments_url, headers=self.client.headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting attachments for card {card_id}: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error getting attachments for card {card_id}: {e}")
            return []

    def get_card_comments(self, card_id: int) -> List[Dict[str, Any]]:
        """Get all comments for a specific card."""
        try:
            import requests
            comments_url = f"{self.api_url}/api/v1/cards/{card_id}/comments"
            response = requests.get(comments_url, headers=self.client.headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting comments for card {card_id}: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error getting comments for card {card_id}: {e}")
            return []

    def get_card_external_links(self, card_id: int) -> List[Dict[str, Any]]:
        """Get all external links for a specific card."""
        try:
            # External links are included in the card details
            card_details = self.get_card_details(card_id)
            return card_details.get('external_links', [])
        except Exception as e:
            logger.error(f"Error getting external links for card {card_id}: {e}")
            return []