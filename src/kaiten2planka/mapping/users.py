"""User mapping functionality."""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def map_user(kaiten_user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map Kaiten user to Planka user.
    
    Args:
        kaiten_user: Kaiten user data
        
    Returns:
        Planka user data
    """
    planka_user = {
        'username': kaiten_user.get('username', kaiten_user.get('login', '')),
        'name': kaiten_user.get('name', kaiten_user.get('full_name', '')),
        'email': kaiten_user.get('email', ''),
    }
    
    # Handle avatar if present
    if 'avatar' in kaiten_user:
        planka_user['avatar_url'] = kaiten_user['avatar']
    
    # Handle role/permissions
    if 'role' in kaiten_user:
        # Map Kaiten roles to Planka roles
        role_mapping = {
            'admin': 'admin',
            'manager': 'user', 
            'user': 'user',
            'viewer': 'user'
        }
        planka_user['role'] = role_mapping.get(
            kaiten_user['role'].lower(), 'user'
        )
    
    logger.debug(f"Mapped user {kaiten_user.get('id')} to Planka format")
    return planka_user
