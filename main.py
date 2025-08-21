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
    try:
        existing_projects = planka_client.get_projects()
        for project in existing_projects:
            project_id = project['id']
            project_name = project['name']
            if planka_client.delete_project(project_id):
                logger.info(f"Deleted existing project: {project_name}")
            else:
                logger.error(f"Failed to delete project: {project_name}")
    except Exception as e:
        logger.error(f"Error while cleaning projects: {e}")

    # Initialize migrator
    migrator = KaitenToPlankaMigrator(kaiten_client, planka_client)

    # First, migrate all users
    migrator.migrate_users()

    # Then, iterate through spaces and migrate each one as a separate project
    kaiten_spaces = kaiten_client.get_spaces()
    if not kaiten_spaces:
        logger.warning("No spaces found in Kaiten. Nothing to migrate.")
        return

    for space in kaiten_spaces:
        # Set space_name as Kaiten Project name only (as requested)
        space_name = space.get('name', f"Kaiten Space {space['id']}")
        logger.info(f"Processing space: {space_name}")

        # Create a new project in Planka for this space
        try:
            project = planka_client.create_project(
                name=space_name,  # Only the Kaiten Project name, nothing else
                description="",  # Empty description as requested
                type="private"
            )
            project_id = project['id']
            logger.info(f"Created new project in Planka: {project['name']}")

            # Get boards for this space
            kaiten_boards = kaiten_client.get_boards_for_space(space['id'])
            if kaiten_boards:
                # Perform migration for this space's data
                migrator.migrate_space_data(project_id, kaiten_boards)
            else:
                logger.info(f"No boards found in space: {space_name}")

        except Exception as e:
            logger.error(f"Failed to migrate space {space_name}: {e}")
    
    logger.info("Migration completed successfully")


if __name__ == "__main__":
    main()