"""
Tests for Planka client functionality.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from planka_client import PlankaClient
import config


class TestPlankaClient(unittest.TestCase):
    
    @patch('planka_client.client.requests.Session')
    def test_init(self, mock_session):
        """Test PlankaClient initialization."""
        client = PlankaClient(config.PLANKA_API_URL, config.PLANKA_API_KEY)
        self.assertEqual(client.api_url, config.PLANKA_API_URL)
        self.assertEqual(client.api_key, config.PLANKA_API_KEY)
        
    @patch('planka_client.client.requests.get')
    @patch('planka_client.client.Planka')
    def test_get_projects(self, mock_planka, mock_get):
        """Test getting projects from Planka."""
        # Mock the plankapy client
        mock_project1 = Mock()
        mock_project1.id = "1"
        mock_project1.name = "Project 1"
        
        mock_project2 = Mock()
        mock_project2.id = "2"
        mock_project2.name = "Project 2"
        
        mock_planka_instance = Mock()
        mock_planka_instance.projects = [mock_project1, mock_project2]
        mock_planka.return_value = mock_planka_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient(config.PLANKA_API_URL, config.PLANKA_API_KEY)
        projects = client.get_projects()
        
        self.assertEqual(len(projects), 2)
        self.assertEqual(projects[0]["name"], "Project 1")
        self.assertEqual(projects[1]["name"], "Project 2")
        
    @patch('planka_client.client.requests.post')
    def test_create_project(self, mock_post):
        """Test creating a project in Planka."""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "item": {
                "id": "1",
                "name": "New Project"
            }
        }
        mock_post.return_value = mock_response
        
        # Create a new client with mocked dependencies
        client = PlankaClient(config.PLANKA_API_URL, config.PLANKA_API_KEY)
        project = client.create_project("New Project", "Test project")
        
        self.assertEqual(project["name"], "New Project")
        # Note: The current implementation doesn't return description
        
    @patch('planka_client.client.Planka')
    def test_get_boards(self, mock_planka):
        """Test getting boards from Planka."""
        # Mock the plankapy client
        mock_board1 = Mock()
        mock_board1.id = "1"
        mock_board1.name = "Board 1"
        
        mock_board2 = Mock()
        mock_board2.id = "2"
        mock_board2.name = "Board 2"
        
        mock_project = Mock()
        mock_project.boards = [mock_board1, mock_board2]
        
        mock_planka_instance = Mock()
        mock_planka_instance.projects = [mock_project]
        mock_planka.return_value = mock_planka_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient(config.PLANKA_API_URL, config.PLANKA_API_KEY)
        boards = client.get_boards()
        
        self.assertEqual(len(boards), 2)
        self.assertEqual(boards[0]["name"], "Board 1")
        self.assertEqual(boards[1]["name"], "Board 2")
        
    @patch('planka_client.client.requests.post')
    def test_create_board(self, mock_post):
        """Test creating a board in Planka."""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "item": {
                "id": "1",
                "name": "New Board"
            }
        }
        mock_post.return_value = mock_response
        
        # Create a new client with mocked dependencies
        client = PlankaClient(config.PLANKA_API_URL, config.PLANKA_API_KEY)
        board = client.create_board("1", "New Board", "Test board")
        
        self.assertEqual(board["name"], "New Board")
        # Note: The current implementation doesn't return description
        
    @patch('planka_client.client.Planka')
    def test_get_lists(self, mock_planka):
        """Test getting lists from Planka."""
        # Mock the plankapy client
        mock_list1 = Mock()
        mock_list1.id = "1"
        mock_list1.name = "List 1"
        
        mock_list2 = Mock()
        mock_list2.id = "2"
        mock_list2.name = "List 2"
        
        mock_board = Mock()
        mock_board.id = "1"  # Make sure the board has the correct ID
        mock_board.lists = [mock_list1, mock_list2]
        
        mock_project = Mock()
        mock_project.boards = [mock_board]
        
        mock_planka_instance = Mock()
        mock_planka_instance.projects = [mock_project]
        mock_planka.return_value = mock_planka_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient(config.PLANKA_API_URL, config.PLANKA_API_KEY)
        lists = client.get_lists("1")
        
        self.assertEqual(len(lists), 2)
        self.assertEqual(lists[0]["name"], "List 1")
        self.assertEqual(lists[1]["name"], "List 2")
        
    @patch('planka_client.client.requests.post')
    def test_create_list(self, mock_post):
        """Test creating a list in Planka."""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "item": {
                "id": "1",
                "name": "New List"
            }
        }
        mock_post.return_value = mock_response
        
        # Create a new client with mocked dependencies
        client = PlankaClient(config.PLANKA_API_URL, config.PLANKA_API_KEY)
        list_obj = client.create_list("1", "New List", 65535)
        
        self.assertEqual(list_obj["name"], "New List")
        # Note: The current implementation doesn't return position
        
    @patch('planka_client.client.Planka')
    def test_get_cards(self, mock_planka):
        """Test getting cards from Planka."""
        # Mock the plankapy client
        mock_card1 = Mock()
        mock_card1.id = "1"
        mock_card1.name = "Card 1"
        
        mock_card2 = Mock()
        mock_card2.id = "2"
        mock_card2.name = "Card 2"
        
        mock_list = Mock()
        mock_list.id = "1"  # Make sure the list has the correct ID
        mock_list.cards = [mock_card1, mock_card2]
        
        mock_board = Mock()
        mock_board.lists = [mock_list]
        
        mock_project = Mock()
        mock_project.boards = [mock_board]
        
        mock_planka_instance = Mock()
        mock_planka_instance.projects = [mock_project]
        mock_planka.return_value = mock_planka_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient(config.PLANKA_API_URL, config.PLANKA_API_KEY)
        cards = client.get_cards("1")
        
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0]["name"], "Card 1")
        self.assertEqual(cards[1]["name"], "Card 2")
        
    @patch('planka_client.client.requests.post')
    def test_create_card(self, mock_post):
        """Test creating a card in Planka."""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "item": {
                "id": "1",
                "name": "New Card"
            }
        }
        mock_post.return_value = mock_response
        
        # Create a new client with mocked dependencies
        client = PlankaClient(config.PLANKA_API_URL, config.PLANKA_API_KEY)
        card = client.create_card("1", "New Card", "Test card", 65535)
        
        self.assertEqual(card["name"], "New Card")
        # Note: The current implementation doesn't return description or position
        
    @patch('planka_client.client.Planka')
    def test_get_users(self, mock_planka):
        """Test getting users from Planka."""
        # Mock the plankapy client
        mock_user1 = Mock()
        mock_user1.id = "1"
        mock_user1.name = "User 1"
        mock_user1.username = "user1"
        
        mock_user2 = Mock()
        mock_user2.id = "2"
        mock_user2.name = "User 2"
        mock_user2.username = "user2"
        
        mock_planka_instance = Mock()
        mock_planka_instance.users = [mock_user1, mock_user2]
        mock_planka.return_value = mock_planka_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient(config.PLANKA_API_URL, config.PLANKA_API_KEY)
        users = client.get_users()
        
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0]["name"], "User 1")
        self.assertEqual(users[1]["name"], "User 2")
        
    @patch('planka_client.client.Planka')
    def test_create_user(self, mock_planka):
        """Test creating a user in Planka."""
        # Mock the plankapy client
        mock_user = Mock()
        mock_user.id = "1"
        mock_user.name = "New User"
        mock_user.username = "newuser"
        
        mock_planka_instance = Mock()
        mock_planka_instance.create_user.return_value = mock_user
        mock_planka.return_value = mock_planka_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient(config.PLANKA_API_URL, config.PLANKA_API_KEY)
        user = client.create_user("New User", "newuser@example.com", "newuser", "password123")
        
        self.assertEqual(user["name"], "New User")
        self.assertEqual(user["username"], "newuser")
        
    @patch('planka_client.client.Planka')
    def test_get_labels(self, mock_planka):
        """Test getting labels from Planka."""
        # Mock the plankapy client
        mock_label1 = Mock()
        mock_label1.id = "1"
        mock_label1.name = "Label 1"
        mock_label1.color = "#FF0000"
        
        mock_label2 = Mock()
        mock_label2.id = "2"
        mock_label2.name = "Label 2"
        mock_label2.color = "#00FF00"
        
        mock_board = Mock()
        mock_board.id = "1"  # Make sure the board has the correct ID
        mock_board.labels = [mock_label1, mock_label2]
        
        mock_project = Mock()
        mock_project.boards = [mock_board]
        
        mock_planka_instance = Mock()
        mock_planka_instance.projects = [mock_project]
        mock_planka.return_value = mock_planka_instance
        
        # Create a new client with mocked dependencies
        client = PlankaClient(config.PLANKA_API_URL, config.PLANKA_API_KEY)
        labels = client.get_labels("1")
        
        self.assertEqual(len(labels), 2)
        self.assertEqual(labels[0]["name"], "Label 1")
        self.assertEqual(labels[1]["name"], "Label 2")
        
    @patch('planka_client.client.requests.post')
    def test_create_label(self, mock_post):
        """Test creating a label in Planka."""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "item": {
                "id": "1",
                "name": "New Label",
                "color": "#CCCCCC"
            }
        }
        mock_post.return_value = mock_response
        
        # Create a new client with mocked dependencies
        client = PlankaClient(config.PLANKA_API_URL, config.PLANKA_API_KEY)
        label = client.create_label("1", "New Label", "#CCCCCC")
        
        self.assertEqual(label["name"], "New Label")
        self.assertEqual(label["color"], "#CCCCCC")


if __name__ == '__main__':
    unittest.main()