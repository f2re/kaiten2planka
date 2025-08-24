#!/usr/bin/env python3
"""
Main script for migrating data from Kaiten to Planka.
"""

import logging
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kaiten_client import KaitenClient
from planka_client import PlankaClient
from migrator import KaitenToPlankaMigrator
import config
from icecream import ic
logger = logging.getLogger(__name__)


def main():
    """Main function to run the migration process."""
    logger.info("Starting Kaiten to Planka migration")

    # Initialize Kaiten client
    kaiten_client = KaitenClient(
        api_url=config.KAITEN_API_URL,
        api_key=config.KAITEN_API_KEY
    )

    # Initialize Planka client
    planka_client = PlankaClient(
        api_url=config.PLANKA_API_URL,
        api_key=config.PLANKA_API_KEY
    )
    
    # Clean all existing projects in Planka before migration
    logger.info("Cleaning all existing projects in Planka")
    if not planka_client.delete_all_boards_and_projects():
        logger.error("Failed to clean existing projects in Planka")
        return
    
    # Verify that all projects are deleted
    try:
        existing_projects = planka_client.get_projects()
        logger.info(f"Found {len(existing_projects)} existing projects after cleanup")
        if existing_projects:
            logger.warning("Some projects still exist after cleanup. This may cause issues.")
            # Continue anyway, but log the warning
    except Exception as e:
        logger.error(f"Error while verifying cleanup: {e}")
    # Initialize migrator
    migrator = KaitenToPlankaMigrator(kaiten_client, planka_client)

    # First, migrate all users
    # migrator.migrate_users()

    # Then, iterate through spaces and migrate each one as a separate project
    kaiten_spaces = kaiten_client.get_spaces()
    if not kaiten_spaces:
        logger.warning("No spaces found in Kaiten. Nothing to migrate.")
        return

    # Iterate over all spaces from Kaiten
    for space in kaiten_spaces:
        # Set space_name as Kaiten Project name only (as requested)
        space_name = space.get('title', f"Kaiten Space {space['id']}")
        logger.info(f"Processing space: {space_name}")

        # Create a new project in Planka for this space
        try:
            ic(space_name)
            project = planka_client.create_project(
                name=space_name,  # Only the Kaiten Project name, nothing else
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
            kaiten_boards = kaiten_client.get_boards_for_space(space['id'])
            if kaiten_boards:
                # Perform migration for this space's data
                migrator.migrate_space_data(project_id, kaiten_boards)
            else:
                logger.info(f"No boards found in space: {space_name}")
        
        except Exception as e:
            logger.error(f"An error occurred while processing space {space_name}: {e}")
            continue
    
    logger.info("Migration process finished.")


if __name__ == "__main__":
    main()