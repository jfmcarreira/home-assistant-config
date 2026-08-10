from typing import Final

DOMAIN: Final = "fan_controller"

# Config entry keys (set during config flow)
CONF_NAME: Final = "name"
CONF_FAN_ENTITY: Final = "fan_entity"
CONF_LIGHT_ENTITY: Final = "light_entity"
CONF_HUMIDITY_SENSOR: Final = "humidity_sensor"
CONF_AVG_HUMIDITY_SENSOR: Final = "average_humidity_sensor"
CONF_DEHUMIDIFIER_SWITCH: Final = "dehumidifier_switch"

# Options keys (set in options flow)
CONF_FAN_TIMEOUT: Final = "fan_timeout"
CONF_MAX_TIMEOUT: Final = "max_timeout"
CONF_HUMIDITY_THRESHOLD: Final = "humidity_threshold"

# Default option values
DEFAULT_FAN_TIMEOUT: Final = 300  # seconds
DEFAULT_MAX_TIMEOUT: Final = 20   # minutes
DEFAULT_HUMIDITY_THRESHOLD: Final = 15  # percent
MAX_HUMIDITY_RISE: Final = 10.0  # percentage points
