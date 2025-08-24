#!/usr/bin/env python3
"""
Debug script to test deletion of a specific list by ID.
"""

import sys
import os
import logging
import requests

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from planka_client.client import PlankaClient
import config

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_specific_list_deletion(list_id: str):
    """Test deletion of a specific list by ID."""
    print(f"Testing deletion of list {list_id}...")
    
    # Initialize Planka client
    planka_client = PlankaClient(
        api_url=config.PLANKA_API_URL,
        api_key=config.PLANKA_API_KEY
    )
    
    # First, let's check if we can find this list
    print(f"\n--- Looking for list {list_id} ---")
    try:
        # Find the list across all projects and boards
        list_obj = None
        project_obj = None
        board_obj = None
        
        for project in planka_client.client.projects:
            try:
                for board in project.boards:
                    try:
                        for lst in board.lists:
                            if lst.id == list_id:
                                list_obj = lst
                                board_obj = board
                                project_obj = project
                                break
                        if list_obj:
                            break
                    except Exception as e:
                        logger.debug(f"Could not get lists for board {board.id}: {e}")
                    if list_obj:
                        break
            except Exception as e:
                logger.debug(f"Could not get boards for project {project.id}: {e}")
            if list_obj:
                break
        
        if list_obj:
            print(f"✓ Found list: {list_obj.name}")
            print(f"  In board: {board_obj.name} (ID: {board_obj.id})")
            print(f"  In project: {project_obj.name} (ID: {project_obj.id})")
            
            # Check if list has any cards
            try:
                cards = list_obj.cards
                print(f"  List has {len(cards)} cards")
                for card in cards[:3]:  # Show first 3 cards
                    print(f"    - {card.name} (ID: {card.id})")
                if len(cards) > 3:
                    print(f"    ... and {len(cards) - 3} more cards")
            except Exception as e:
                print(f"  Could not get cards: {e}")
            
        else:
            print(f"✗ List {list_id} not found")
            return
            
    except Exception as e:
        print(f"Error finding list: {e}")
        return
    
    # Now try to delete the list directly using the API
    print(f"\n--- Attempting direct API deletion of list {list_id} ---")
    try:
        headers = {
            'Authorization': f'Bearer {config.PLANKA_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Try to get the list first
        response = requests.get(
            f"{config.PLANKA_API_URL}/lists/{list_id}",
            headers=headers
        )
        print(f"GET list status: {response.status_code}")
        if response.status_code == 200:
            list_data = response.json()
            print(f"List data: {list_data}")
        elif response.status_code == 404:
            print("List not found (may already be deleted)")
            return
        else:
            print(f"Error getting list: {response.status_code}")
            print(f"Response: {response.text}")
            
        # Try to delete the list
        delete_response = requests.delete(
            f"{config.PLANKA_API_URL}/lists/{list_id}",
            headers=headers
        )
        print(f"DELETE list status: {delete_response.status_code}")
        if delete_response.status_code == 200:
            print("✓ List deleted successfully")
        elif delete_response.status_code == 404:
            print("ℹ List not found (may already be deleted)")
        elif delete_response.status_code == 403:
            print("✗ Forbidden to delete list")
            print(f"Response: {delete_response.text}")
        else:
            print(f"✗ Unexpected error: {delete_response.status_code}")
            print(f"Response: {delete_response.text}")
            
    except Exception as e:
        print(f"Error with direct API call: {e}")
    
    # Now try to delete using plankapy
    print(f"\n--- Attempting plankapy deletion of list {list_id} ---")
    try:
        if list_obj:
            list_obj.delete()
            print("✓ List deleted successfully using plankapy")
        else:
            print("Cannot delete: list object not found")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print("ℹ List not found (may already be deleted)")
        elif e.response.status_code == 403:
            print("✗ Forbidden to delete list using plankapy")
            print(f"Response: {e.response.text if e.response else 'No response'}")
        else:
            print(f"✗ HTTP error deleting list: {e}")
            print(f"Response: {e.response.text if e.response else 'No response'}")
    except Exception as e:
        print(f"Error deleting list using plankapy: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        list_id = sys.argv[1]
    else:
        # Use one of the problematic list IDs from the error
        list_id = "1582154351567176782"
    
    test_specific_list_deletion(list_id)