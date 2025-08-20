"""Board mapping functions for Kaiten to Planka conversion."""

from typing import Dict, Any, List, Optional

from .core import _convert_datetime, _map_user_reference


def map_board(kaiten_board: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map Kaiten board to Planka board format.
    
    Args:
        kaiten_board: Raw board data from Kaiten API
        
    Returns:
        Mapped board data for Planka
    """
    # Map Kaiten columns to Planka lists
    lists = []
    for column in kaiten_board.get('columns', []):
        if column.get('type') == 'lane':
            lists.append({
                'id': str(column['id']),
                'name': column.get('title', 'Unnamed List'),
                'position': column.get('position', 0),
                'isArchived': column.get('is_archived', False),
                'createdAt': _convert_datetime(column.get('created')),
                'updatedAt': _convert_datetime(column.get('modified')),
            })
    
    return {
        'id': str(kaiten_board['id']),
        'name': kaiten_board.get('title', 'Unnamed Board'),
        'description': kaiten_board.get('description') or '',
        'projectId': str(kaiten_board.get('project_id', '')),
        'createdAt': _convert_datetime(kaiten_board.get('created')),
        'updatedAt': _convert_datetime(kaiten_board.get('modified')),
        'isArchived': kaiten_board.get('is_archived', False),
        'color': kaiten_board.get('color') or '#1976D2',  # Default blue
        'lists': lists,
        'labels': _map_labels(kaiten_board.get('labels', [])),
        'members': [_map_user_reference(member) for member in kaiten_board.get('members', [])],
        'metadata': {
            'kaiten_id': str(kaiten_board['id']),
            'kaiten_url': kaiten_board.get('url', ''),
            'kaiten_type': kaiten_board.get('type', 'board'),
        },
    }


def _map_labels(kaiten_labels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Map Kaiten labels to Planka labels format."""
    return [
        {
            'id': str(label['id']),
            'name': label.get('name', 'Unnamed Label'),
            'color': label.get('color') or '#E2E2E2',  # Default light gray
        }
        for label in kaiten_labels
        if label.get('id')
    ]
