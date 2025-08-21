"""Attachment handling with streaming and checksum validation."""

import os
import hashlib
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    reraise=True
)
def download_attachment(
    url: str, 
    dest_path: str, 
    session: Optional[requests.Session] = None,
    chunk_size: int = 8192
) -> Tuple[str, str]:
    """
    Download attachment with streaming and checksum validation.
    
    Args:
        url: URL to download from
        dest_path: Local path to save file
        session: Optional requests session (for auth)
        chunk_size: Size of chunks for streaming download
        
    Returns:
        Tuple of (file_path, sha256_hash)
        
    Raises:
        requests.RequestException: If download fails
        ValueError: If file validation fails
    """
    if session is None:
        session = requests.Session()
    
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Use temporary file for atomic operation
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            response = session.get(url, stream=True)
            response.raise_for_status()
            
            # Validate content type if possible
            content_type = response.headers.get('content-type', '')
            if content_type.startswith('text/html'):
                raise ValueError("Received HTML instead of file content")
            
            sha256_hash = hashlib.sha256()
            total_size = 0
            
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # Filter out keep-alive chunks
                    temp_file.write(chunk)
                    sha256_hash.update(chunk)
                    total_size += len(chunk)
            
            temp_file.flush()
            
            # Validate file size
            expected_size = response.headers.get('content-length')
            if expected_size and int(expected_size) != total_size:
                raise ValueError(f"Size mismatch: expected {expected_size}, got {total_size}")
            
            # Move to final destination
            shutil.move(temp_file.name, dest_path)
            
            hash_hex = sha256_hash.hexdigest()
            logger.info(f"Downloaded {url} to {dest_path} (SHA256: {hash_hex})")
            
            return str(dest_path), hash_hex
            
        except Exception:
            # Clean up temp file on error
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            raise


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    reraise=True
)
def upload_attachment_to_planka(
    file_path: str,
    planka_entity_id: str,
    session: requests.Session,
    planka_base_url: str
) -> Dict[str, Any]:
    """
    Upload attachment to Planka with retry logic.
    
    Args:
        file_path: Path to local file
        planka_entity_id: ID of Planka entity (card, board, etc.)
        session: Authenticated Planka session
        planka_base_url: Planka API base URL
        
    Returns:
        Upload response data
        
    Raises:
        requests.RequestException: If upload fails
        FileNotFoundError: If file doesn't exist
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Calculate checksum for verification
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    
    original_checksum = sha256_hash.hexdigest()
    
    try:
        with open(file_path, 'rb') as f:
            files = {
                'file': (file_path.name, f, 'application/octet-stream')
            }
            
            response = session.post(
                f"{planka_base_url}/cards/{planka_entity_id}/attachments",
                files=files
            )
            response.raise_for_status()
            
        result = response.json()
        result['original_checksum'] = original_checksum
        
        logger.info(f"Uploaded {file_path} to entity {planka_entity_id}")
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to upload {file_path}: {e}")
        raise
