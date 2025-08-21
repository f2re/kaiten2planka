"""Card mapping functionality."""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


def map_card(kaiten_card: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map Kaiten card to Planka card.
    
    Args:
        kaiten_card: Kaiten card data
        
    Returns:
        Planka card data
    """
    # Build description with original timestamps
    description = kaiten_card.get('description', '')
    
    # Add original timestamps to custom fields
    custom_fields = {}
    if 'created_at' in kaiten_card:
        custom_fields['original_created_at'] = kaiten_card['created_at']
    if 'updated_at' in kaiten_card:
        custom_fields['original_updated_at'] = kaiten_card['updated_at']
    
    planka_card = {
        'name': kaiten_card.get('title', kaiten_card.get('name', '')),
        'description': description,
        'position': kaiten_card.get('position', 0),
    }
    
    # Handle due date
    if 'due_date' in kaiten_card:
        planka_card['due_date'] = kaiten_card['due_date']
    
    # Handle labels
    if 'labels' in kaiten_card and kaiten_card['labels']:
        planka_card['label_names'] = [
            label.get('name', '') for label in kaiten_card['labels']
        ]
        planka_card['label_colors'] = [
            label.get('color', '#808080') for label in kaiten_card['labels']
        ]
    
    # Handle assignees
    if 'assignees' in kaiten_card and kaiten_card['assignees']:
        planka_card['user_ids'] = [
            str(assignee.get('id', '')) for assignee in kaiten_card['assignees']
        ]
    
    # Add custom fields if any
    if custom_fields:
        planka_card['custom_fields'] = custom_fields
    
    # Handle checklists
    if 'checklists' in kaiten_card:
        planka_card['tasks'] = _map_checklists(kaiten_card['checklists'])
    
    logger.debug(f"Mapped card {kaiten_card.get('id')} to Planka format")
    return planka_card


def _map_checklists(checklists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Map Kaiten checklists to Planka tasks."""
    tasks = []
    
    for checklist in checklists:
        checklist_name = checklist.get('name', 'Checklist')
        items = checklist.get('items', [])
        
        for item in items:
            task = {
                'name': f"[{checklist_name}] {item.get('text', '')}",
                'is_completed': item.get('completed', False),
                'position': item.get('position', 0)
            }
            tasks.append(task)
    
    return tasks
