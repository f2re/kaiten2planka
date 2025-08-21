"""Main migration engine with orchestration logic."""

import concurrent.futures
import hashlib
import json
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass

from ..auth.kaiten import authenticate_kaiten
from ..auth.planka import authenticate_planka
from ..discovery.kaiten_client import (
    list_kaiten_projects, 
    list_kaiten_cards, 
    list_kaiten_attachments
)
from ..mapping.core import map_kaiten_to_planka
from ..storage.idempotency import IdempotencyStore
from ..storage.attachments import download_attachment, upload_attachment_to_planka
from ..planka.client import PlankaClient
from ..utils.rate_limit import RateLimiter
from ..utils.retry import retry_with_backoff
from ..config import Settings

logger = logging.getLogger(__name__)


@dataclass
class MigrationResults:
    """Results of migration operation."""
    migrated: Dict[str, int]
    skipped: Dict[str, int]
    errors: List[Dict[str, Any]]
    attachments_transferred: int


class MigrationEngine:
    """Main migration engine coordinating all operations."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.kaiten_session = None
        self.planka_session = None
        self.planka_client = None
        self.store = IdempotencyStore(settings.database.path)
        self.rate_limiter = RateLimiter(settings.migration.rate_limit_rps)
        
    def _authenticate(self) -> None:
        """Authenticate with both APIs."""
        logger.info("Authenticating with Kaiten and Planka APIs...")
        
        self.kaiten_session = authenticate_kaiten(
            self.settings.kaiten.api_key,
            self.settings.kaiten.api_url
        )
        
        self.planka_session = authenticate_planka(
            self.settings.planka.api_key, 
            self.settings.planka.api_url
        )
        
        self.planka_client = PlankaClient(
            self.planka_session,
            self.settings.planka.api_url
        )
        
        logger.info("Authentication successful for both APIs")
    
    def dry_run(self) -> Dict[str, Any]:
        """
        Perform dry run analysis.
        
        Returns:
            Dictionary with planned migration counts
        """
        logger.info("Starting dry run analysis...")
        self._authenticate()
        
        results = {
            'planned_migrations': {},
            'estimated_attachments': 0,
            'estimated_users': 0
        }
        
        try:
            # Count projects
            projects = list(list_kaiten_projects(
                self.kaiten_session, 
                self.settings.kaiten.api_url
            ))
            results['planned_migrations']['projects'] = len(projects)
            logger.info(f"Found {len(projects)} projects to migrate")
            
            # Count cards and attachments
            total_cards = 0
            total_attachments = 0
            unique_users = set()
            
            for project in projects:
                logger.debug(f"Analyzing project: {project.get('title', 'Unknown')}")
                
                cards = list(list_kaiten_cards(
                    self.kaiten_session,
                    self.settings.kaiten.api_url,
                    project['id']
                ))
                total_cards += len(cards)
                
                for card in cards:
                    # Count attachments
                    attachments = list(list_kaiten_attachments(
                        self.kaiten_session,
                        self.settings.kaiten.api_url,
                        card['id']
                    ))
                    total_attachments += len(attachments)
                    
                    # Count unique users
                    if 'assignees' in card:
                        for assignee in card['assignees']:
                            unique_users.add(assignee.get('id'))
            
            results['planned_migrations']['cards'] = total_cards
            results['estimated_attachments'] = total_attachments
            results['estimated_users'] = len(unique_users)
            
            logger.info(f"Dry run complete: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Dry run failed: {e}")
            raise
    
    def run_migration(self) -> MigrationResults:
        """
        Run full migration.
        
        Returns:
            Migration results
        """
        logger.info("Starting full migration...")
        self._authenticate()
        
        if self.settings.migration.force:
            logger.info("Force flag enabled, clearing existing migration records")
            self.store.clear_migrations()
        
        results = MigrationResults(
            migrated={},
            skipped={},
            errors=[],
            attachments_transferred=0
        )
        
        try:
            # Step 1: Migrate users first
            self._migrate_users(results)
            
            # Step 2: Migrate projects (which become boards)
            project_mapping = self._migrate_projects(results)
            
            # Step 3: Migrate cards with attachments
            self._migrate_cards(results, project_mapping)
            
            logger.info("Migration completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
    
    def _migrate_users(self, results: MigrationResults) -> Dict[str, str]:
        """
        Migrate users and return mapping of Kaiten ID to Planka ID.
        
        Returns:
            Dictionary mapping Kaiten user IDs to Planka user IDs
        """
        logger.info("Migrating users...")
        
        results.migrated['users'] = 0
        results.skipped['users'] = 0
        user_mapping = {}
        
        # For this implementation, we'll assume users are managed separately
        # In a real implementation, you'd extract users from projects/cards
        # and create them in Planka if they don't exist
        
        logger.info("User migration completed (assuming external user management)")
        return user_mapping
    
    def _migrate_projects(self, results: MigrationResults) -> Dict[str, str]:
        """
        Migrate all projects and return mapping.
        
        Returns:
            Dictionary mapping Kaiten project IDs to Planka board IDs
        """
        logger.info("Migrating projects...")
        
        projects = list(list_kaiten_projects(
            self.kaiten_session,
            self.settings.kaiten.api_url
        ))
        
        results.migrated['projects'] = 0
        results.skipped['projects'] = 0
        project_mapping = {}
        
        for project in projects:
            try:
                with self.rate_limiter:
                    project_id, planka_board_id = self._migrate_single_project(project)
                    if planka_board_id:
                        project_mapping[project_id] = planka_board_id
                        results.migrated['projects'] += 1
                    else:
                        results.skipped['projects'] += 1
                        
            except Exception as e:
                self._handle_migration_error(results, 'project', project, e)
        
        logger.info(f"Project migration completed: {results.migrated['projects']} migrated, {results.skipped['projects']} skipped")
        return project_mapping
    
    def _migrate_single_project(self, project: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        """Migrate a single project."""
        kaiten_id = str(project['id'])
        checksum = self._calculate_checksum(project)
        
        # Check if already migrated
        planka_id = self.store.is_migrated(kaiten_id, 'project', checksum)
        if planka_id:
            logger.debug(f"Project {kaiten_id} already migrated, skipping")
            return kaiten_id, None
        
        # Map and create in Planka
        planka_data = map_kaiten_to_planka('project', project)
        
        if not self.settings.migration.dry_run:
            response = self.planka_client.create_board(planka_data)
            planka_id = str(response['id'])
            
            # Create default list in the board
            default_list_data = {
                'name': 'To Do',
                'position': 0
            }
            list_response = self.planka_client.create_list(planka_id, default_list_data)
            
            self.store.record_migration(kaiten_id, planka_id, 'project', checksum)
            logger.info(f"Migrated project: {project.get('title', 'Unknown')} -> {planka_id}")
        else:
            planka_id = f"dry-run-board-{kaiten_id}"
            logger.info(f"[DRY RUN] Would migrate project: {project.get('title', 'Unknown')}")
        
        return kaiten_id, planka_id
    
    def _migrate_cards(self, results: MigrationResults, project_mapping: Dict[str, str]) -> None:
        """Migrate all cards with concurrent processing."""
        logger.info("Migrating cards...")
        
        results.migrated['cards'] = 0
        results.skipped['cards'] = 0
        
        # Collect all cards from all projects
        all_cards = []
        for project_id, planka_board_id in project_mapping.items():
            cards = list(list_kaiten_cards(
                self.kaiten_session,
                self.settings.kaiten.api_url,
                int(project_id)
            ))
            
            for card in cards:
                card['_planka_board_id'] = planka_board_id
                all_cards.append(card)
        
        logger.info(f"Found {len(all_cards)} cards to migrate")
        
        # Process cards with thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.settings.migration.workers) as executor:
            # Submit all card migration tasks
            future_to_card = {
                executor.submit(self._migrate_single_card, card): card
                for card in all_cards
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_card):
                card = future_to_card[future]
                try:
                    migrated = future.result()
                    if migrated:
                        results.migrated['cards'] += 1
                    else:
                        results.skipped['cards'] += 1
                        
                except Exception as e:
                    self._handle_migration_error(results, 'card', card, e)
        
        logger.info(f"Card migration completed: {results.migrated['cards']} migrated, {results.skipped['cards']} skipped")
    
    def _migrate_single_card(self, card: Dict[str, Any]) -> bool:
        """Migrate a single card with attachments."""
        with self.rate_limiter:
            kaiten_id = str(card['id'])
            checksum = self._calculate_checksum(card)
            
            # Check if already migrated
            planka_id = self.store.is_migrated(kaiten_id, 'card', checksum)
            if planka_id:
                logger.debug(f"Card {kaiten_id} already migrated, skipping")
                return False
            
            # Get board and create default list if needed
            planka_board_id = card['_planka_board_id']
            
            # Map and create in Planka
            planka_data = map_kaiten_to_planka('card', card)
            
            if not self.settings.migration.dry_run:
                # Get or create a list in the board
                boards = self.planka_client.get_boards()
                target_board = next((b for b in boards if b['id'] == planka_board_id), None)
                
                if not target_board:
                    raise ValueError(f"Board {planka_board_id} not found")
                
                # Assume first list exists or create one
                lists = target_board.get('lists', [])
                if not lists:
                    list_data = {'name': 'Default', 'position': 0}
                    list_response = self.planka_client.create_list(planka_board_id, list_data)
                    list_id = list_response['id']
                else:
                    list_id = lists[0]['id']
                
                # Create card
                response = self.planka_client.create_card(list_id, planka_data)
                planka_card_id = str(response['id'])
                
                # Migrate attachments
                self._migrate_card_attachments(card, planka_card_id)
                
                self.store.record_migration(kaiten_id, planka_card_id, 'card', checksum)
                logger.info(f"Migrated card: {card.get('title', 'Unknown')} -> {planka_card_id}")
            else:
                logger.info(f"[DRY RUN] Would migrate card: {card.get('title', 'Unknown')}")
            
            return True
    
    def _migrate_card_attachments(self, card: Dict[str, Any], planka_card_id: str) -> None:
        """Migrate attachments for a card."""
        attachments = list(list_kaiten_attachments(
            self.kaiten_session,
            self.settings.kaiten.api_url,
            card['id']
        ))
        
        for attachment in attachments:
            try:
                with self.rate_limiter:
                    self._migrate_single_attachment(attachment, planka_card_id)
            except Exception as e:
                logger.error(f"Failed to migrate attachment {attachment.get('id')}: {e}")
    
    @retry_with_backoff(max_attempts=3)
    def _migrate_single_attachment(self, attachment: Dict[str, Any], planka_card_id: str) -> None:
        """Migrate a single attachment."""
        attachment_url = attachment.get('url', '')
        if not attachment_url:
            raise ValueError("Attachment URL is missing")
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            try:
                # Download attachment
                file_path, checksum = download_attachment(
                    attachment_url,
                    temp_file.name,
                    self.kaiten_session,
                    self.settings.migration.attachment_chunk_size
                )
                
                # Upload to Planka
                upload_result = upload_attachment_to_planka(
                    file_path,
                    planka_card_id,
                    self.planka_session,
                    self.settings.planka.api_url
                )
                
                logger.debug(f"Migrated attachment: {attachment.get('filename', 'unknown')} -> {upload_result.get('id')}")
                
            finally:
                # Clean up temp file
                temp_path = Path(temp_file.name)
                if temp_path.exists():
                    temp_path.unlink()
    
    def _handle_migration_error(
        self, 
        results: MigrationResults, 
        entity_type: str, 
        entity: Dict[str, Any], 
        error: Exception
    ) -> None:
        """Handle migration error for an entity."""
        entity_id = entity.get('id', 'unknown')
        error_msg = f"Failed to migrate {entity_type} {entity_id}: {error}"
        
        logger.error(error_msg)
        self.store.record_error(str(entity_id), entity_type, str(error))
        
        results.errors.append({
            'entity_type': entity_type,
            'entity_id': entity_id,
            'error': str(error)
        })
    
    def _calculate_checksum(self, entity: Dict[str, Any]) -> str:
        """Calculate entity checksum for change detection."""
        # Create stable representation excluding volatile fields
        stable_entity = {k: v for k, v in entity.items() 
                        if k not in ['_planka_board_id', 'updated_at']}
        
        stable_data = json.dumps(stable_entity, sort_keys=True)
        return hashlib.sha256(stable_data.encode()).hexdigest()
