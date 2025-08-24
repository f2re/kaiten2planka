#!/usr/bin/env python3
"""
Debug script to test the delete_all_boards_and_projects method.
"""

import sys
import os
import logging

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from planka_client.client import PlankaClient
import config

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_delete_all():
    """Debug the delete_all_boards_and_projects method."""
    print("Debugging delete_all_boards_and_projects method...")
    
    # Initialize Planka client
    planka_client = PlankaClient(
        api_url=config.PLANKA_API_URL,
        api_key=config.PLANKA_API_KEY
    )
    
    print("\n--- Testing delete_all_boards_and_projects ---")
    try:
        result = planka_client.delete_all_boards_and_projects()
        print(f"Result: {result}")
        
        # Check final state
        print("\n--- Final state check ---")
        projects = planka_client.get_projects()
        print(f"Projects remaining: {len(projects)}")
        
        boards = planka_client.get_boards()
        print(f"Boards remaining: {len(boards)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_delete_all()