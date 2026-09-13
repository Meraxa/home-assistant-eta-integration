"""Tests for eta_heating_technology utils helpers."""

from types import SimpleNamespace

from custom_components.eta_heating_technology.utils import (
    entity_data_key,
    entity_display_name,
    entity_unique_key,
)


def _obj(uri: str, full_name: str) -> SimpleNamespace:
    """Minimal stand-in for api.Object used by the helpers."""
    return SimpleNamespace(uri=uri, full_name=full_name)


def test_entity_data_key_uses_uri() -> None:
    """Coordinator keys must be URI-based so duplicate menu names do not collide."""
    obj = _obj("/120/10101/0/0/12096", "Heizkreis.Heizkreis.Heizgrenze für Heizen")
    assert entity_data_key(obj) == "/120/10101/0/0/12096"


def test_entity_unique_key_keeps_full_name_when_unique() -> None:
    """Non-colliding entities keep the previous unique_id suffix."""
    obj = _obj("/1/2", "Heizkreis.Aussentemperatur")
    assert entity_unique_key(obj, [obj]) == "Heizkreis.Aussentemperatur"


def test_entity_unique_key_uses_uri_on_collision() -> None:
    """Colliding full_names use URI so both entities remain distinct."""
    active = _obj("/120/10101/0/0/12096", "Heizkreis.Heizkreis.Heizgrenze für Heizen")
    inactive = _obj("/120/10101/0/0/14116", "Heizkreis.Heizkreis.Heizgrenze für Heizen")
    objects = [active, inactive]
    assert entity_unique_key(active, objects) == active.uri
    assert entity_unique_key(inactive, objects) == inactive.uri


def test_entity_display_name_unique() -> None:
    """Unique full_name stays unchanged."""
    obj = _obj("/1/2", "Heizkreis.Aussentemperatur")
    assert entity_display_name(obj, [obj]) == "Heizkreis.Aussentemperatur"


def test_entity_display_name_disambiguates_duplicates() -> None:
    """Duplicate full_names append the last URI segment."""
    active = _obj("/120/10101/0/0/12096", "Heizkreis.Heizkreis.Heizgrenze für Heizen")
    inactive = _obj("/120/10101/0/0/14116", "Heizkreis.Heizkreis.Heizgrenze für Heizen")
    objects = [active, inactive]
    assert entity_display_name(active, objects) == (
        "Heizkreis.Heizkreis.Heizgrenze für Heizen (12096)"
    )
    assert entity_display_name(inactive, objects) == (
        "Heizkreis.Heizkreis.Heizgrenze für Heizen (14116)"
    )
