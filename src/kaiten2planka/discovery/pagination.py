"""Pagination utilities for API clients."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PaginationInfo:
    """Pagination information from API response."""
    page: int
    per_page: int
    total: int
    total_pages: int
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PaginationInfo':
        """Create PaginationInfo from API response dictionary."""
        return cls(
            page=data.get('page', 1),
            per_page=data.get('per_page', 20),
            total=data.get('total', 0),
            total_pages=data.get('total_pages', 1)
        )


def handle_pagination(
    session,
    url: str,
    params: Optional[dict] = None,
    page: int = 1,
    per_page: int = 50
) -> tuple[list, PaginationInfo]:
    """
    Handle pagination for API requests.
    
    Args:
        session: Requests session
        url: API endpoint URL
        params: Query parameters
        page: Starting page
        per_page: Items per page
        
    Returns:
        Tuple of (items, pagination_info)
    """
    if params is None:
        params = {}
        
    params.update({
        'page': page,
        'per_page': per_page
    })
    
    response = session.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    items = data.get('data', [])
    pagination = PaginationInfo.from_dict(data.get('pagination', {}))
    
    return items, pagination
