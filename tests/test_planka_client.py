"""
Tests for Planka client functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from planka_client import PlankaClient


class TestPlankaClient(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.planka_client = PlankaClient("https://example.planka.com/api", "test-api-key")
        
    @patch('planka_client.client.requests.Session')
    def test_init(self, mock_session):
        """Test PlankaClient initialization."""
        client = PlankaClient("https://example.planka.com/api", "test-api-key")
        self.assertEqual(client.api_url, "https://example.planka.com/api")
        self.assertEqual(client.api_key, "test-api-key")
        
    @patch('planka_client.client.requests.Session')
    def test_get_projects(self, mock_session):
        """Test getting projects from Planka."""
        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "projects": [
                    {"id": "1", "name": "Project 1"},
                    {"id": "2", "name": "Project 2"}
                ]
            }
        }
        
        # Mock the session
        mock_session_instance = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient("https://example.planka.com/api", "test-api-key")
        projects = client.get_projects()
        
        self.assertEqual(len(projects), 2)
        self.assertEqual(projects[0]["name"], "Project 1")
        self.assertEqual(projects[1]["name"], "Project 2")
        
    @patch('planka_client.client.requests.Session')
    def test_create_project(self, mock_session):
        """Test creating a project in Planka."""
        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "project": {
                    "id": "1",
                    "name": "New Project",
                    "description": "Test project"
                }
            }
        }
        
        # Mock the session
        mock_session_instance = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient("https://example.planka.com/api", "test-api-key")
        project = client.create_project("New Project", "Test project")
        
        self.assertEqual(project["name"], "New Project")
        self.assertEqual(project["description"], "Test project")
        
    @patch('planka_client.client.requests.Session')
    def test_get_boards(self, mock_session):
        """Test getting boards from Planka."""
        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "boards": [
                    {"id": "1", "name": "Board 1"},
                    {"id": "2", "name": "Board 2"}
                ]
            }
        }
        
        # Mock the session
        mock_session_instance = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient("https://example.planka.com/api", "test-api-key")
        boards = client.get_boards("project-1")
        
        self.assertEqual(len(boards), 2)
        self.assertEqual(boards[0]["name"], "Board 1")
        self.assertEqual(boards[1]["name"], "Board 2")
        
    @patch('planka_client.client.requests.Session')
    def test_create_board(self, mock_session):
        """Test creating a board in Planka."""
        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "board": {
                    "id": "1",
                    "name": "New Board",
                    "description": "Test board"
                }
            }
        }
        
        # Mock the session
        mock_session_instance = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient("https://example.planka.com/api", "test-api-key")
        board = client.create_board("project-1", "New Board", "Test board")
        
        self.assertEqual(board["name"], "New Board")
        self.assertEqual(board["description"], "Test board")
        
    @patch('planka_client.client.requests.Session')
    def test_get_lists(self, mock_session):
        """Test getting lists from Planka."""
        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "lists": [
                    {"id": "1", "name": "List 1"},
                    {"id": "2", "name": "List 2"}
                ]
            }
        }
        
        # Mock the session
        mock_session_instance = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient("https://example.planka.com/api", "test-api-key")
        lists = client.get_lists("board-1")
        
        self.assertEqual(len(lists), 2)
        self.assertEqual(lists[0]["name"], "List 1")
        self.assertEqual(lists[1]["name"], "List 2")
        
    @patch('planka_client.client.requests.Session')
    def test_create_list(self, mock_session):
        """Test creating a list in Planka."""
        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "list": {
                    "id": "1",
                    "name": "New List",
                    "position": 65535
                }
            }
        }
        
        # Mock the session
        mock_session_instance = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient("https://example.planka.com/api", "test-api-key")
        list_obj = client.create_list("board-1", "New List", 65535)
        
        self.assertEqual(list_obj["name"], "New List")
        self.assertEqual(list_obj["position"], 65535)
        
    @patch('planka_client.client.requests.Session')
    def test_get_cards(self, mock_session):
        """Test getting cards from Planka."""
        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "cards": [
                    {"id": "1", "name": "Card 1"},
                    {"id": "2", "name": "Card 2"}
                ]
            }
        }
        
        # Mock the session
        mock_session_instance = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient("https://example.planka.com/api", "test-api-key")
        cards = client.get_cards("list-1")
        
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0]["name"], "Card 1")
        self.assertEqual(cards[1]["name"], "Card 2")
        
    @patch('planka_client.client.requests.Session')
    def test_create_card(self, mock_session):
        """Test creating a card in Planka."""
        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "card": {
                    "id": "1",
                    "name": "New Card",
                    "description": "Test card",
                    "position": 65535
                }
            }
        }
        
        # Mock the session
        mock_session_instance = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient("https://example.planka.com/api", "test-api-key")
        card = client.create_card("list-1", "New Card", "Test card", 65535)
        
        self.assertEqual(card["name"], "New Card")
        self.assertEqual(card["description"], "Test card")
        self.assertEqual(card["position"], 65535)
        
    @patch('planka_client.client.requests.Session')
    def test_get_users(self, mock_session):
        """Test getting users from Planka."""
        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "users": [
                    {"id": "1", "name": "User 1", "email": "user1@example.com"},
                    {"id": "2", "name": "User 2", "email": "user2@example.com"}
                ]
            }
        }
        
        # Mock the session
        mock_session_instance = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient("https://example.planka.com/api", "test-api-key")
        users = client.get_users()
        
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0]["name"], "User 1")
        self.assertEqual(users[1]["name"], "User 2")
        
    @patch('planka_client.client.requests.Session')
    def test_create_user(self, mock_session):
        """Test creating a user in Planka."""
        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "user": {
                    "id": "1",
                    "name": "New User",
                    "email": "newuser@example.com",
                    "username": "newuser"
                }
            }
        }
        
        # Mock the session
        mock_session_instance = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient("https://example.planka.com/api", "test-api-key")
        user = client.create_user("New User", "newuser@example.com", "newuser", "password123")
        
        self.assertEqual(user["name"], "New User")
        self.assertEqual(user["email"], "newuser@example.com")
        self.assertEqual(user["username"], "newuser")
        
    @patch('planka_client.client.requests.Session')
    def test_get_labels(self, mock_session):
        """Test getting labels from Planka."""
        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "labels": [
                    {"id": "1", "name": "Label 1", "color": "#FF0000"},
                    {"id": "2", "name": "Label 2", "color": "#00FF00"}
                ]
            }
        }
        
        # Mock the session
        mock_session_instance = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient("https://example.planka.com/api", "test-api-key")
        labels = client.get_labels("board-1")
        
        self.assertEqual(len(labels), 2)
        self.assertEqual(labels[0]["name"], "Label 1")
        self.assertEqual(labels[1]["name"], "Label 2")
        
    @patch('planka_client.client.requests.Session')
    def test_create_label(self, mock_session):
        """Test creating a label in Planka."""
        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "label": {
                    "id": "1",
                    "name": "New Label",
                    "color": "#CCCCCC"
                }
            }
        }
        
        # Mock the session
        mock_session_instance = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient("https://example.planka.com/api", "test-api-key")
        label = client.create_label("board-1", "New Label", "#CCCCCC")
        
        self.assertEqual(label["name"], "New Label")
        self.assertEqual(label["color"], "#CCCCCC")


if __name__ == '__main__':
    unittest.main()