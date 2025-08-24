#!/usr/bin/env python3
"""
Simple test to check existing lists and try to delete one.
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

def test_existing_lists():
    """Test getting existing lists and trying to delete one."""
    print("Testing existing lists...")
    
    # Initialize Planka client
    planka_client = PlankaClient(
        api_url=config.PLANKA_API_URL,
        api_key=config.PLANKA_API_KEY
    )
    
    # Get all boards
    print("\n--- Getting all boards ---")
    try:
        boards = planka_client.get_boards()
        print(f"Found {len(boards)} boards")
        
        if not boards:
            print("No boards found")
            return
            
        # Take the first board that has a valid ID
        board_id = boards[0]['id']
        board_name = boards[0]['name']
        project_id = boards[0].get('projectId', 'Unknown')
        print(f"Using board: {board_name} (ID: {board_id}) in project {project_id}")
        
        # Get lists for this board
        print(f"\n--- Getting lists for board {board_id} ---")
        try:
            lists = planka_client.get_lists(board_id)
            print(f"Found {len(lists)} lists in board {board_id}")
            
            if not lists:
                print("No lists found in board")
                return
                
            # Take the first list
            list_id = lists[0]['id']
            list_name = lists[0]['name']
            print(f"Using list: {list_name} (ID: {list_id})")
            
            # Try to delete this list
            print(f"\n--- Attempting to delete list {list_id} ---")
            try:
                # Find the list object
                list_obj = None
                for project in planka_client.client.projects:
                    try:
                        for board in project.boards:
                            if board.id == board_id:
                                try:
                                    for lst in board.lists:
                                        if lst.id == list_id:
                                            list_obj = lst
                                            break
                                except Exception as e:
                                    logger.debug(f"Could not get lists: {e}")
                                break
                    except Exception as e:
                        logger.debug(f"Could not get boards: {e}")
                    if list_obj:
                        break
                
                if list_obj:
                    list_obj.delete()
                    print(f"✓ Successfully deleted list {list_id}")
                else:
                    print(f"✗ Could not find list object for {list_id}")
                    
            except Exception as e:
                print(f"✗ Error deleting list {list_id}: {e}")
                import traceback
                traceback.print_exc()
                
        except Exception as e:
            print(f"Error getting lists for board {board_id}: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"Error getting boards: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_existing_lists()