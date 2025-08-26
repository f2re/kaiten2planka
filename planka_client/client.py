"""
Planka API client for sending data.
"""

import logging
import requests
from typing import Dict, Any, List
from urllib.parse import urljoin
from plankapy import Planka, TokenAuth

# Import and apply patches to plankapy
from .patcher import patch_plankapy

logger = logging.getLogger(__name__)


class PlankaClient:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        # Initialize the plankapy client
        self.client = Planka(self.api_url, TokenAuth(self.api_key))

    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects from Planka."""
        try:
            projects = self.client.projects
            # Convert plankapy Project objects to dictionaries
            return [{'id': p.id, 'name': p.name} for p in projects]
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return []

    def create_project(self, name: str, description: str = "", type: str = "private") -> Dict[str, Any]:
        """Create a new project in Planka."""
        try:
            # Use direct HTTP request instead of plankapy's create_project method
            # which has compatibility issues
            url = f"{self.api_url}/projects"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "name": name,
                "type": type
            }
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code in [200, 201]:
                result = response.json()
                project_data = result.get('item', {})
                return {
                    'id': project_data.get('id'),
                    'name': project_data.get('name')
                }
            else:
                logger.error(f"Error creating project: HTTP {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return {}

    def get_boards(self) -> List[Dict[str, Any]]:
        """Get all boards from Planka."""
        try:
            # Get all projects first
            projects = self.client.projects
            all_boards = []
            
            # For each project, get its boards
            for project in projects:
                try:
                    boards = project.boards
                    for board in boards:
                        all_boards.append({
                            'id': board.id,
                            'name': board.name,
                            'projectId': project.id
                        })
                except Exception as e:
                    logger.debug(f"Could not get boards for project {project.id}: {e}")
                    # Continue with other projects even if one fails
            
            logger.info(f"Total boards found across all projects: {len(all_boards)}")
            return all_boards
        except Exception as e:
            logger.error(f"Error getting all boards: {e}")
            return []

    def create_board(self, project_id: str, name: str, description: str = "", type: str = "kanban", position: int = 65535) -> Dict[str, Any]:
        """Create a new board in Planka."""
        try:
            # Find the project
            project = None
            for p in self.client.projects:
                if p.id == project_id:
                    project = p
                    break
            
            if not project:
                logger.error(f"Project {project_id} not found")
                return {}
            
            # Create the board
            board = project.create_board(name=name)
            return {'id': board.id, 'name': board.name}
        except Exception as e:
            logger.error(f"Error creating board: {e}")
            return {}

    def get_lists(self, board_id: str) -> List[Dict[str, Any]]:
        """Get all lists for a board from Planka."""
        try:
            # Find the board across all projects
            board_obj = None
            for project in self.client.projects:
                try:
                    for board in project.boards:
                        if board.id == board_id:
                            board_obj = board
                            break
                except Exception as e:
                    logger.debug(f"Could not get boards for project {project.id}: {e}")
                if board_obj:
                    break
            
            if not board_obj:
                logger.error(f"Board {board_id} not found")
                return []
            
            # Get lists for the board
            lists = board_obj.lists
            return [{'id': lst.id, 'name': lst.name} for lst in lists]
        except Exception as e:
            logger.error(f"Error getting lists for board {board_id}: {e}")
            return []

    def create_list(self, board_id: str, name: str, position: int = 65535, type: str = "active") -> Dict[str, Any]:
        """Create a new list in Planka."""
        try:
            # Use direct HTTP request instead of plankapy's create_list method
            # which has compatibility issues
            url = f"{self.api_url}/boards/{board_id}/lists"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "name": name,
                "position": position,
                "type": type
            }
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code in [200, 201]:
                result = response.json()
                list_data = result.get('item', {})
                return {
                    'id': list_data.get('id'),
                    'name': list_data.get('name')
                }
            else:
                logger.error(f"Error creating list: HTTP {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            logger.error(f"Error creating list: {e}")
            return {}

    def get_cards(self, list_id: str) -> List[Dict[str, Any]]:
        """Get all cards for a list from Planka."""
        try:
            # Find the list across all boards and projects
            list_obj = None
            for project in self.client.projects:
                try:
                    for board in project.boards:
                        for lst in board.lists:
                            if lst.id == list_id:
                                list_obj = lst
                                break
                        if list_obj:
                            break
                except Exception as e:
                    logger.debug(f"Could not get boards/lists for project {project.id}: {e}")
                if list_obj:
                    break
            
            if not list_obj:
                logger.error(f"List {list_id} not found")
                return []
            
            # Get cards for the list
            cards = list_obj.cards
            return [{'id': card.id, 'name': card.name} for card in cards]
        except Exception as e:
            logger.error(f"Error getting cards for list {list_id}: {e}")
            return []

    def create_card(self, list_id: str, name: str, description: str = "", position: int = 65535, type: str = "project") -> Dict[str, Any]:
        """Create a new card in Planka."""
        try:
            # Use direct HTTP request instead of plankapy's create_card method
            # which has compatibility issues
            url = f"{self.api_url}/lists/{list_id}/cards"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "name": name,
                "description": description if description else " ",  # Use space instead of empty string
                "position": position,
                "type": type
            }
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code in [200, 201]:
                result = response.json()
                card_data = result.get('item', {})
                return {
                    'id': card_data.get('id'),
                    'name': card_data.get('name')
                }
            else:
                logger.error(f"Error creating card: HTTP {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            logger.error(f"Error creating card: {e}")
            return {}

    def create_checklist(self, card_id: str, name: str) -> Dict[str, Any]:
        """Create a new checklist (task) in Planka."""
        try:
            url = f"{self.api_url}/cards/{card_id}/tasks"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "name": name
            }
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code in [200, 201]:
                result = response.json()
                checklist_data = result.get('item', {})
                return {
                    'id': checklist_data.get('id'),
                    'name': checklist_data.get('name')
                }
            else:
                logger.error(f"Error creating checklist: HTTP {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            logger.error(f"Error creating checklist: {e}")
            return {}

    def create_checklist_item(self, task_id: str, name: str, is_completed: bool = False) -> Dict[str, Any]:
        """Create a new item in a checklist (task-item) in Planka."""
        try:
            url = f"{self.api_url}/tasks/{task_id}/task-items"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "name": name,
                "isCompleted": is_completed
            }
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code in [200, 201]:
                result = response.json()
                item_data = result.get('item', {})
                return {
                    'id': item_data.get('id'),
                    'name': item_data.get('name'),
                    'isCompleted': item_data.get('isCompleted', False)
                }
            else:
                logger.error(f"Error creating checklist item: HTTP {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            logger.error(f"Error creating checklist item: {e}")
            return {}

    def upload_attachment(self, card_id: str, file_path: str, file_name: str = None) -> Dict[str, Any]:
        """Upload an attachment to a card in Planka."""
        try:
            url = f"{self.api_url}/cards/{card_id}/attachments"
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # If file_name is not provided, use the basename of file_path
            if not file_name:
                import os
                file_name = os.path.basename(file_path)
            
            # Check file size (Planka has limits)
            import os
            file_size = os.path.getsize(file_path)
            max_size = 10 * 1024 * 1024  # 10MB limit
            
            if file_size > max_size:
                logger.warning(f"File {file_name} is too large ({file_size} bytes). Skipping upload.")
                return {}
            
            with open(file_path, 'rb') as f:
                # Correct way to send file with form data
                files = {'attachment': (file_name, f, 'application/octet-stream')}
                # Send form fields as data
                data = {
                    'name': file_name
                }
                response = requests.post(url, headers=headers, files=files, data=data)
                
            if response.status_code in [200, 201]:
                result = response.json()
                attachment_data = result.get('item', {})
                return {
                    'id': attachment_data.get('id'),
                    'name': attachment_data.get('name')
                }
            else:
                logger.error(f"Error uploading attachment: HTTP {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            logger.error(f"Error uploading attachment: {e}")
            return {}

    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users from Planka."""
        try:
            users = self.client.users
            return [{'id': u.id, 'name': u.name, 'username': u.username} for u in users]
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []

    def create_user(self, name: str, email: str, username: str, password: str, role: str = "boardUser") -> Dict[str, Any]:
        """Create a new user in Planka."""
        try:
            user = self.client.create_user(username=username, email=email, password=password, name=name)
            return {'id': user.id, 'name': user.name, 'username': user.username}
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return {}

    def get_labels(self, board_id: str) -> List[Dict[str, Any]]:
        """Get all labels for a board from Planka."""
        try:
            # Find the board across all projects
            board_obj = None
            for project in self.client.projects:
                try:
                    for board in project.boards:
                        if board.id == board_id:
                            board_obj = board
                            break
                except Exception as e:
                    logger.debug(f"Could not get boards for project {project.id}: {e}")
                if board_obj:
                    break
            
            if not board_obj:
                logger.error(f"Board {board_id} not found")
                return []
            
            # Get labels for the board
            labels = board_obj.labels
            return [{'id': label.id, 'name': label.name, 'color': label.color} for label in labels]
        except Exception as e:
            logger.error(f"Error getting labels for board {board_id}: {e}")
            return []

    def create_label(self, board_id: str, name: str, color: str = "#CCCCCC") -> Dict[str, Any]:
        """Create a new label in Planka."""
        try:
            # Find the board across all projects
            board_obj = None
            for project in self.client.projects:
                try:
                    for board in project.boards:
                        if board.id == board_id:
                            board_obj = board
                            break
                except Exception as e:
                    logger.debug(f"Could not get boards for project {project.id}: {e}")
                if board_obj:
                    break
            
            if not board_obj:
                logger.error(f"Board {board_id} not found")
                return {}
            
            # Create the label
            # Note: plankapy doesn't seem to have a direct method for creating labels
            # We'll need to use the raw API call
            logger.warning("Label creation not implemented in plankapy wrapper")
            return {}
        except Exception as e:
            logger.error(f"Error creating label: {e}")
            return {}

    def add_label_to_card(self, card_id: str, label_id: str) -> Dict[str, Any]:
        """Add a label to a card in Planka."""
        try:
            # Find the card across all lists, boards, and projects
            card_obj = None
            for project in self.client.projects:
                try:
                    for board in project.boards:
                        for lst in board.lists:
                            for card in lst.cards:
                                if card.id == card_id:
                                    card_obj = card
                                    break
                            if card_obj:
                                break
                        if card_obj:
                            break
                except Exception as e:
                    logger.debug(f"Could not get cards for project {project.id}: {e}")
                if card_obj:
                    break
            
            if not card_obj:
                logger.error(f"Card {card_id} not found")
                return {}
            
            # Add label to card
            # Note: plankapy doesn't seem to have a direct method for adding labels to cards
            # We'll need to use the raw API call
            logger.warning("Adding label to card not implemented in plankapy wrapper")
            return {}
        except Exception as e:
            logger.error(f"Error adding label to card: {e}")
            return {}

    def delete_board(self, board_id: str) -> bool:
        """Delete a board from Planka."""
        try:
            logger.debug(f"Attempting to delete board {board_id}")
            
            # Find the board across all projects
            board_obj = None
            for project in self.client.projects:
                try:
                    for board in project.boards:
                        if board.id == board_id:
                            board_obj = board
                            break
                except Exception as e:
                    logger.debug(f"Could not get boards for project {project.id}: {e}")
                if board_obj:
                    break
            
            if not board_obj:
                logger.warning(f"Board {board_id} not found (already deleted)")
                return True
            
            # Delete the board
            board_obj.delete()
            logger.debug(f"Successfully deleted board {board_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting board {board_id}: {e}")
            return False

    def delete_board_with_contents(self, board_id: str) -> bool:
        """
        Delete a board and all its contents (lists and cards).
        
        Args:
            board_id (str): The ID of the board to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.debug(f"Attempting to delete board {board_id} with all contents")
            
            # Find the board across all projects
            board_obj = None
            for project in self.client.projects:
                try:
                    for board in project.boards:
                        if board.id == board_id:
                            board_obj = board
                            break
                except Exception as e:
                    logger.debug(f"Could not get boards for project {project.id}: {e}")
                if board_obj:
                    break
            
            if not board_obj:
                logger.warning(f"Board {board_id} not found (already deleted)")
                return True
            
            # 1) Get all lists for this board
            lists = board_obj.lists
            
            # 2) For each list - get cards and delete them
            for lst in lists:
                list_id = lst.id
                
                # Get all cards in this list
                cards = lst.cards
                
                # Delete each card
                for card in cards:
                    card_id = card.id
                    try:
                        card.delete()
                        logger.debug(f"Deleted card {card_id}")
                    except requests.exceptions.HTTPError as e:
                        if e.response.status_code == 404:
                            logger.warning(f"Card {card_id} not found (already deleted)")
                        else:
                            logger.error(f"Error deleting card {card_id}: {e}")
                            logger.error(f"Response body: {e.response.text if e.response else 'No response'}")
                            # Continue with other cards even if one fails
                    except Exception as e:
                        logger.error(f"Error deleting card {card_id}: {e}")
                        # Continue with other cards even if one fails
                
                # Delete the list itself
                try:
                    lst.delete()
                    logger.debug(f"Deleted list {list_id}")
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        logger.warning(f"List {list_id} not found (already deleted)")
                    elif e.response.status_code == 403:
                        logger.warning(f"Forbidden to delete list {list_id}. May already be deleted or insufficient permissions. Continuing...")
                    else:
                        logger.error(f"Error deleting list {list_id}: {e}")
                        logger.error(f"Response body: {e.response.text if e.response else 'No response'}")
                        # Continue with other lists even if one fails
                except Exception as e:
                    logger.error(f"Error deleting list {list_id}: {e}")
                    # Continue with other lists even if one fails
            
            # 3) Delete the board itself
            try:
                board_obj.delete()
                logger.debug(f"Successfully deleted board {board_id} with all contents")
                return True
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    logger.warning(f"Board {board_id} not found (already deleted)")
                    return True
                else:
                    logger.error(f"Error deleting board {board_id}: {e}")
                    logger.error(f"Response body: {e.response.text if e.response else 'No response'}")
                    return False
            except Exception as e:
                logger.error(f"Error deleting board {board_id}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting board {board_id} with contents: {e}")
            return False

    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project from Planka.
        
        Args:
            project_id (str): The ID of the project to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.debug(f"Attempting to delete project {project_id}")
            
            # Find the project
            project_obj = None
            for project in self.client.projects:
                if project.id == project_id:
                    project_obj = project
                    break
            
            if not project_obj:
                logger.warning(f"Project {project_id} not found (already deleted)")
                return True
            
            # First delete all boards in this project
            try:
                boards = project_obj.boards
                logger.debug(f"Found {len(boards)} boards to delete in project {project_id}")
                
                # Delete each board with its contents
                for board in boards:
                    board_id = board.id
                    if not self.delete_board_with_contents(board_id):
                        logger.error(f"Failed to delete board {board_id} in project {project_id}")
                        # Continue with other boards but return False at the end
            
            except Exception as e:
                logger.warning(f"Error getting/deleting boards for project {project_id}: {e}")
                # Continue anyway
            
            # Now try to delete the project
            try:
                project_obj.delete()
                logger.info(f"Successfully deleted project {project_id}")
                return True
            except requests.exceptions.HTTPError as http_err:
                if http_err.response.status_code == 404:
                    # Project not found, consider it deleted
                    logger.warning(f"Project {project_id} not found (already deleted)")
                    return True
                elif http_err.response.status_code == 422:
                    # Handle "Must not have boards" error
                    error_msg = http_err.response.text if http_err.response else "No response"
                    logger.error(f"Cannot delete project {project_id}: {error_msg}")
                    # Try one more time after a short delay
                    import time
                    time.sleep(1.0)
                    try:
                        project_obj.delete()
                        logger.info(f"Successfully deleted project {project_id} on retry")
                        return True
                    except Exception as retry_e:
                        logger.error(f"Retry failed for project {project_id}: {retry_e}")
                        return False
                else:
                    logger.error(f"HTTP error deleting project {project_id}: {http_err}")
                    logger.error(f"Response body: {http_err.response.text if http_err.response else 'No response'}")
                    return False
            except Exception as e:
                logger.error(f"Error deleting project {project_id}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            return False

    def delete_all_boards_and_projects(self) -> bool:
        """
        Delete all boards and projects from Planka.
        
        First deletes all boards, then deletes all projects.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Starting to delete all boards and projects...")
            
            # 1. Get all boards
            boards = self.get_boards()
            logger.info(f"Found {len(boards)} boards to delete")
            
            # 2. Delete all boards
            for board in boards:
                board_id = board['id']
                if not self.delete_board_with_contents(board_id):
                    logger.error(f"Failed to delete board {board_id}")
                    # Continue with other boards even if one fails
            
            # 3. Get all projects
            projects = self.get_projects()
            logger.info(f"Found {len(projects)} projects to delete")
            
            # 4. Delete all projects
            for project in projects:
                project_id = project['id']
                if not self.delete_project(project_id):
                    logger.error(f"Failed to delete project {project_id}")
                    # Continue with other projects even if one fails
                    
            logger.info("Finished deleting all boards and projects")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting all boards and projects: {e}")
            return False