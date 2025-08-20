"""Project mapping functions for Kaiten to Planka conversion."""

from typing import Dict, Any

from .core import _convert_datetime, _map_user_reference


def map_project(kaiten_project: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map Kaiten project to Planka project format.
    
    Args:
        kaiten_project: Raw project data from Kaiten API
        
    Returns:
        Mapped project data for Planka
    """
    return {
        'id': str(kaiten_project['id']),
        'name': kaiten_project.get('name', 'Unnamed Project'),
        'description': kaiten_project.get('description') or '',
        'createdAt': _convert_datetime(kaiten_project.get('created')),
        'updatedAt': _convert_datetime(kaiten_project.get('modified')),
        'isArchived': kaiten_project.get('is_archived', False),
        'isTemplate': kaiten_project.get('is_template', False),
        'color': kaiten_project.get('color') or '#1976D2',  # Default blue
        'creator': _map_user_reference(kaiten_project.get('created_by')),
        'members': [_map_user_reference(member) for member in kaiten_project.get('members', [])],
        'metadata': {
            'kaiten_id': str(kaiten_project['id']),
            'kaiten_url': kaiten_project.get('url', ''),
        },
    }
