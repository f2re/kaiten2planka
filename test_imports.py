#!/usr/bin/env python3
"""
Test script to verify that all modules can be imported correctly.
"""

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported without errors."""
    try:
        from kaiten_client import KaitenClient
        print("✓ KaitenClient imported successfully")
    except Exception as e:
        print(f"✗ Failed to import KaitenClient: {e}")
        return False
    
    try:
        from planka_client import PlankaClient
        print("✓ PlankaClient imported successfully")
    except Exception as e:
        print(f"✗ Failed to import PlankaClient: {e}")
        return False
    
    try:
        from migrator import KaitenToPlankaMigrator
        print("✓ KaitenToPlankaMigrator imported successfully")
    except Exception as e:
        print(f"✗ Failed to import KaitenToPlankaMigrator: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing module imports...")
    if test_imports():
        print("All modules imported successfully!")
    else:
        print("Some modules failed to import.")
        sys.exit(1)