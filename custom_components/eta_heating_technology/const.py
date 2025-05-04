"""Constants for ETA heating technology."""

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
    "Ein": True,
    "Aus": False,
    "Eingeschaltet": True,
    "Ausgeschaltet": False,
}
