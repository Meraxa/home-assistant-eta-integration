"""Tests for cockpit path handling. No Home Assistant runtime."""

from custom_components.eta_heating_technology.cockpit import entity_path


def test_entity_path_strips_config_entry_prefix() -> None:
    """The panel keeps the ETA menu path after the entry id."""
    assert entity_path("01KFS4Z1", "01KFS4Z1-Kessel.Kessel") == "Kessel.Kessel"


def test_entity_path_keeps_uri_fallback() -> None:
    """Colliding menu names are stored as the ETA URI and stay unchanged."""
    uri = "/120/10101/0/0/12168"
    assert entity_path("01KFS4Z1", f"01KFS4Z1-{uri}") == uri


def test_entity_path_without_prefix_is_unchanged() -> None:
    """A unique id from another entry is not cut at a hyphen inside the path."""
    assert entity_path("other", "Kessel.Ein/Aus Taste") == "Kessel.Ein/Aus Taste"
