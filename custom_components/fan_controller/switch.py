"""Switch platform for the Fan Controller integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import FanCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Fan auto mode switch from a config entry."""
    coordinator: FanCoordinator = entry.runtime_data
    async_add_entities([FanAutoModeSwitch(coordinator, entry)])


class FanAutoModeSwitch(SwitchEntity):
    """Switch entity representing the auto mode toggle for a fan."""
    _attr_has_entity_name = True

    def __init__(
        self, coordinator: FanCoordinator, entry: ConfigEntry
    ) -> None:
        self._coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_auto_mode"
        self._attr_name = f"{entry.title} Auto Mode"
        self._attr_icon = "mdi:fan-auto"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Joao Carreira",
        )

    async def async_added_to_hass(self) -> None:
        self._coordinator.register_state_change_callback(self._handle_coordinator_update)

    async def async_will_remove_from_hass(self) -> None:
        self._coordinator.unregister_state_change_callback(self._handle_coordinator_update)

    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool:
        return self._coordinator.auto_mode

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._coordinator.auto_mode = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._coordinator.auto_mode = False

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "Humidity When Light Turned ON": self._coordinator.humidity_light_on,
            "Humidity When Fan Turned ON": self._coordinator.humidity_fan_on,
            "Average Humidity": self._coordinator.average_humidity,
            "Timer Remaining": self._coordinator.timer_remaining,
            "State": self._coordinator.current_state_name,
        }
