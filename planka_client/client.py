"""
Planka API client for sending data.
"""

import logging
import requests
from typing import Dict, Any, List, Optional
from plankapy import Planka, TokenAuth
from plankapy.models import Card_, Task_

logger = logging.getLogger(__name__)


class PlankaClient:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        # Ensure the API URL ends with /api for Planka
        if not self.api_url.endswith('/api'):
            self.api_url = f"{self.api_url}/api"
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
            # Use direct HTTP request instead of plankapy's create_board method
            # which has compatibility issues
            url = f"{self.api_url}/projects/{project_id}/boards"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "name": name,
                "position": position
            }
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code in [200, 201]:
                result = response.json()
                board_data = result.get('item', {})
                return {
                    'id': board_data.get('id'),
                    'name': board_data.get('name')
                }
            else:
                logger.error(f"Error creating board: HTTP {response.status_code} - {response.text}")
                return {}
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

    def upload_attachment(self, card_id: str, file_path: str, file_name: str | None = None) -> Dict[str, Any]:
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
            max_size = 10 * 1024 * 1024  # 10MB
            
            if file_size > max_size:
                logger.warning(f"File {file_name} is too large ({file_size} bytes). Skipping upload.")
                return {}
            
            # Try with "file" field name instead of "attachment"
            with open(file_path, 'rb') as f:
                files = {
                    'file': (file_name, f, 'application/octet-stream'),
                    'name': (None, file_name, 'text/plain'),
                    'type': (None, 'file', 'text/plain')
                }
                response = requests.post(url, headers=headers, files=files)
                
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
            # Use direct HTTP request to create the label
            url = f"{self.api_url}/boards/{board_id}/labels"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "name": name,
                "color": color
            }
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code in [200, 201]:
                result = response.json()
                label_data = result.get('item', {})
                return {
                    'id': label_data.get('id'),
                    'name': label_data.get('name'),
                    'color': label_data.get('color')
                }
            else:
                logger.error(f"Error creating label: HTTP {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            logger.error(f"Error creating label: {e}")
            return {}

    def add_label_to_card(self, card_id: str, label_id: str) -> Dict[str, Any]:
        """Add a label to a card in Planka using plankapy."""
        try:
            # Find the card using plankapy
            card = self._get_card_by_id(card_id)
            if not card:
                logger.error(f"Card with id {card_id} not found")
                return {}
            
            # Find the label across all boards
            label_obj = None
            for project in self.client.projects:
                try:
                    for board in project.boards:
                        for label in board.labels:
                            if label.id == label_id:
                                label_obj = label
                                break
                        if label_obj:
                            break
                except Exception as e:
                    logger.debug(f"Could not get labels for project {project.id}: {e}")
                if label_obj:
                    break
            
            if not label_obj:
                logger.error(f"Label {label_id} not found")
                return {}
            
            # Add label to card using plankapy method
            card_label = card.add_label(label_obj)
            
            # Refresh card to get updated labels
            card.refresh()
            
            # Verify the label was added
            if card_label and hasattr(card_label, 'id'):
                return {"id": card_label.id}
            else:
                logger.warning("Label added but no card label ID returned")
                return {}
        except Exception as e:
            logger.error(f"Error adding label to card using plankapy: {e}")
            # Fallback to direct API call if plankapy method fails
            try:
                url = f"{self.api_url}/cards/{card_id}/card-labels"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                data = {"labelId": label_id}
                
                response = requests.post(url, headers=headers, json=data)
                if response.status_code in [200, 201]:
                    result = response.json()
                    card_label_data = result.get('item', {})
                    return {
                        'id': card_label_data.get('id'),
                        'labelId': card_label_data.get('labelId')
                    }
                else:
                    logger.error(f"Error adding label to card via API: HTTP {response.status_code} - {response.text}")
                    return {}
            except Exception as api_e:
                logger.error(f"Error adding label to card via API fallback: {api_e}")
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
            logger.debug(f"Found {len(lists)} lists in board {board_id}")
            
            # 2) For each list - get cards and delete them
            for lst in lists:
                list_id = lst.id
                
                # Get all cards in this list
                cards = lst.cards
                logger.debug(f"Found {len(cards)} cards in list {list_id}")
                
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
            
            # Wait a moment for changes to propagate
            import time
            time.sleep(0.5)
            
            # 3) Delete the board itself
            try:
                # Find the board again just before deletion
                board_obj = None
                for project in self.client.projects:
                    try:
                        for board in project.boards:
                            if board.id == board_id:
                                board_obj = board
                                break
                    except Exception as e:
                        logger.debug(f"Could not get boards for project {project.id} before final deletion: {e}")
                    if board_obj:
                        break
                
                if not board_obj:
                    logger.warning(f"Board {board_id} not found (already deleted)")
                    return True
                    
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
            
            # Wait a moment for changes to propagate
            import time
            time.sleep(1.0)
            
            # Now try to delete the project
            try:
                # Find the project again just before deletion
                project_obj = None
                for project in self.client.projects:
                    if project.id == project_id:
                        project_obj = project
                        break
                
                if not project_obj:
                    logger.warning(f"Project {project_id} not found (already deleted)")
                    return True
                    
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
                    # Try one more time after a longer delay
                    import time
                    time.sleep(2.0)
                    
                    try:
                        # Find the project again
                        project_obj = None
                        for project in self.client.projects:
                            if project.id == project_id:
                                project_obj = project
                                break
                        
                        if project_obj:
                            # Check if it still has boards
                            boards = project_obj.boards
                            if len(boards) > 0:
                                logger.debug(f"Project {project_id} still has {len(boards)} boards after delay")
                                # Try to delete them again
                                for board in boards:
                                    board_id = board.id
                                    if not self.delete_board_with_contents(board_id):
                                        logger.error(f"Failed to delete board {board_id} on retry")
                                
                                # Wait a bit more for changes to propagate
                                time.sleep(1.0)
                        
                        # Try one more time to delete the project
                        if project_obj:
                            project_obj.delete()
                            logger.info(f"Successfully deleted project {project_id} on retry")
                            return True
                    except Exception as refresh_e:
                        logger.error(f"Refresh failed for project {project_id}: {refresh_e}")
                    
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
        
        First deletes all boards with their contents, then deletes all projects.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Starting to delete all boards and projects...")
            
            # 1. Get all projects first
            projects = self.get_projects()
            logger.info(f"Found {len(projects)} projects to process")
            
            # 2. For each project, delete all boards with their contents
            for project in projects:
                project_id = project['id']
                try:
                    logger.debug(f"Processing project {project_id}")
                    
                    # Get boards for this specific project
                    project_obj = None
                    for p in self.client.projects:
                        if p.id == project_id:
                            project_obj = p
                            break
                    
                    if not project_obj:
                        logger.warning(f"Project {project_id} not found in client projects")
                        continue
                    
                    # Get all boards in this project
                    boards = project_obj.boards
                    logger.info(f"Found {len(boards)} boards in project {project_id}")
                    
                    # Delete all boards with their contents
                    for board in boards:
                        board_id = board.id
                        if not self.delete_board_with_contents(board_id):
                            logger.error(f"Failed to delete board {board_id}")
                            # Continue with other boards even if one fails
                
                except Exception as e:
                    logger.error(f"Error processing project {project_id}: {e}")
                    # Continue with other projects even if one fails
            
            # 3. Wait a moment for changes to propagate and refresh client data
            import time
            time.sleep(1.0)
            
            # 4. Now delete all projects
            projects = self.get_projects()
            logger.info(f"Found {len(projects)} projects to delete")
            
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

    def create_comment(self, card_id: str, content: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a comment on a card using the Planka API directly.
        
        Note: Comments in Planka are always attributed to the authenticated user.
        We can't specify a user ID for comments in Planka.
        
        Known issue: Comment creation may fail due to API compatibility issues
        between the plankapy library and newer versions of Planka.
        """
        logger.warning("Comment creation is currently not working due to API compatibility issues. "
                      "This is a known limitation when using newer versions of Planka with the plankapy library.")
        return {}

    def _get_card_by_id(self, card_id: str) -> Optional[Card_]:
        """
        Find a card by ID across all projects, boards, and lists using plankapy.
        """
        try:
            for project in self.client.projects:
                for board in project.boards:
                    for lst in board.lists:
                        for card in lst.cards:
                            if card.id == card_id:
                                return card
        except Exception as e:
            logger.error(f"Error finding card {card_id}: {e}")
        return None

    def _get_task_list_by_id(self, task_list_id: str) -> Optional[Task_]:
        """
        Find a task list by ID across all projects, boards, lists, and cards using plankapy.
        """
        try:
            for project in self.client.projects:
                for board in project.boards:
                    for lst in board.lists:
                        for card in lst.cards:
                            for task_list in card.tasks:
                                if task_list.id == task_list_id:
                                    return task_list
        except Exception as e:
            logger.error(f"Error finding task list {task_list_id}: {e}")
        return None

    # ---------- Чек-листы (task-lists) ----------
    def create_task_list(self, card_id: str, name: str, position: Optional[int] = None) -> Dict[str, Any]:
        """
        Создать список задач (task-list) у карточки используя plankapy.
        """
        try:
            # Find the card using plankapy
            card = self._get_card_by_id(card_id)
            if not card:
                logger.error(f"Card with id {card_id} not found")
                # Fallback to direct API call
                url = f"{self.api_url}/cards/{card_id}/task-lists"
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {"name": name}
                if position is not None:
                    payload["position"] = int(position)
                else:
                    # Default position if not provided
                    payload["position"] = 65535
                resp = requests.post(url, headers=headers, json=payload)
                if resp.status_code in (200, 201):
                    item = resp.json().get("item", {})
                    # «Двойная проверка»: наличие id и совпадение имени
                    if item.get("id") and (item.get("name") == name or not name):
                        return {"id": item.get("id"), "name": item.get("name")}
                logger.error(f"Error creating task-list: HTTP {resp.status_code} - {resp.text}")
                return {}
            
            # Create task list using plankapy method
            kwargs = {}
            if position is not None:
                kwargs["position"] = int(position)
            else:
                # Default position if not provided
                kwargs["position"] = 65535
            
            task_list = card.add_task(name=name, **kwargs)
            
            # Refresh card to get updated task lists
            card.refresh()
            
            # Verify the task list was added
            if task_list and hasattr(task_list, 'id'):
                return {"id": task_list.id, "name": getattr(task_list, 'name', name)}
            else:
                logger.warning("Task list created but no ID returned")
                return {"name": name}
        except Exception as e:
            logger.error(f"Error creating task list using plankapy: {e}")
            # Fallback to direct API call
            url = f"{self.api_url}/cards/{card_id}/task-lists"
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {"name": name}
            if position is not None:
                payload["position"] = int(position)
            else:
                # Default position if not provided
                payload["position"] = 65535
            resp = requests.post(url, headers=headers, json=payload)
            if resp.status_code in (200, 201):
                item = resp.json().get("item", {})
                # «Двойная проверка»: наличие id и совпадение имени
                if item.get("id") and (item.get("name") == name or not name):
                    return {"id": item.get("id"), "name": item.get("name")}
            logger.error(f"Error creating task-list: HTTP {resp.status_code} - {resp.text}")
            return {}

    def create_task_in_list(self, task_list_id: str, name: str, is_completed: bool = False,
                            position: Optional[int] = None) -> Dict[str, Any]:
        """
        Создать задачу (пункт чек-листа) внутри task-list используя plankapy.
        """
        try:
            # Find the task list using plankapy
            task_list = self._get_task_list_by_id(task_list_id)
            if not task_list:
                logger.error(f"Task list with id {task_list_id} not found")
                # Fallback to direct API call
                url = f"{self.api_url}/task-lists/{task_list_id}/tasks"
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {"name": name, "isCompleted": bool(is_completed)}
                if position is not None:
                    payload["position"] = int(position)
                resp = requests.post(url, headers=headers, json=payload)
                if resp.status_code in (200, 201):
                    item = resp.json().get("item", {})
                    # «Двойная проверка»: сверка имени и флага isCompleted
                    if item.get("id"):
                        ok_name = (item.get("name") == name) or not name
                        ok_done = bool(item.get("isCompleted", False)) == bool(is_completed)
                        if ok_name and ok_done:
                            return {"id": item.get("id"), "name": item.get("name"), "isCompleted": item.get("isCompleted", False)}
                logger.error(f"Error creating task in list: HTTP {resp.status_code} - {resp.text}")
                return {}
            
            # Create task item using plankapy method
            kwargs = {}
            if position is not None:
                kwargs["position"] = int(position)
            
            task_item = task_list.add_task_item(name=name, is_completed=is_completed, **kwargs)
            
            # Refresh task list to get updated items
            task_list.refresh()
            
            # Verify the task item was added
            if task_item and hasattr(task_item, 'id'):
                return {
                    "id": task_item.id, 
                    "name": getattr(task_item, 'name', name),
                    "isCompleted": getattr(task_item, 'is_completed', is_completed)
                }
            else:
                logger.warning("Task item created but no ID returned")
                return {"name": name, "isCompleted": is_completed}
        except Exception as e:
            logger.error(f"Error creating task item using plankapy: {e}")
            # Fallback to direct API call
            url = f"{self.api_url}/task-lists/{task_list_id}/tasks"
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {"name": name, "isCompleted": bool(is_completed)}
            if position is not None:
                payload["position"] = int(position)
            resp = requests.post(url, headers=headers, json=payload)
            if resp.status_code in (200, 201):
                item = resp.json().get("item", {})
                # «Двойная проверка»: сверка имени и флага isCompleted
                if item.get("id"):
                    ok_name = (item.get("name") == name) or not name
                    ok_done = bool(item.get("isCompleted", False)) == bool(is_completed)
                    if ok_name and ok_done:
                        return {"id": item.get("id"), "name": item.get("name"), "isCompleted": item.get("isCompleted", False)}
            logger.error(f"Error creating task in list: HTTP {resp.status_code} - {resp.text}")
            return {}


    def create_external_link(self, card_id: str, url: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new external link on a card in Planka.
        
        Args:
            card_id (str): The ID of the card to add the external link to
            url (str): The URL of the external link
            name (str, optional): The name/title of the external link
            
        Returns:
            Dict[str, Any]: The created link data or empty dict on failure
        """
        try:
            # First, let's try to create an attachment-like entry for the link
            # Planka typically treats external links as attachments with URL content
            url_endpoint = f"{self.api_url}/cards/{card_id}/attachments"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "url": url,
                "name": name if name else url,
                "type": "link"
            }
            
            response = requests.post(url_endpoint, headers=headers, json=data)
            if response.status_code in [200, 201]:
                result = response.json()
                link_data = result.get('item', {})
                return {
                    'id': link_data.get('id'),
                    'name': link_data.get('name'),
                    'url': link_data.get('url')
                }
            else:
                logger.error(f"Error creating external link: HTTP {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            logger.error(f"Error creating external link: {e}")
            return {}