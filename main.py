#!/usr/bin/env python3
"""
Main script for migrating data from Kaiten to Planka.
"""

import os
import sys
import logging
from typing import Dict, Any
import yaml
from dotenv import load_dotenv

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kaiten_client import KaitenClient
from planka_client import PlankaClient
from migrator import KaitenToPlankaMigrator

# Load environment variables
load_dotenv()

# Set up logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"Configuration file {config_path} not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {e}")
        sys.exit(1)


def main():
    """Main function to run the migration process."""
    logger.info("Starting Kaiten to Planka migration")
    
    # Load configuration
    config = load_config()
    
    # Initialize Kaiten client
    kaiten_config = config['kaiten']
    kaiten_client = KaitenClient(
        api_url=kaiten_config['api_url'],
        api_key=os.path.expandvars(kaiten_config['api_key'])
    )
    
    # Initialize Planka client
    planka_config = config['planka']
    planka_client = PlankaClient(
        api_url=planka_config['api_url'],
        api_key=os.path.expandvars(planka_config['api_key'])
    )
    
    # For now, we'll create a default project to migrate boards into
    # In a more complete implementation, we would migrate projects as well
    projects = planka_client.get_projects()
    if projects:
        project_id = projects[0]['id']  # Use the first project
        logger.info(f"Using existing project: {projects[0]['name']}")
    else:
        # Create a new project if none exists
        project = planka_client.create_project(
            name="Migrated from Kaiten",
            description="Project migrated from Kaiten"
        )
        project_id = project['id']
        logger.info(f"Created new project: {project['name']}")
    
    # Initialize migrator
    migrator = KaitenToPlankaMigrator(kaiten_client, planka_client)
    
    # Perform complete migration
    migrator.migrate_all(project_id)
    
    logger.info("Migration completed successfully")


if __name__ == "__main__":
    main()