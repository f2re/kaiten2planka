#!/usr/bin/env python3
"""
Utility script for common tasks related to the Kaiten to Planka migration.
"""

import os
import sys
import argparse

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kaiten_client import KaitenClient
from planka_client import PlankaClient
import config

def test_kaiten_connection():
    """Test connection to Kaiten API."""
    print("Testing Kaiten connection...")
    try:
        kaiten_client = KaitenClient(
            api_url=config.KAITEN_API_URL,
            api_key=config.KAITEN_API_KEY
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
    try:
        planka_client = PlankaClient(
            api_url=config.PLANKA_API_URL,
            api_key=config.PLANKA_API_KEY
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