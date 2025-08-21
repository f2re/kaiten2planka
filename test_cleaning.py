#!/usr/bin/env python3
"""
Test script to verify project cleaning functionality.
"""

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from planka_client import PlankaClient
import config

def test_cleaning():
    """Test the project cleaning functionality."""
    print("Testing project cleaning functionality...")
    
    # Initialize Planka client
    planka_client = PlankaClient(
        api_url=config.PLANKA_API_URL,
        api_key=config.PLANKA_API_KEY
    )
    
    # Get all projects first
    print("Getting existing projects...")
    try:
        projects = planka_client.get_projects()
        print(f"Current projects: {len(projects)}")
        for project in projects:
            print(f"  - {project.get('name', 'Unknown')} (ID: {project.get('id', 'Unknown')})")
    except Exception as e:
        print(f"Error getting projects: {e}")
        return False
    
    # Create a test project
    print("\nCreating a test project...")
    try:
        test_project = planka_client.create_project(
            name="Test Project for Cleaning",
            description="This is a test project that should be deleted",
            type="private"
        )
        print(f"Created test project: {test_project}")
        
        if not test_project or 'id' not in test_project:
            print("Failed to create test project - invalid response")
            return False
            
        project_id = test_project['id']
        print(f"Created test project with ID: {project_id}")
        
        # Get all projects to verify it exists
        projects_before = planka_client.get_projects()
        print(f"Number of projects before cleaning: {len(projects_before)}")
        
        # Try to delete the project
        print("Deleting the test project...")
        if planka_client.delete_project(project_id):
            print("Successfully deleted test project")
        else:
            print("Failed to delete test project")
            return False
        
        # Get all projects to verify it was deleted
        projects_after = planka_client.get_projects()
        print(f"Number of projects after cleaning: {len(projects_after)}")
        
        return True
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cleaning()
    if success:
        print("\n✅ Test passed!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)