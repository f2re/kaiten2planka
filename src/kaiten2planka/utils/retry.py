"""Retry utilities with exponential backoff."""

import time
import random
import logging
from typing import Callable, Any, Type, Tuple
from functools import wraps

logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_attempts: int = 5,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
        max_delay: Maximum delay between retries
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts")
                        raise last_exception
                    
                    # Calculate delay with exponential backoff and jitter
                    delay = min(
                        backoff_factor ** attempt + random.uniform(0, 1),
                        max_delay
                    )
                    
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{max_attempts}), "
                        f"retrying in {delay:.2f}s: {e}"
                    )
                    time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator
