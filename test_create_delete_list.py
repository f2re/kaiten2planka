#!/usr/bin/env python3
"""
Debug script to test list creation and deletion.
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

def test_create_and_delete_list():
    """Test creating and then deleting a list."""
    print("Testing list creation and deletion...")
    
    # Initialize Planka client
    planka_client = PlankaClient(
        api_url=config.PLANKA_API_URL,
        api_key=config.PLANKA_API_KEY
    )
    
    # First, get a project to work with
    print("\n--- Getting projects ---")
    try:
        projects = planka_client.get_projects()
        if not projects:
            print("No projects found")
            return
            
        project_id = projects[0]['id']
        project_name = projects[0]['name']
        print(f"Using project: {project_name} (ID: {project_id})")
        
        # Get boards for this project
        boards = planka_client.get_boards()
        project_boards = [b for b in boards if b.get('projectId') == project_id]
        
        if not project_boards:
            print("No boards found in project")
            return
            
        board_id = project_boards[0]['id']
        board_name = project_boards[0]['name']
        print(f"Using board: {board_name} (ID: {board_id})")
        
        # Create a new list
        print(f"\n--- Creating new list ---")
        try:
            new_list = planka_client.create_list(
                board_id=board_id,
                name="Test List for Deletion"
            )
            if new_list:
                list_id = new_list['id']
                list_name = new_list['name']
                print(f"✓ Created list: {list_name} (ID: {list_id})")
                
                # Now try to delete the list
                print(f"\n--- Deleting list {list_id} ---")
                try:
                    # Find the list object
                    list_obj = None
                    for project in planka_client.client.projects:
                        try:
                            for board in project.boards:
                                for lst in board.lists:
                                    if lst.id == list_id:
                                        list_obj = lst
                                        break
                                if list_obj:
                                    break
                        except Exception as e:
                            logger.debug(f"Could not get boards/lists for project {project.id}: {e}")
                        if list_obj:
                            break
                    
                    if list_obj:
                        list_obj.delete()
                        print(f"✓ Successfully deleted list {list_id}")
                    else:
                        print(f"✗ Could not find list object for {list_id}")
                        
                except Exception as e:
                    print(f"✗ Error deleting list: {e}")
                    import traceback
                    traceback.print_exc()
                    
            else:
                print("Failed to create list")
                
        except Exception as e:
            print(f"Error creating list: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"Error getting projects/boards: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_create_and_delete_list()