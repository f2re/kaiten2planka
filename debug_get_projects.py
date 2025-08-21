#!/usr/bin/env python3
"""
Debug script to check get_projects API response.
"""

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config

def debug_get_projects():
    """Debug get_projects API response."""
    print("Debugging get_projects API response...")
    
    # Make direct API call
    try:
        import requests
        headers = {
            'Authorization': f'Bearer {config.PLANKA_API_KEY}',
            'Content-Type': 'application/json'
        }
        response = requests.get(
            f"{config.PLANKA_API_URL.rstrip('/')}/projects",
            headers=headers
        )
        print(f"Get projects status: {response.status_code}")
        print(f"Get projects response text: {response.text}")
        if response.status_code == 200:
            print(f"Get projects response JSON: {response.json()}")
    except Exception as e:
        print(f"Error in debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_get_projects()