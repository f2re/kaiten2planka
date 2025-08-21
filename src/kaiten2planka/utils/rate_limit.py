"""Rate limiting utilities."""

import time
import threading
from typing import Optional


class RateLimiter:
    """Thread-safe rate limiter."""
    
    def __init__(self, requests_per_second: float):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0
        self.last_request_time = 0.0
        self._lock = threading.Lock()
    
    def wait_if_needed(self) -> None:
        """Wait if necessary to respect rate limit."""
        if self.min_interval == 0:
            return
            
        with self._lock:
            current_time = time.time()
            elapsed = current_time - self.last_request_time
            
            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                time.sleep(sleep_time)
                self.last_request_time = time.time()
            else:
                self.last_request_time = current_time
    
    def __enter__(self):
        """Context manager entry."""
        self.wait_if_needed()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass
