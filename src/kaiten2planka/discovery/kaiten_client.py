"""Kaiten API client with pagination support."""

from typing import Iterator, Dict, Any, List, Optional
import requests
import time
import logging
from dataclasses import dataclass

from .pagination import PaginationInfo, handle_pagination

logger = logging.getLogger(__name__)


def _handle_rate_limit(response: requests.Response) -> None:
    """Handle rate limiting based on response headers."""
    if 'X-RateLimit-Remaining' in response.headers:
        remaining = int(response.headers['X-RateLimit-Remaining'])
        if remaining < 10:  # Conservative threshold
            reset_time = response.headers.get('X-RateLimit-Reset')
            if reset_time:
                wait_time = max(1, int(reset_time) - int(time.time()))
                logger.warning("Rate limit approaching, waiting %ss", wait_time)
                time.sleep(wait_time)


def list_kaiten_projects(session: requests.Session, base_url: str) -> Iterator[Dict[str, Any]]:
    """
    List all projects from Kaiten with pagination.
    
    Args:
        session: Authenticated requests session
        base_url: Kaiten API base URL
        
    Yields:
        Individual project data
        
    Raises:
        requests.RequestException: If API request fails
    """
    page = 1
    per_page = 50
    
    while True:
        try:
            response = session.get(
                f"{base_url}/projects",
                params={'page': page, 'per_page': per_page}
            )
            response.raise_for_status()
            _handle_rate_limit(response)
            
            data = response.json()
            projects = data.get('data', [])
            
            if not projects:
                break
                
            for project in projects:
                yield project
            
            # Check if we have more pages
            pagination = data.get('pagination', {})
            if page >= pagination.get('total_pages', 1):
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            logger.error("Failed to fetch projects page %d: %s", page, e)
            raise


def list_kaiten_cards(
    session: requests.Session, 
    base_url: str,
    project_id: Optional[str] = None,
    board_id: Optional[str] = None
) -> Iterator[Dict[str, Any]]:
    """
    List all cards from Kaiten with optional filtering.
    
    Args:
        session: Authenticated requests session
        base_url: Kaiten API base URL
        project_id: Optional project ID to filter by
        board_id: Optional board ID to filter by
        
    Yields:
        Individual card data
        
    Raises:
        requests.RequestException: If API request fails
    """
    params = {}
    if project_id:
        params['project_id'] = project_id
    if board_id:
        params['board_id'] = board_id
    
    page = 1
    per_page = 50
    
    while True:
        try:
            response = session.get(
                f"{base_url}/cards",
                params={
                    'page': page,
                    'per_page': per_page,
                    **params
                }
            )
            response.raise_for_status()
            _handle_rate_limit(response)
            
            data = response.json()
            cards = data.get('data', [])
            
            if not cards:
                break
                
            for card in cards:
                yield card
            
            # Check if we have more pages
            pagination = data.get('pagination', {})
            if page >= pagination.get('total_pages', 1):
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            logger.error("Failed to fetch cards page %d: %s", page, e)
            raise


def list_kaiten_attachments(
    session: requests.Session,
    base_url: str,
    card_id: str
) -> Iterator[Dict[str, Any]]:
    """
    List all attachments from a Kaiten card.
    
    Args:
        session: Authenticated requests session
        base_url: Kaiten API base URL
        card_id: ID of the card to get attachments for
        
    Yields:
        Individual attachment data
        
    Raises:
        requests.RequestException: If API request fails
    """
    try:
        response = session.get(f"{base_url}/cards/{card_id}/attachments")
        response.raise_for_status()
        _handle_rate_limit(response)
        
        attachments = response.json().get('data', [])
        
        for attachment in attachments:
            yield attachment
            
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch attachments for card %s: %s", card_id, e)
        raise
