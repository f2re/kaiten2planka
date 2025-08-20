"""Kaiten authentication module."""

from typing import Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

logger = logging.getLogger(__name__)


def authenticate_kaiten(api_key: str, base_url: str) -> requests.Session:
    """
    Authenticate with Kaiten API and return configured session.
    
    Args:
        api_key: Kaiten API key
        base_url: Kaiten API base URL
        
    Returns:
        Authenticated requests session
        
    Raises:
        ValueError: If API key is invalid
        requests.RequestException: If authentication fails
    """
    if not api_key:
        raise ValueError("API key cannot be empty")
    
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'User-Agent': 'kaiten2planka/1.0.0'
    })
    
    # Configure retries
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    # Validate authentication
    try:
        response = session.get(f"{base_url}/me")
        response.raise_for_status()
        logger.info("Successfully authenticated with Kaiten")
        return session
    except requests.exceptions.HTTPError as e:
        if e.response.status_code in [401, 403]:
            raise ValueError("Invalid Kaiten API key") from e
        raise
    except requests.exceptions.RequestException as e:
        logger.error("Failed to authenticate with Kaiten: %s", e)
        raise
