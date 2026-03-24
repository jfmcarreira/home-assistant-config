from typing import Final

DOMAIN: Final = "fan_controller"

# Config entry keys (set during config flow)
CONF_NAME: Final = "name"
CONF_FAN_ENTITY: Final = "fan_entity"
CONF_LIGHT_ENTITY: Final = "light_entity"
CONF_HUMIDITY_SENSOR: Final = "humidity_sensor"
CONF_AVG_HUMIDITY_SENSOR: Final = "average_humidity_sensor"

# Options keys (set in options flow)
CONF_FAN_TIMEOUT: Final = "fan_timeout"
CONF_MAX_TIMEOUT: Final = "max_timeout"
CONF_HUMIDITY_THRESHOLD: Final = "humidity_threshold"

# Default option values
DEFAULT_FAN_TIMEOUT: Final = 300  # seconds
DEFAULT_MAX_TIMEOUT: Final = 20   # minutes
DEFAULT_HUMIDITY_THRESHOLD: Final = 15  # percent

# State machine state names
STATE_OFF: Final = "off"
STATE_FAN_MANUAL_ON: Final = "fan_manual_on"
STATE_LIGHT_ON: Final = "light_on"
STATE_LIGHT_ON_FAN_ON: Final = "light_on_fan_on"
STATE_LIGHT_ON_FAN_OFF: Final = "light_on_fan_off"
STATE_FAN_ON_HIGH_HUMIDITY: Final = "fan_on_high_humidity"
STATE_FAN_ON_TIMEOUT: Final = "fan_on_timeout"

# Quiet hours (hardcoded — not configurable)
QUIET_HOURS_START: Final = 22  # 22:00
QUIET_HOURS_END: Final = 7    # 07:00
