#!/usr/bin/env python3
"""
Utility script for common tasks related to the Kaiten to Planka migration.
"""

import os
import sys
import argparse
from dotenv import load_dotenv
import yaml

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kaiten_client import KaitenClient
from planka_client import PlankaClient

# Load environment variables
load_dotenv()

def load_config(config_path: str = "config.yaml"):
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Configuration file {config_path} not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML configuration: {e}")
        sys.exit(1)

def test_kaiten_connection():
    """Test connection to Kaiten API."""
    print("Testing Kaiten connection...")
    config = load_config()
    kaiten_config = config['kaiten']
    
    try:
        kaiten_client = KaitenClient(
            api_url=kaiten_config['api_url'],
            api_key=os.path.expandvars(kaiten_config['api_key'])
        )
        boards = kaiten_client.get_boards()
        print(f"✓ Successfully connected to Kaiten. Found {len(boards)} boards.")
        return True
    except Exception as e:
        print(f"✗ Failed to connect to Kaiten: {e}")
        return False

def test_planka_connection():
    """Test connection to Planka API."""
    print("Testing Planka connection...")
    config = load_config()
    planka_config = config['planka']
    
    try:
        planka_client = PlankaClient(
            api_url=planka_config['api_url'],
            api_key=os.path.expandvars(planka_config['api_key'])
        )
        projects = planka_client.get_projects()
        print(f"✓ Successfully connected to Planka. Found {len(projects)} projects.")
        return True
    except Exception as e:
        print(f"✗ Failed to connect to Planka: {e}")
        return False

def main():
    """Main function to run utility tasks."""
    parser = argparse.ArgumentParser(description="Kaiten to Planka migration utilities")
    parser.add_argument(
        "task",
        choices=["test-kaiten", "test-planka", "test-both"],
        help="Task to perform"
    )
    
    args = parser.parse_args()
    
    if args.task == "test-kaiten":
        test_kaiten_connection()
    elif args.task == "test-planka":
        test_planka_connection()
    elif args.task == "test-both":
        kaiten_success = test_kaiten_connection()
        planka_success = test_planka_connection()
        
        if kaiten_success and planka_success:
            print("\n✓ Both connections successful! You're ready to run the migration.")
        else:
            print("\n✗ One or both connections failed. Please check your configuration.")
            sys.exit(1)

if __name__ == "__main__":
    main()