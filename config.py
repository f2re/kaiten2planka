"""
Centralized configuration management for the application.

This module loads configuration from environment variables and provides
a single source of truth for all configuration settings.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Kaiten Configuration
KAITEN_API_URL = os.getenv('KAITEN_API_URL')
KAITEN_API_KEY = os.getenv('KAITEN_API_KEY')

# Planka Configuration
PLANKA_API_URL = os.getenv('PLANKA_API_URL')
PLANKA_API_KEY = os.getenv('PLANKA_API_KEY')

# Validate that all required environment variables are set
def validate_config():
    """Ensure all required configuration variables are set."""
    required_vars = {
        'KAITEN_API_URL': KAITEN_API_URL,
        'KAITEN_API_KEY': KAITEN_API_KEY,
        'PLANKA_API_URL': PLANKA_API_URL,
        'PLANKA_API_KEY': PLANKA_API_KEY,
    }
    
    missing_vars = [key for key, value in required_vars.items() if not value]
    
    if missing_vars:
        logging.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Run validation on import
validate_config()
