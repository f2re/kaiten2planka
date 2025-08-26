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
        # Get columns (lists) from Kaiten board
        kaiten_columns = self.kaiten_client.get_columns(kaiten_board_id)
        
        # Create a mapping from Kaiten column ID to Planka list ID
        column_to_list_map = {}
        
        # Create lists in Planka for each column
        for i, kaiten_column in enumerate(kaiten_columns):
            try:
                planka_list = self.planka_client.create_list(
                    board_id=planka_board_id,
                    name=kaiten_column['title'],
                    position=i * 65535  # Spread out positions
                )
                if planka_list and 'id' in planka_list:
                    column_to_list_map[kaiten_column['id']] = planka_list['id']
                    logger.info(f"Created list: {kaiten_column['title']}")
                else:
                    logger.error(f"Failed to create list {kaiten_column['title']}")
            except Exception as e:
                logger.error(f"Failed to create list {kaiten_column['title']}: {e}")
        
        # If no columns were created, create a default list to avoid errors
        if not column_to_list_map:
            default_list = self.planka_client.create_list(
                board_id=planka_board_id,
                name="Default List"
            )
            if default_list and 'id' in default_list:
                # We'll put all cards in this default list
                default_list_id = default_list['id']
                logger.info("Created default list")
            else:
                logger.error("Failed to create default list")
                return
        
        # Get cards from Kaiten board
        kaiten_cards = self.kaiten_client.get_cards(kaiten_board_id)
        
        for kaiten_card in kaiten_cards:
            try:
                # Get detailed card information
                card_details = self.kaiten_client.get_card_details(kaiten_card['id'])
                
                # Determine which list this card should go to
                target_list_id = None
                if 'column_id' in kaiten_card and kaiten_card['column_id'] in column_to_list_map:
                    target_list_id = column_to_list_map[kaiten_card['column_id']]
                elif column_to_list_map:
                    # Put in the first available list
                    target_list_id = next(iter(column_to_list_map.values()))
                else:
                    # Put in default list
                    target_list_id = default_list_id
                
                # Create card in Planka
                planka_card = self.planka_client.create_card(
                    list_id=target_list_id,
                    name=kaiten_card['title'],
                    description=card_details.get('description', ''),
                )
                
                if planka_card and 'id' in planka_card:
                    planka_card_id = planka_card['id']
                    logger.info(f"Created card: {kaiten_card['title']} in list {target_list_id}")
                    
                    # Migrate checklists for this card
                    self.migrate_checklists(kaiten_card['id'], planka_card_id)
                    
                    # Migrate attachments for this card
                    self.migrate_attachments(kaiten_card['id'], planka_card_id)
                else:
                    logger.error(f"Failed to create card {kaiten_card['title']}")
            except Exception as e:
                logger.error(f"Failed to create card {kaiten_card['title']}: {e}")

    def migrate_checklists(self, kaiten_card_id: int, planka_card_id: str):
        """Migrate checklists from a Kaiten card to a Planka card."""
        try:
            kaiten_checklists = self.kaiten_client.get_checklists(kaiten_card_id)
            
            for checklist in kaiten_checklists:
                # Create checklist in Planka
                planka_checklist = self.planka_client.create_checklist(
                    card_id=planka_card_id,
                    name=checklist.get('title', 'Checklist')
                )
                
                if planka_checklist and 'id' in planka_checklist:
                    planka_checklist_id = planka_checklist['id']
                    logger.info(f"Created checklist: {checklist.get('title', 'Checklist')}")
                    
                    # Migrate checklist items
                    items = checklist.get('items', [])
                    for item in items:
                        self.planka_client.create_checklist_item(
                            task_id=planka_checklist_id,
                            name=item.get('text', ''),
                            is_completed=item.get('checked', False)
                        )
                else:
                    logger.error(f"Failed to create checklist {checklist.get('title', 'Checklist')}")
        except Exception as e:
            logger.error(f"Error migrating checklists for card {kaiten_card_id}: {e}")

    def migrate_attachments(self, kaiten_card_id: int, planka_card_id: str):
        """Migrate attachments from a Kaiten card to a Planka card."""
        try:
            kaiten_attachments = self.kaiten_client.get_attachments(kaiten_card_id)
            
            for attachment in kaiten_attachments:
                # Download attachment from Kaiten
                attachment_url = attachment.get('url')
                attachment_name = attachment.get('name', 'attachment')
                
                if attachment_url:
                    # Create a temporary file to download the attachment
                    import tempfile
                    import os
                    import requests
                    
                    try:
                        response = requests.get(attachment_url)
                        if response.status_code == 200:
                            # Check content length if available
                            content_length = response.headers.get('content-length')
                            if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB
                                logger.warning(f"Skipping attachment {attachment_name} - file too large ({int(content_length)} bytes)")
                                continue
                            
                            # Create a temporary file
                            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                                tmp_file.write(response.content)
                                tmp_file_path = tmp_file.name
                            
                            # Check file size
                            file_size = os.path.getsize(tmp_file_path)
                            if file_size > 10 * 1024 * 1024:  # 10MB
                                logger.warning(f"Skipping attachment {attachment_name} - file too large ({file_size} bytes)")
                                os.unlink(tmp_file_path)
                                continue
                            
                            # Upload to Planka
                            result = self.planka_client.upload_attachment(
                                card_id=planka_card_id,
                                file_path=tmp_file_path,
                                file_name=attachment_name
                            )
                            
                            # Clean up temporary file
                            os.unlink(tmp_file_path)
                            
                            if result and 'id' in result:
                                logger.info(f"Uploaded attachment: {attachment_name}")
                            else:
                                logger.warning(f"Failed to upload attachment: {attachment_name}")
                        else:
                            logger.error(f"Failed to download attachment {attachment_name}: HTTP {response.status_code}")
                    except Exception as e:
                        logger.error(f"Error downloading/uploading attachment {attachment_name}: {e}")
                else:
                    logger.warning(f"Attachment {attachment_name} has no URL")
        except Exception as e:
            logger.error(f"Error migrating attachments for card {kaiten_card_id}: {e}")

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

        # Process all spaces from Kaiten
        for space in kaiten_spaces:
            space_name = space.get('title', f"Kaiten Space {space['id']}")
            logger.info(f"Processing space: {space_name}")

            # Create a new project in Planka for this space
            try:
                project = self.planka_client.create_project(
                    name=space_name,
                    description=" ",  # Space character instead of empty string to avoid API error
                    type="private"
                )
                
                # Check if project was created successfully
                if not project or 'id' not in project:
                    logger.error(f"Failed to create project in Planka for space {space_name}. Response: {project}")
                    continue  # Skip to the next space
                    
                project_id = project['id']
                logger.info(f"Created new project in Planka: {project.get('name', project_id)}")

                # Get boards for this space
                kaiten_boards = self.kaiten_client.get_boards_for_space(space['id'])
                if kaiten_boards:
                    # Perform migration for this space's data
                    self.migrate_boards(project_id, kaiten_boards)
                else:
                    logger.info(f"No boards found in space: {space_name}")

            except Exception as e:
                logger.error(f"An error occurred while processing space {space_name}: {e}")
                continue