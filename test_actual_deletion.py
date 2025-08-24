#!/usr/bin/env python3
"""
Simple test to verify that project deletion is actually working.
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

def test_actual_deletion():
    """Test actual project deletion."""
    print("Testing actual project deletion...")
    
    # Initialize Planka client
    planka_client = PlankaClient(
        api_url=config.PLANKA_API_URL,
        api_key=config.PLANKA_API_KEY
    )
    
    print("\n--- Getting all projects BEFORE deletion ---")
    try:
        projects_before = planka_client.get_projects()
        count_before = len(projects_before)
        print(f"Found {count_before} projects before deletion")
        
        # Show first few projects
        for i, project in enumerate(projects_before[:3]):
            print(f"  {i+1}. {project['name']} (ID: {project['id']})")
    except Exception as e:
        print(f"Error getting projects before deletion: {e}")
        return False
    
    if count_before == 0:
        print("No projects to delete")
        return True
    
    # Try to delete ONE project for testing
    project_to_delete = projects_before[0]
    project_id = project_to_delete['id']
    project_name = project_to_delete['name']
    
    print(f"\n--- Attempting to delete project: {project_name} (ID: {project_id}) ---")
    try:
        if planka_client.delete_project(project_id):
            print(f"✓ Successfully deleted project: {project_name}")
        else:
            print(f"✗ Failed to delete project: {project_name}")
            return False
    except Exception as e:
        print(f"Error deleting project: {e}")
        return False
    
    print("\n--- Getting all projects AFTER deletion ---")
    try:
        projects_after = planka_client.get_projects()
        count_after = len(projects_after)
        print(f"Found {count_after} projects after deletion")
        print(f"Change: {count_before} → {count_after} (Δ: {count_after - count_before})")
        
        # Check if the deleted project is really gone
        project_ids_after = [p['id'] for p in projects_after]
        if project_id in project_ids_after:
            print(f"✗ Project {project_id} still exists after deletion!")
            return False
        else:
            print(f"✓ Project {project_id} is confirmed deleted")
            
        # Show first few remaining projects
        for i, project in enumerate(projects_after[:3]):
            print(f"  {i+1}. {project['name']} (ID: {project['id']})")
            
        return True
    except Exception as e:
        print(f"Error getting projects after deletion: {e}")
        return False

if __name__ == "__main__":
    success = test_actual_deletion()
    if success:
        print("\n✓ Test passed!")
        sys.exit(0)
    else:
        print("\n✗ Test failed!")
        sys.exit(1)