"""Project mapping functionality."""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def map_project(kaiten_project: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map Kaiten project to Planka board.
    
    Args:
        kaiten_project: Kaiten project data
        
    Returns:
        Planka board data
    """
    # Preserve original timestamps
    description = kaiten_project.get('description', '')
    
    if 'created_at' in kaiten_project or 'updated_at' in kaiten_project:
        description += '\n\n--- Original Timestamps ---\n'
        if 'created_at' in kaiten_project:
            description += f'Created: {kaiten_project["created_at"]}\n'
        if 'updated_at' in kaiten_project:
            description += f'Updated: {kaiten_project["updated_at"]}\n'
    
    planka_board = {
        'name': kaiten_project.get('title', kaiten_project.get('name', '')),
        'description': description,
        'position': kaiten_project.get('position', 0),
    }
    
    # Handle background color if present
    if 'color' in kaiten_project:
        planka_board['background_color'] = kaiten_project['color']
    
    logger.debug(f"Mapped project {kaiten_project.get('id')} to board")
    return planka_board
