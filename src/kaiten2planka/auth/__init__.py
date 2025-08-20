"""Authentication modules for Kaiten and Planka APIs."""

from .kaiten import authenticate_kaiten
from .planka import authenticate_planka

__all__ = ["authenticate_kaiten", "authenticate_planka"]
