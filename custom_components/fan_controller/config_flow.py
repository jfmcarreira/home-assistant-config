"""Config flow for the Fan Controller integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import entity_registry as er
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
    CONF_DEHUMIDIFIER_SWITCH,
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
        vol.Optional(CONF_DEHUMIDIFIER_SWITCH): EntitySelector(
            EntitySelectorConfig(domain="switch")
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

    async def _async_validate_entities(
        self, user_input: dict[str, Any]
    ) -> tuple[dict[str, str], str | None]:
        """Validate configured entities and return the stable fan registry ID."""
        errors: dict[str, str] = {}
        entity_registry = er.async_get(self.hass)
        entity_domains = {
            CONF_FAN_ENTITY: "fan",
            CONF_LIGHT_ENTITY: "light",
            CONF_HUMIDITY_SENSOR: "sensor",
            CONF_AVG_HUMIDITY_SENSOR: "sensor",
            CONF_DEHUMIDIFIER_SWITCH: "switch",
        }
        fan_registry_id: str | None = None

        for config_key, domain in entity_domains.items():
            entity_id = user_input.get(config_key)
            if entity_id is None:
                continue
            if not entity_id.startswith(f"{domain}."):
                errors[config_key] = "entity_not_found"
                continue
            registry_entry = entity_registry.async_get(entity_id)
            if registry_entry is None:
                errors[config_key] = "entity_not_found"
                continue
            if config_key == CONF_FAN_ENTITY:
                fan_registry_id = registry_entry.id

        return errors, fan_registry_id

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial config step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors, fan_registry_id = await self._async_validate_entities(user_input)
            if not errors and fan_registry_id is not None:
                if any(
                    entry.data.get(CONF_FAN_ENTITY) == user_input[CONF_FAN_ENTITY]
                    for entry in self._async_current_entries()
                ):
                    errors[CONF_FAN_ENTITY] = "already_configured"
                else:
                    await self.async_set_unique_id(fan_registry_id)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=user_input[CONF_NAME], data=user_input
                    )

        return self.async_show_form(
            step_id="user", data_schema=_CONFIG_SCHEMA, errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Reconfigure the fan and source entities for an existing controller."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            errors, fan_registry_id = await self._async_validate_entities(user_input)
            if not errors and fan_registry_id is not None:
                await self.async_set_unique_id(fan_registry_id)
                for existing_entry in self._async_current_entries():
                    if (
                        existing_entry.entry_id != entry.entry_id
                        and (
                            existing_entry.unique_id == fan_registry_id
                            or existing_entry.data.get(CONF_FAN_ENTITY)
                            == user_input[CONF_FAN_ENTITY]
                        )
                    ):
                        errors[CONF_FAN_ENTITY] = "already_configured"
                        break
                if not errors:
                    return self.async_update_reload_and_abort(
                        entry,
                        title=user_input[CONF_NAME],
                        data=user_input,
                        unique_id=fan_registry_id,
                    )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                _CONFIG_SCHEMA, entry.data
            ),
            errors=errors,
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
