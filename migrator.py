"""
Comprehensive migration module for transferring data from Kaiten to Planka.
"""

import logging
from typing import Dict, Any, List
from kaiten_client import KaitenClient
from planka_client import PlankaClient

logger = logging.getLogger(__name__)


class KaitenToPlankaMigrator:
    def __init__(self, kaiten_client: KaitenClient, planka_client: PlankaClient):
        self.kaiten_client = kaiten_client
        self.planka_client = planka_client
        self.kaiten_to_planka_user_map = {}
        self.kaiten_to_planka_board_map = {}
        self.kaiten_to_planka_list_map = {}
        self.kaiten_to_planka_label_map = {}

    def migrate_users(self):
        """Migrate users from Kaiten to Planka."""
        logger.info("Starting user migration")
        
        kaiten_users = self.kaiten_client.get_users()
        planka_users = self.planka_client.get_users()
        
        # Create a mapping of existing Planka users by email
        planka_user_emails = {user['email']: user for user in planka_users}
        
        for kaiten_user in kaiten_users:
            # Skip if user already exists in Planka
            if kaiten_user['email'] in planka_user_emails:
                self.kaiten_to_planka_user_map[kaiten_user['id']] = planka_user_emails[kaiten_user['email']]['id']
                continue
            
            # Create new user in Planka
            # Note: We're using a placeholder password here as we don't have access to the original passwords
            try:
                planka_user = self.planka_client.create_user(
                    name=kaiten_user['name'],
                    email=kaiten_user['email'],
                    username=kaiten_user['email'].split('@')[0],  # Use part of email as username
                    password="TempPassword123!"  # Placeholder password
                )
                self.kaiten_to_planka_user_map[kaiten_user['id']] = planka_user['id']
                logger.info(f"Created user: {kaiten_user['name']}")
            except Exception as e:
                logger.error(f"Failed to create user {kaiten_user['name']}: {e}")

    def migrate_boards(self, project_id: str):
        """Migrate boards from Kaiten to Planka."""
        logger.info("Starting board migration")
        
        kaiten_boards = self.kaiten_client.get_boards()
        
        for kaiten_board in kaiten_boards:
            try:
                planka_board = self.planka_client.create_board(
                    project_id=project_id,
                    name=kaiten_board['name'],
                    description=kaiten_board.get('description', '')
                )
                self.kaiten_to_planka_board_map[kaiten_board['id']] = planka_board['id']
                logger.info(f"Created board: {kaiten_board['name']}")
                
                # Migrate lists and cards for this board
                self.migrate_lists_and_cards(kaiten_board['id'], planka_board['id'])
            except Exception as e:
                logger.error(f"Failed to create board {kaiten_board['name']}: {e}")

    def migrate_lists_and_cards(self, kaiten_board_id: int, planka_board_id: str):
        """Migrate lists and cards from a Kaiten board to a Planka board."""
        # First, create default list since Planka requires at least one list
        default_list = self.planka_client.create_list(
            board_id=planka_board_id,
            name="Default List"
        )
        
        # Get cards from Kaiten board
        kaiten_cards = self.kaiten_client.get_cards(kaiten_board_id)
        
        for kaiten_card in kaiten_cards:
            try:
                # Get detailed card information
                card_details = self.kaiten_client.get_card_details(kaiten_card['id'])
                
                # Create card in Planka (using default list for now)
                planka_card = self.planka_client.create_card(
                    list_id=default_list['id'],
                    name=kaiten_card['title'],
                    description=card_details.get('description', ''),
                )
                
                logger.info(f"Created card: {kaiten_card['title']}")
                
                # TODO: Migrate checklists, attachments, comments, etc.
            except Exception as e:
                logger.error(f"Failed to create card {kaiten_card['title']}: {e}")

    def migrate_tags(self, planka_board_id: str):
        """Migrate tags from Kaiten to labels in Planka."""
        logger.info("Starting tag migration")
        
        kaiten_tags = self.kaiten_client.get_tags()
        
        for kaiten_tag in kaiten_tags:
            try:
                planka_label = self.planka_client.create_label(
                    board_id=planka_board_id,
                    name=kaiten_tag['name'],
                    color=kaiten_tag.get('color', '#CCCCCC')
                )
                self.kaiten_to_planka_label_map[kaiten_tag['id']] = planka_label['id']
                logger.info(f"Created label: {kaiten_tag['name']}")
            except Exception as e:
                logger.error(f"Failed to create label {kaiten_tag['name']}: {e}")

    def migrate_all(self, project_id: str):
        """Run complete migration process."""
        logger.info("Starting complete migration process")
        
        # Migrate users first
        self.migrate_users()
        
        # Migrate boards
        self.migrate_boards(project_id)
        
        # For a more complete implementation, we would also:
        # 1. Migrate tags to labels
        # 2. Associate cards with labels
        # 3. Migrate checklists
        # 4. Migrate attachments
        # 5. Migrate comments
        # 6. Preserve card positions
        # 7. Handle due dates
        # 8. Handle assignees
        
        logger.info("Complete migration process finished")