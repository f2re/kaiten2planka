"""
Comprehensive migration module for transferring data from Kaiten to Planka.
"""

import logging
import re
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
        if not kaiten_users:
            logger.warning("No users found in Kaiten to migrate.")
            return

        # Get existing planka users to prevent duplicates
        try:
            planka_users = self.planka_client.get_users()
            planka_emails = {user['email'] for user in planka_users if 'email' in user}
        except Exception as e:
            logger.error(f"Error fetching Planka users: {e}")
            planka_emails = set()

        for user in kaiten_users:
            email = user.get('email')
            if not email:
                logger.warning(f"Skipping user {user.get('full_name')} due to missing email.")
                continue

            if email in planka_emails:
                logger.info(f"User with email {email} already exists in Planka. Skipping.")
                continue
            
            # Create new user in Planka
            # Note: We're using a placeholder password here as we don't have access to the original passwords
            try:
                planka_user = self.planka_client.create_user(
                    name=user['full_name'],
                    email=user['email'],
                    username=re.sub(r'[^a-zA-Z0-9]', '', user['email'].split('@')[0]),
                    password="TempPassword123!"  # Placeholder password
                )
                if planka_user and 'id' in planka_user:
                    self.kaiten_to_planka_user_map[user['id']] = planka_user['id']
                    logger.info(f"Created user: {user['full_name']}")
                else:
                    logger.error(f"Failed to create user {user['full_name']}: Invalid response from Planka API")
            except Exception as e:
                logger.error(f"Failed to create user {user['full_name']}: {e}")


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

    def migrate_boards(self, project_id: str, kaiten_boards: List[Dict[str, Any]]):
        """Migrate all boards, lists, and cards for a given space into a project."""
        return self.migrate_space_data(project_id, kaiten_boards)
        
    def migrate_space_data(self, project_id: str, kaiten_boards: List[Dict[str, Any]]):
        """Migrate all boards, lists, and cards for a given space into a project."""
        logger.info(f"Starting board migration for project {project_id}")
        for i, kaiten_board in enumerate(kaiten_boards):
            try:
                planka_board = self.planka_client.create_board(
                    project_id=project_id,
                    name=kaiten_board['title'],
                    description=kaiten_board.get('description') or "",
                    position=i
                )
                self.kaiten_to_planka_board_map[kaiten_board['id']] = planka_board['id']
                logger.info(f"Created board: {kaiten_board['title']}")
                
                # Migrate lists and cards for this board
                self.migrate_lists_and_cards(kaiten_board['id'], planka_board['id'])
            except Exception as e:
                logger.error(f"Failed to create board {kaiten_board.get('title', 'Unknown')}: {e}")
        # 4. Migrate attachments
        # 5. Migrate comments
        # 6. Preserve card positions
        # 7. Handle due dates
        # 8. Handle assignees
        
        logger.info("Complete migration process finished")
        
    def migrate_all(self):
        """Perform complete migration from Kaiten to Planka."""
        # First, migrate all users
        self.migrate_users()

        # Then, iterate through spaces and migrate each one as a separate project
        kaiten_spaces = self.kaiten_client.get_spaces()
        if not kaiten_spaces:
            logger.warning("No spaces found in Kaiten. Nothing to migrate.")
            return

        for space in kaiten_spaces:
            space_name = space.get('name', f"Kaiten Space {space['id']}")
            logger.info(f"Processing space: {space_name}")

            # Create a new project in Planka for this space
            try:
                project = self.planka_client.create_project(
                    name=space_name,
                    description="",  # Empty description as requested
                    type="private"
                )
                project_id = project['id']
                logger.info(f"Created new project in Planka: {project['name']}")

                # Get boards for this space
                kaiten_boards = self.kaiten_client.get_boards_for_space(space['id'])
                if kaiten_boards:
                    # Perform migration for this space's data
                    self.migrate_boards(project_id, kaiten_boards)
                else:
                    logger.info(f"No boards found in space: {space_name}")

            except Exception as e:
                logger.error(f"Failed to migrate space {space_name}: {e}")