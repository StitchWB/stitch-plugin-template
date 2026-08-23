"""Service layer for this service plugin.

Business logic lives here — ``__main__.py`` handlers are thin wrappers
that parse params, call service functions, and return results. This
mirrors the reference plugins (stitch-cards, stitch-totp, …) where
``service.py`` holds the domain logic and ``__main__.py`` only dispatches.

Replace the placeholder functions below with your own domain logic.
"""

# _generated_by: stitch_plugin_tools scaffold v3

from __future__ import annotations

from typing import Any


def health_check() -> dict[str, Any]:
    """Return a health-check response."""
    return {"pong": True}


def echo(text: str) -> dict[str, Any]:
    """Echo the provided text back to the caller."""
    return {"text": text}
