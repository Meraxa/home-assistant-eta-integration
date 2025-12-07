"""Constants for ETA heating technology."""

import enum
from logging import Logger, getLogger

from homeassistant.components.sensor import SensorDeviceClass

LOGGER: Logger = getLogger(__package__)

NAME = "ETA Heating Technology"
DEVICE_NAME = "ETA Heating"
DOMAIN = "eta_heating_technology"
ISSUE_URL = "https://github.com/meraxa/home-assistant_eta_integration/issues"

# Configuration and options
CONF_HOST = "host"
CONF_PORT = "port"

CHOSEN_ENTITIES = "chosen_entities"

ETA_SENSOR_UNITS = {
    "°C": SensorDeviceClass.TEMPERATURE,
    "W": SensorDeviceClass.POWER,
    "A": SensorDeviceClass.CURRENT,
    "Hz": SensorDeviceClass.FREQUENCY,
    "Pa": SensorDeviceClass.PRESSURE,
    "V": SensorDeviceClass.VOLTAGE,
    "W/m²": SensorDeviceClass.IRRADIANCE,
    "bar": SensorDeviceClass.PRESSURE,
    "kW": SensorDeviceClass.POWER,
    "kWh": SensorDeviceClass.ENERGY,
    "kg": SensorDeviceClass.WEIGHT,
    "mV": SensorDeviceClass.VOLTAGE,
    "s": SensorDeviceClass.DURATION,
    "%rH": SensorDeviceClass.HUMIDITY,
    "m³/h": SensorDeviceClass.VOLUME_FLOW_RATE,
}

ETA_BINARY_SENSOR_UNITS_DE = {
    "1802": False,  # Aus
    "1803": True,  # Ein
}

ETA_STRING_SENSOR_VALUES_DE = {
    "2004": "Heizversuch",
    "2005": "Zünden",
    "2006": "Heizen",
    "2008": "Glutabbrand wegen Entaschung",
    "2012": "Bereit",
    "2014": "Entaschen",
    "2021": "Heizen",
    "2023": "Stoker leeren",
    "2024": "Füllen",
}


class EtaSensorType(enum.Enum):
    """Enumeration of sensor types."""

    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"
    STRING_SENSOR = "string_sensor"


# Miscellaneous constants
HTTP_OK = 200
