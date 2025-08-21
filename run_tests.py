#!/usr/bin/env python3
"""
Test runner for all migration tests.
"""

import sys
import os
import unittest

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """Run all tests."""
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())