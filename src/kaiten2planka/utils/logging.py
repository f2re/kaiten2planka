"""Logging configuration utilities."""

import logging
import logging.config
import sys
from typing import Optional
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON log formatter."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)


def setup_logging(level: str = 'INFO', log_file: Optional[str] = None, format_type: str = 'json'):
    """
    Setup application logging.
    
    Args:
        level: Logging level
        log_file: Optional log file path
        format_type: Format type ('json' or 'text')
    """
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    if format_type == 'json':
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
    handlers.append(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        if format_type == 'json':
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        handlers=handlers,
        force=True
    )
    
    # Set third-party loggers to WARNING
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
