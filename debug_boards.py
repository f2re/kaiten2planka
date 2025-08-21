#!/usr/bin/env python3
"""
Debug script to check Planka API responses for boards.
"""

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config

def debug_planka_boards():
    """Debug Planka API responses for boards."""
    print("Debugging Planka API responses for boards...")
    
    # First create a project to test with
    print("\n--- Creating a test project ---")
    try:
        import requests
        headers = {
            'Authorization': f'Bearer {config.PLANKA_API_URL}',
            'Content-Type': 'application/json'
        }
        # Fix the authorization header
        headers = {
            'Authorization': f'Bearer {config.PLANKA_API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            'name': 'Test Project for Board Debugging',
            'description': 'Test project for board debugging',
            'type': 'private'
        }
        response = requests.post(
            f"{config.PLANKA_API_URL.rstrip('/')}/projects",
            headers=headers,
            json=data
        )
        print(f"Project creation status: {response.status_code}")
        if response.status_code == 200:
            project_data = response.json()
            project_id = project_data['item']['id']
            print(f"Created project with ID: {project_id}")
            
            # Now test creating a board
            print("\n--- Testing board creation ---")
            board_data = {
                'name': 'Test Board',
                'description': 'Test board for debugging',
                'type': 'kanban',
                'position': 65535
            }
            board_response = requests.post(
                f"{config.PLANKA_API_URL.rstrip('/')}/projects/{project_id}/boards",
                headers=headers,
                json=board_data
            )
            print(f"Board creation status: {board_response.status_code}")
            print(f"Board response text: {board_response.text}")
            if board_response.status_code == 200:
                print(f"Board response JSON: {board_response.json()}")
            
            # Clean up - delete the project
            print("\n--- Cleaning up test project ---")
            delete_response = requests.delete(
                f"{config.PLANKA_API_URL.rstrip('/')}/projects/{project_id}",
                headers=headers
            )
            print(f"Project deletion status: {delete_response.status_code}")
        else:
            print(f"Failed to create project: {response.text}")
    except Exception as e:
        print(f"Error in debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_planka_boards()