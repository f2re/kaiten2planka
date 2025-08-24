#!/usr/bin/env python3
"""
Debug script to understand the exact API response structure.
"""

import sys
import os
import requests
import logging

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_api_responses():
    """Debug the actual API responses to understand the structure."""
    print("Debugging API responses...")
    
    # Set up headers
    headers = {
        'Authorization': f'Bearer {config.PLANKA_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("\n--- Testing GET /projects ---")
    try:
        response = requests.get(
            f"{config.PLANKA_API_URL}/projects",
            headers=headers
        )
        print(f"Status code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Look at the first few projects
                items = data.get('items', [])
                print(f"Found {len(items)} projects")
                if items:
                    first_project = items[0]
                    print(f"First project keys: {list(first_project.keys())}")
                    print(f"First project: {first_project}")
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                print(f"Response text: {response.text[:500]}...")
        else:
            print(f"Error: {response.status_code}")
            print(f"Response text: {response.text[:500]}...")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_api_responses()