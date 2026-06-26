"""API layer for Claude Code Proxy."""

try:
    # Importing create_app pulls in app-level dependencies (routes, core modules).
    # Keep this behind a try/except so lightweight imports (like tests) don't
    # execute the full application import graph and fail early on unrelated
    # syntax/runtime issues in other modules.
    from .app import create_app
except Exception:
    create_app = None

from .models import (
    MessagesRequest,
    MessagesResponse,
    TokenCountRequest,
    TokenCountResponse,
)

__all__ = [
    "MessagesRequest",
    "MessagesResponse",
    "TokenCountRequest",
    "TokenCountResponse",
    "create_app",
]
