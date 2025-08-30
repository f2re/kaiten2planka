"""
Planka client package.
"""

from .patcher import patch_plankapy
from .client import PlankaClient

# Apply patches when package is imported
patch_plankapy()

__all__ = ['PlankaClient']