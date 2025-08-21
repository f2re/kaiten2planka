#!/usr/bin/env python3
"""
Debug script to check Planka API responses.
"""

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from planka_client import PlankaClient
import config

def debug_planka():
    """Debug Planka API responses."""
    print("Debugging Planka API responses...")
    
    # Initialize Planka client
    planka_client = PlankaClient(
        api_url=config.PLANKA_API_URL,
        api_key=config.PLANKA_API_KEY
    )
    
    # Test getting projects
    print("\n--- Testing get_projects ---")
    try:
        projects = planka_client.get_projects()
        print(f"Projects response: {projects}")
        print(f"Type: {type(projects)}")
    except Exception as e:
        print(f"Error getting projects: {e}")
        import traceback
        traceback.print_exc()
    
    # Test creating a project with direct API call
    print("\n--- Testing direct API call ---")
    try:
        import requests
        headers = {
            'Authorization': f'Bearer {config.PLANKA_API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            'name': 'Direct API Test Project',
            'description': 'Test project created via direct API call',
            'type': 'private'
        }
        response = requests.post(
            f"{config.PLANKA_API_URL.rstrip('/')}/projects",
            headers=headers,
            json=data
        )
        print(f"Direct API response status: {response.status_code}")
        print(f"Direct API response headers: {response.headers}")
        print(f"Direct API response text: {response.text}")
        if response.status_code == 200:
            print(f"Direct API response JSON: {response.json()}")
    except Exception as e:
        print(f"Error in direct API call: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_planka()
