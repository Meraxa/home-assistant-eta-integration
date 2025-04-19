"""Constants for ETA heating technology."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "ETA Heating Technology"
DOMAIN = "eta_heating_technology"
ISSUE_URL = "https://github.com/meraxa/home-assistant_eta_integration/issues"

# Configuration and options
CONF_HOST = "host"
CONF_PORT = "port"

SENSORS_DICT = "SENSORS_DICT"
CHOSEN_ENTITIES = "chosen_entities"

ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
