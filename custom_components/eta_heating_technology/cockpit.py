"""Pure helpers for the ETA cockpit panel."""

from __future__ import annotations


def entity_path(entry_id: str, unique_id: str) -> str:
    """
    Return the menu path stored behind the config-entry prefix.

    Unique ids are ``<entry_id>-<full name>``. Colliding names fall back to the
    ETA URI, which is kept as-is so the panel can still show the point.
    """
    prefix = f"{entry_id}-"
    if unique_id.startswith(prefix):
        return unique_id[len(prefix) :]
    return unique_id
