"""Planka API client implementation."""

from typing import Dict, Any, List, Optional
import requests
import logging

logger = logging.getLogger(__name__)


class PlankaClient:
    """Planka API client with high-level operations."""
    
    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url.rstrip('/')
    
    def create_board(self, board_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new board in Planka."""
        response = self.session.post(
            f"{self.base_url}/boards",
            json=board_data
        )
        response.raise_for_status()
        return response.json()
    
    def create_list(self, board_id: str, list_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new list in a board."""
        list_data['board_id'] = board_id
        response = self.session.post(
            f"{self.base_url}/lists",
            json=list_data
        )
        response.raise_for_status()
        return response.json()
    
    def create_card(self, list_id: str, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new card in a list."""
        card_data['list_id'] = list_id
        response = self.session.post(
            f"{self.base_url}/cards",
            json=card_data
        )
        response.raise_for_status()
        return response.json()
    
    def upload_attachment(
        self, 
        card_id: str, 
        file_path: str, 
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload attachment to a card."""
        with open(file_path, 'rb') as f:
            files = {
                'file': (filename or file_path, f, 'application/octet-stream')
            }
            response = self.session.post(
                f"{self.base_url}/cards/{card_id}/attachments",
                files=files
            )
        response.raise_for_status()
        return response.json()
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        response = self.session.post(
            f"{self.base_url}/users",
            json=user_data
        )
        response.raise_for_status()
        return response.json()
    
    def get_boards(self) -> List[Dict[str, Any]]:
        """Get all boards."""
        response = self.session.get(f"{self.base_url}/boards")
        response.raise_for_status()
        return response.json()
