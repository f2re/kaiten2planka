#!/usr/bin/env python3
"""
Comprehensive test to create and delete a full project-board-list hierarchy.
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

def test_full_hierarchy():
    """Test creating and deleting a full project-board-list hierarchy."""
    print("Testing full project-board-list hierarchy creation and deletion...")
    
    # Initialize Planka client
    planka_client = PlankaClient(
        api_url=config.PLANKA_API_URL,
        api_key=config.PLANKA_API_KEY
    )
    
    # Create a new project
    print("\n--- Creating new project ---")
    try:
        project = planka_client.create_project(
            name="Test Project for Deletion",
            description=" ",  # Space character instead of empty string to avoid API error
            type="private"
        )
        if project:
            project_id = project['id']
            project_name = project['name']
            print(f"✓ Created project: {project_name} (ID: {project_id})")
            
            # Create a board in this project
            print(f"\n--- Creating new board in project {project_id} ---")
            try:
                board = planka_client.create_board(
                    project_id=project_id,
                    name="Test Board for Deletion"
                )
                if board:
                    board_id = board['id']
                    board_name = board['name']
                    print(f"✓ Created board: {board_name} (ID: {board_id})")
                    
                    # Create a list in this board
                    print(f"\n--- Creating new list in board {board_id} ---")
                    try:
                        new_list = planka_client.create_list(
                            board_id=board_id,
                            name="Test List for Deletion"
                        )
                        if new_list:
                            list_id = new_list['id']
                            list_name = new_list['name']
                            print(f"✓ Created list: {list_name} (ID: {list_id})")
                            
                            # Try to delete the list directly
                            print(f"\n--- Deleting list {list_id} ---")
                            try:
                                # Find the list object
                                list_obj = None
                                for project in planka_client.client.projects:
                                    if project.id == project_id:
                                        try:
                                            for board in project.boards:
                                                if board.id == board_id:
                                                    for lst in board.lists:
                                                        if lst.id == list_id:
                                                            list_obj = lst
                                                            break
                                                    if list_obj:
                                                        break
                                        except Exception as e:
                                            logger.debug(f"Could not get boards/lists: {e}")
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
                        
                else:
                    print("Failed to create board")
                    
            except Exception as e:
                print(f"Error creating board: {e}")
                import traceback
                traceback.print_exc()
                
            # Now delete the entire project (which should delete board and list)
            print(f"\n--- Deleting project {project_id} with all contents ---")
            try:
                if planka_client.delete_project(project_id):
                    print(f"✓ Successfully deleted project {project_id} with all contents")
                else:
                    print(f"✗ Failed to delete project {project_id}")
                    
            except Exception as e:
                print(f"✗ Error deleting project: {e}")
                import traceback
                traceback.print_exc()
                
        else:
            print("Failed to create project")
            
    except Exception as e:
        print(f"Error creating project: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_hierarchy()