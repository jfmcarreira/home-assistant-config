"""Switch platform for the Fan Controller integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
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
    _attr_entity_category = EntityCategory.CONFIG
    _attr_should_poll = False

    def __init__(
        self, coordinator: FanCoordinator, entry: ConfigEntry
    ) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_auto_mode"
        self._attr_translation_key = "auto_mode"
        self._attr_icon = "mdi:fan-auto"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Joao Carreira",
        )

    async def async_added_to_hass(self) -> None:
        """Register for coordinator updates."""
        await super().async_added_to_hass()
        self._coordinator.register_state_change_callback(self._handle_coordinator_update)

    async def async_will_remove_from_hass(self) -> None:
        self._coordinator.unregister_state_change_callback(self._handle_coordinator_update)

    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool:
        return self._coordinator.auto_mode

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._coordinator.async_set_auto_mode(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._coordinator.async_set_auto_mode(False)

    @property
    def extra_state_attributes(self) -> dict[str, float | str | None]:
        return {
            "humidity_when_light_turned_on": self._coordinator.humidity_light_on,
            "humidity_when_fan_turned_on": self._coordinator.humidity_fan_on,
            "average_humidity": self._coordinator.average_humidity,
            "humidity_reference": self._coordinator.humidity_reference,
            "timer_expires_at": (
                self._coordinator.timer_expires_at.isoformat()
                if self._coordinator.timer_expires_at is not None
                else None
            ),
            "controller_state": self._coordinator.current_state_name,
        }
