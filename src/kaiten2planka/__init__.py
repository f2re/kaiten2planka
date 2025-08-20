"""Kaiten to Planka migration tool."""

__version__ = "1.0.0"

from .auth.kaiten import authenticate_kaiten
from .auth.planka import authenticate_planka
from .discovery.kaiten_client import (
    list_kaiten_projects,
    list_kaiten_cards,
    list_kaiten_attachments,
)
from .mapping.core import map_kaiten_to_planka
from .storage.attachments import download_attachment, upload_attachment_to_planka
from .migration.engine import MigrationEngine

__all__ = [
    "authenticate_kaiten",
    "authenticate_planka",
    "list_kaiten_projects",
    "list_kaiten_cards",
    "list_kaiten_attachments",
    "map_kaiten_to_planka",
    "download_attachment",
    "upload_attachment_to_planka",
    "MigrationEngine",
]
