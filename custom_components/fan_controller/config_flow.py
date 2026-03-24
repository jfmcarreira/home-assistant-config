"""Config flow for the Fan Controller integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_AVG_HUMIDITY_SENSOR,
    CONF_FAN_ENTITY,
    CONF_FAN_TIMEOUT,
    CONF_HUMIDITY_SENSOR,
    CONF_HUMIDITY_THRESHOLD,
    CONF_LIGHT_ENTITY,
    CONF_MAX_TIMEOUT,
    CONF_NAME,
    DEFAULT_FAN_TIMEOUT,
    DEFAULT_HUMIDITY_THRESHOLD,
    DEFAULT_MAX_TIMEOUT,
    DOMAIN,
)

_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT)
        ),
        vol.Required(CONF_FAN_ENTITY): EntitySelector(
            EntitySelectorConfig(domain="fan")
        ),
        vol.Required(CONF_LIGHT_ENTITY): EntitySelector(
            EntitySelectorConfig(domain="light")
        ),
        vol.Required(CONF_HUMIDITY_SENSOR): EntitySelector(
            EntitySelectorConfig(domain="sensor", device_class="humidity")
        ),
        vol.Required(CONF_AVG_HUMIDITY_SENSOR): EntitySelector(
            EntitySelectorConfig(domain="sensor", device_class="humidity")
        ),
    }
)

_OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_FAN_TIMEOUT, default=DEFAULT_FAN_TIMEOUT): NumberSelector(
            NumberSelectorConfig(
                min=5,
                max=1200,
                step=1,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="s",
            )
        ),
        vol.Required(CONF_MAX_TIMEOUT, default=DEFAULT_MAX_TIMEOUT): NumberSelector(
            NumberSelectorConfig(
                min=5,
                max=120,
                step=1,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="min",
            )
        ),
        vol.Required(
            CONF_HUMIDITY_THRESHOLD, default=DEFAULT_HUMIDITY_THRESHOLD
        ): NumberSelector(
            NumberSelectorConfig(
                min=5,
                max=80,
                step=1,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="%",
            )
        ),
    }
)


class FanConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fan Controller."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial config step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            existing_fan_entities = [
                entry.data.get(CONF_FAN_ENTITY)
                for entry in self._async_current_entries()
            ]
            if user_input[CONF_FAN_ENTITY] in existing_fan_entities:
                errors[CONF_FAN_ENTITY] = "already_configured"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=_CONFIG_SCHEMA, errors=errors
        )

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> "FanOptionsFlow":
        """Return the options flow handler."""
        return FanOptionsFlow(config_entry)


class FanOptionsFlow(OptionsFlow):
    """Handle options flow for Bathroom Fan Controller."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                _OPTIONS_SCHEMA, self._config_entry.options
            ),
        )
