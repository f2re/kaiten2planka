"""
Planka API client for sending data.
"""

import requests
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class PlankaClient:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an API request to Planka."""
        # Ensure the endpoint is treated as a relative path
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        url = urljoin(self.api_url + '/', endpoint)
        logger.debug(f"Making {method} request to {url} with data: {kwargs.get('json')}")
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {url}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response body: {e.response.text}")
            raise

    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects from Planka."""
        response = self._make_request('GET', '/projects')
        return response.get('data', {}).get('projects', [])

    def create_project(self, name: str, description: str = "", type: str = "private") -> Dict[str, Any]:
        """Create a new project in Planka."""
        data = {
            'name': name,
            'description': description if description else " ",
            'type': type
        }
        response = self._make_request('POST', '/projects', json=data)
        return response.get('item', {})

    def get_boards(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all boards for a project from Planka."""
        response = self._make_request('GET', f'/projects/{project_id}/boards')
        return response.get('data', {}).get('boards', [])

    def create_board(self, project_id: str, name: str, description: str = "", type: str = "kanban", position: int = 65535) -> Dict[str, Any]:
        """Create a new board in Planka."""
        data = {
            'name': name,
            'description': description if description else " ",
            'type': type,
            'position': position
        }
        response = self._make_request('POST', f'/projects/{project_id}/boards', json=data)
        return response.get('item', {})

    def get_lists(self, board_id: str) -> List[Dict[str, Any]]:
        """Get all lists for a board from Planka."""
        response = self._make_request('GET', f'/boards/{board_id}/lists')
        return response.get('data', {}).get('lists', [])

    def create_list(self, board_id: str, name: str, position: int = 65535, type: str = "active") -> Dict[str, Any]:
        """Create a new list in Planka."""
        data = {
            'name': name,
            'position': position,
            'type': type
        }
        response = self._make_request('POST', f'/boards/{board_id}/lists', json=data)
        return response.get('item', {})

    def get_cards(self, list_id: str) -> List[Dict[str, Any]]:
        """Get all cards for a list from Planka."""
        response = self._make_request('GET', f'/lists/{list_id}/cards')
        return response.get('data', {}).get('cards', [])

    def create_card(self, list_id: str, name: str, description: str = "", position: int = 65535, type: str = "project") -> Dict[str, Any]:
        """Create a new card in Planka."""
        data = {
            'name': name,
            'description': description if description else " ",
            'position': position,
            'type': type
        }
        response = self._make_request('POST', f'/lists/{list_id}/cards', json=data)
        return response.get('item', {})

    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users from Planka."""
        response = self._make_request('GET', '/users')
        logger.info(f"Raw response from get_users: {response}")
        return response.get('data', {}).get('users', [])

    def create_user(self, name: str, email: str, username: str, password: str, role: str = "boardUser") -> Dict[str, Any]:
        """Create a new user in Planka."""
        data = {
            'name': name,
            'email': email,
            'username': username,
            'password': password,
            'role': role
        }
        response = self._make_request('POST', '/users', json=data)
        return response.get('item', {})

    def get_labels(self, board_id: str) -> List[Dict[str, Any]]:
        """Get all labels for a board from Planka."""
        response = self._make_request('GET', f'/boards/{board_id}/labels')
        return response.get('data', {}).get('labels', [])

    def create_label(self, board_id: str, name: str, color: str = "#CCCCCC") -> Dict[str, Any]:
        """Create a new label in Planka."""
        data = {
            'name': name,
            'color': color
        }
        response = self._make_request('POST', f'/boards/{board_id}/labels', json=data)
        return response.get('data', {}).get('label', {})

    def add_label_to_card(self, card_id: str, label_id: str) -> Dict[str, Any]:
        """Add a label to a card in Planka."""
        data = {
            'labelId': label_id
        }
        response = self._make_request('POST', f'/cards/{card_id}/labels', json=data)
        return response.get('data', {})
        
    def delete_project(self, project_id: str) -> bool:
        """Delete a project from Planka."""
        try:
            self._make_request('DELETE', f'/projects/{project_id}')
            return True
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            return False