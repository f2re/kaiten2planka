"""Core mapping functions for Kaiten to Planka conversion."""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def map_kaiten_to_planka(entity_type: str, kaiten_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map Kaiten entity to Planka format.
    
    Args:
        entity_type: Type of entity to map (project, board, card, user)
        kaiten_payload: Raw data from Kaiten API
        
    Returns:
        Dictionary with mapped data for Planka
        
    Raises:
        ValueError: If entity_type is not supported
    """
    mapper = {
        'project': map_project,
        'board': map_board,
        'card': map_card,
        'user': map_user,
    }.get(entity_type.lower())
    
    if not mapper:
        raise ValueError(f"Unsupported entity type: {entity_type}")
    
    try:
        result = mapper(kaiten_payload)
        logger.debug("Mapped %s: %s -> %s", entity_type, kaiten_payload.get('id'), result)
        return result
    except Exception as e:
        logger.error("Failed to map %s %s: %s", entity_type, kaiten_payload.get('id'), e)
        raise

def _convert_datetime(dt_str: Optional[str]) -> Optional[str]:
    """Convert Kaiten datetime string to ISO format."""
    if not dt_str:
        return None
    try:
        # Example: "2023-01-01T12:00:00.000000+00:00" -> "2023-01-01T12:00:00.000Z"
        dt = datetime.fromisoformat(dt_str.rstrip('Z'))
        return dt.isoformat(timespec='milliseconds') + 'Z'
    except (ValueError, TypeError) as e:
        logger.warning("Failed to parse datetime '%s': %s", dt_str, e)
        return None

def _map_user_reference(user: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Map user reference to Planka format."""
    if not user:
        return None
    
    return {
        'id': str(user.get('id')),
        'name': user.get('full_name') or user.get('login') or 'Unknown User',
        'username': user.get('login') or f"user_{user.get('id')}",
        'email': user.get('email', ''),
    }
