"""Utils for eta_heating_technology."""

from .api import Value
from .const import ETA_BINARY_SENSOR_VALUES_DE, ETA_SENSOR_UNITS, ETA_STRING_SENSOR_VALUES_DE, EtaSensorType


def determine_sensor_type(value: Value) -> EtaSensorType | None:
    """Determine the sensor type based on the value's unit and string representation."""
    sensor_unit = value.unit
    if sensor_unit in ETA_SENSOR_UNITS:
        return EtaSensorType.SENSOR
    if value.value in ETA_BINARY_SENSOR_VALUES_DE:
        return EtaSensorType.BINARY_SENSOR
    if value.value in ETA_STRING_SENSOR_VALUES_DE:
        return EtaSensorType.STRING_SENSOR
    # Fallback: unitless values with a non-empty strValue are string sensors
    # This covers all ETA state code ranges (2000, 4000, etc.)
    if value.unit == "" and value.str_value:
        return EtaSensorType.STRING_SENSOR
    return None
