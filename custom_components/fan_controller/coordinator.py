"""Coordinator for the Fan Controller integration."""
from __future__ import annotations

from typing import Any, Protocol

from statemachine import StateMachine, State
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant, HassJob, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_state_change_event, async_call_later
from homeassistant.helpers import entity_registry as er
from homeassistant.exceptions import ConfigEntryError
import homeassistant.util.dt as dt_util

from .const import (
    CONF_AVG_HUMIDITY_SENSOR,
    CONF_DEHUMIDIFIER_SWITCH,
    CONF_FAN_ENTITY,
    CONF_FAN_TIMEOUT,
    CONF_HUMIDITY_SENSOR,
    CONF_HUMIDITY_THRESHOLD,
    CONF_LIGHT_ENTITY,
    CONF_MAX_TIMEOUT,
    DEFAULT_FAN_TIMEOUT,
    DEFAULT_HUMIDITY_THRESHOLD,
    DEFAULT_MAX_TIMEOUT,
    DOMAIN,
    MAX_HUMIDITY_RISE,
)


class FanController(Protocol):
    """Protocol defining the interface the state machine uses to query/act on state."""

    def is_fan_on(self) -> bool: ...
    def is_light_on(self) -> bool: ...
    def is_high_humidity(self) -> bool: ...
    def is_humidity_recovered(self) -> bool: ...
    def is_auto_on_disabled(self) -> bool: ...
    def turn_on_fan(self, reason: str) -> None: ...
    def turn_off_fan(self, reason: str) -> None: ...
    def set_timer(self, seconds: float) -> None: ...
    def cancel_timer(self) -> None: ...
    def get_fan_timeout_seconds(self) -> float: ...
    def get_max_timeout_seconds(self) -> float: ...
    def log_humidity_recovered(self) -> None: ...
    def record_humidity_light_on(self) -> None: ...
    def record_humidity_fan_on(self) -> None: ...


class FanStateMachine(StateMachine):
    off = State(initial=True)
    fan_manual_on = State()
    light_on = State()
    light_on_fan_on = State()
    light_on_fan_off = State()
    fan_on_high_humidity = State()
    fan_on_timeout = State()

    state_update = (
        off.to(light_on_fan_on, cond=["is_fan_on", "is_light_on"])
        | off.to(fan_manual_on, cond=["is_fan_on"])
        | off.to(light_on, cond=["is_light_on"])
        | fan_manual_on.to(light_on_fan_on, cond=["is_light_on", "is_fan_on"])
        | light_on.to(light_on_fan_on, cond=["is_fan_on"])
        | light_on_fan_on.to(
            fan_on_high_humidity,
            cond=["is_fan_on", "is_high_humidity"],
            unless=["is_light_on"],
        )
        | light_on_fan_on.to(
            fan_on_timeout,
            cond=["is_fan_on"],
            unless=["is_light_on", "is_auto_on_disabled"],
        )
        | light_on_fan_on.to(light_on_fan_off, cond=["is_light_on"], unless=["is_fan_on"])
        | light_on_fan_off.to(light_on_fan_on, cond=["is_light_on", "is_fan_on"])
        | light_on_fan_off.to(light_on, cond=["is_light_on"], unless=["is_fan_on"])
        | light_on_fan_off.to(
            fan_on_high_humidity,
            cond=["is_high_humidity"],
            unless=["is_light_on", "is_auto_on_disabled"],
        )
        | fan_on_timeout.to(light_on_fan_on, cond=["is_light_on"])
        | off.from_(light_on, unless=["is_light_on", "is_fan_on"])
        | off.from_(fan_manual_on, unless=["is_fan_on"])
        | off.from_(light_on_fan_on, unless=["is_light_on", "is_fan_on"])
        | off.from_(light_on_fan_off, unless=["is_light_on", "is_fan_on"])
        | off.from_(fan_on_high_humidity, unless=["is_light_on", "is_fan_on"])
        | off.from_(fan_on_timeout, unless=["is_light_on", "is_fan_on"])
        | off.to.itself()
        | fan_manual_on.to.itself()
        | light_on.to.itself()
        | light_on_fan_on.to.itself()
        | light_on_fan_off.to.itself()
        | fan_on_high_humidity.to.itself()
        | fan_on_timeout.to.itself()
    )

    humidity_update = (
        # this will keep fan turning on
        # off.to(fan_on_high_humidity, cond=["is_high_humidity"]) |
        light_on.to(
            light_on_fan_on,
            cond=["is_high_humidity"],
            unless=["is_auto_on_disabled"],
        )
        | fan_on_high_humidity.to(
            fan_on_timeout,
            cond=["is_humidity_recovered"],
            unless=["is_auto_on_disabled"],
        )
        | fan_on_timeout.to(
            fan_on_high_humidity,
            cond=["is_high_humidity"],
            unless=["is_auto_on_disabled"],
        )
        | off.to.itself()
        | fan_manual_on.to.itself()
        | light_on.to.itself()
        | light_on_fan_on.to.itself()
        | light_on_fan_off.to.itself()
        | fan_on_high_humidity.to.itself()
        | fan_on_timeout.to.itself()
    )

    timer_update = (
        fan_manual_on.to(off)
        | fan_on_high_humidity.to(off)
        | fan_on_timeout.to(off)
        | off.to.itself(internal=True)
        | light_on.to.itself()
        | light_on_fan_on.to.itself()
        | light_on_fan_off.to.itself()
        | fan_on_high_humidity.to.itself()
        | fan_on_timeout.to.itself()
    )

    def on_enter_state(self, source, target, event) -> None:
        if source is None or source == target:
            return
        self.model.cancel_timer()

    def on_enter_off(self, source) -> None:
        if source is None or source.id == "off":
            return
        reason = (
            "humidity recovery timeout elapsed"
            if source.id == "fan_on_timeout"
            else "manual runtime limit elapsed"
        )
        self.model.turn_off_fan(reason)

    def on_enter_light_on(self, source) -> None:
        if source is None or source.id == "off":
            self.model.record_humidity_light_on()

    def on_enter_fan_manual_on(self) -> None:
        self.model.set_timer(self.model.get_max_timeout_seconds())

    def on_humidity_update(self, source, target) -> None:
        """Start the fan only for the humidity-driven light-on transition."""
        if source.id == "light_on" and target.id == "light_on_fan_on":
            self.model.turn_on_fan("humidity rose above the start threshold")

    def on_enter_light_on_fan_off(self) -> None:
        pass

    def on_enter_fan_on_timeout(self, source) -> None:
        if source.id == "fan_on_high_humidity":
            self.model.log_humidity_recovered()
        self.model.turn_on_fan("the post-run timeout started")
        self.model.set_timer(self.model.get_fan_timeout_seconds())

    def on_enter_fan_on_high_humidity(self) -> None:
        self.model.turn_on_fan("humidity rose again during the post-run timeout")


class FanCoordinator:
    """Coordinates entity listeners, timers, and state machine for one bathroom fan instance."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._fan_entity: str = entry.data[CONF_FAN_ENTITY]
        self._light_entity: str = entry.data[CONF_LIGHT_ENTITY]
        self._humidity_sensor: str = entry.data[CONF_HUMIDITY_SENSOR]
        self._avg_humidity_sensor: str = entry.data[CONF_AVG_HUMIDITY_SENSOR]
        self._dehumidifier_switch: str | None = entry.data.get(
            CONF_DEHUMIDIFIER_SWITCH
        )

        self._auto_mode: bool = True
        self._humidity_light_on: float | None = None
        self._humidity_fan_on: float | None = None
        self._current_humidity: float | None = None
        self._timer_unsub = None
        self._timer_expires_at: datetime | None = None

        self._state_change_callbacks: list[Any] = []

        self.machine = FanStateMachine(self)

    async def async_setup(self) -> None:
        """Set up entity listeners and reconstruct initial state."""
        self._validate_configured_entities()
        self._current_humidity = self._get_sensor_value(self._humidity_sensor)

        self.entry.async_on_unload(
            async_track_state_change_event(
                self.hass,
                [self._fan_entity, self._light_entity],
                self._handle_fan_light_state_change,
            )
        )
        self.entry.async_on_unload(
            async_track_state_change_event(
                self.hass,
                [self._humidity_sensor, self._avg_humidity_sensor],
                self._handle_humidity_state_change,
            )
        )
        self.entry.async_on_unload(self.cancel_timer)

        if self._control_entities_available():
            self.machine.state_update()
            self.machine.humidity_update()

    def _validate_configured_entities(self) -> None:
        """Fail setup when an entry references missing or invalid entities."""
        entity_registry = er.async_get(self.hass)
        entity_domains = {
            self._fan_entity: "fan",
            self._light_entity: "light",
            self._humidity_sensor: "sensor",
            self._avg_humidity_sensor: "sensor",
        }
        if self._dehumidifier_switch is not None:
            entity_domains[self._dehumidifier_switch] = "switch"

        for entity_id, domain in entity_domains.items():
            if not entity_id.startswith(f"{domain}.") or entity_registry.async_get(
                entity_id
            ) is None:
                raise ConfigEntryError(f"Configured entity no longer exists: {entity_id}")

    def _get_sensor_value(self, entity_id: str) -> float | None:
        """Return a numeric sensor state when it is available."""
        state = self.hass.states.get(entity_id)
        if state is None or state.state in ("unavailable", "unknown", ""):
            return None
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return None

    @callback
    def _handle_fan_light_state_change(self, event) -> None:
        self.hass.async_create_task(self._async_trigger_state_update())

    async def _async_trigger_state_update(self) -> None:
        if not self._control_entities_available():
            self._notify_state_change()
            return
        self.machine.state_update()
        self._notify_state_change()

    @callback
    def _handle_humidity_state_change(self, event) -> None:
        if event.data.get("entity_id") == self._humidity_sensor:
            new_state = event.data.get("new_state")
            if new_state is None or new_state.state in ("unavailable", "unknown", ""):
                return
            try:
                self._current_humidity = float(new_state.state)
            except (ValueError, TypeError):
                return

        self.hass.async_create_task(self._async_trigger_humidity_update())

    async def _async_trigger_humidity_update(self) -> None:
        if not self._control_entities_available():
            self._notify_state_change()
            return
        self.machine.humidity_update()
        self._notify_state_change()

    def _control_entities_available(self) -> bool:
        """Return whether fan and light states are safe to use for control decisions."""
        return (
            self._entity_state_available(self._fan_entity)
            and self._entity_state_available(self._light_entity)
        )

    def _entity_state_available(self, entity_id: str) -> bool:
        state = self.hass.states.get(entity_id)
        return state is not None and state.state not in ("unavailable", "unknown")

    def _notify_state_change(self) -> None:
        for cb in tuple(self._state_change_callbacks):
            cb()

    def register_state_change_callback(self, cb) -> None:
        """Register a callback to be called whenever state transitions."""
        self._state_change_callbacks.append(cb)

    def unregister_state_change_callback(self, cb) -> None:
        """Unregister a state-change callback."""
        if cb in self._state_change_callbacks:
            self._state_change_callbacks.remove(cb)

    @property
    def auto_mode(self) -> bool:
        return self._auto_mode

    async def async_set_auto_mode(self, value: bool) -> None:
        """Set Auto Mode and immediately stop controlled equipment when disabled."""
        if self._auto_mode == value:
            return

        self._auto_mode = value
        if not value:
            self.cancel_timer()
            self.turn_off_fan("Auto Mode was disabled")
        else:
            await self._async_trigger_state_update()
            await self._async_trigger_humidity_update()

        self._notify_state_change()

    @property
    def current_state_name(self) -> str:
        return self.machine.current_state.id

    @property
    def dehumidifier_switch(self) -> str | None:
        return self._dehumidifier_switch

    @property
    def humidity_light_on(self) -> float | None:
        return self._humidity_light_on

    @property
    def humidity_fan_on(self) -> float | None:
        return self._humidity_fan_on

    @property
    def average_humidity(self) -> float | None:
        return self._get_sensor_value(self._avg_humidity_sensor)

    @property
    def humidity_reference(self) -> float | None:
        humidity_light_on = self.humidity_light_on if self.humidity_light_on is not None else 100.0
        humidity_fan_on = self.humidity_fan_on if self.humidity_fan_on is not None else 100.0
        avg = self.average_humidity if self.average_humidity is not None else 100.0
        return max(avg, min(humidity_fan_on, humidity_light_on))

    @property
    def timer_expires_at(self) -> datetime | None:
        return self._timer_expires_at

    @property
    def humidity_start_threshold(self) -> float | None:
        """Return the humidity value that triggers automatic fan operation."""
        if self.humidity_reference is None:
            return None
        threshold_ratio = self.get_humidity_threshold_ratio()
        return self.humidity_reference + min(
            MAX_HUMIDITY_RISE,
            max(100 - self.humidity_reference, 0.0) * threshold_ratio / 100.0,
        )

    def is_fan_on(self) -> bool:
        state = self.hass.states.get(self._fan_entity)
        return state is not None and state.state == "on"

    def is_light_on(self) -> bool:
        state = self.hass.states.get(self._light_entity)
        return state is not None and state.state == "on"

    def is_high_humidity(self) -> bool:
        if self._humidity_light_on is None or self._current_humidity is None:
            return False
        humidity_start_threshold = self.humidity_start_threshold
        return (
            humidity_start_threshold is not None
            and self._current_humidity > humidity_start_threshold
        )

    def is_humidity_recovered(self) -> bool:
        """Return whether humidity has returned to the light-on baseline."""
        return (
            self._humidity_light_on is not None
            and self._current_humidity is not None
            and self._current_humidity <= self._humidity_light_on
        )

    def is_auto_on_disabled(self) -> bool:
        return not self._auto_mode

    def turn_on_fan(self, reason: str) -> None:
        self.turn_on_dehumidifier()
        self.record_humidity_fan_on()
        if self.is_fan_on():
            return
        self._log_fan_decision(f"Fan on requested: {reason}.")
        self.hass.async_create_task(
            self.hass.services.async_call(
                "fan", "turn_on", {"entity_id": self._fan_entity}
            )
        )

    def turn_off_fan(self, reason: str) -> None:
        self.turn_off_dehumidifier()
        if not self.is_fan_on():
            return
        self._log_fan_decision(f"Fan off requested: {reason}.")
        self.hass.async_create_task(
            self.hass.services.async_call(
                "fan", "turn_off", {"entity_id": self._fan_entity}
            )
        )

    def turn_on_dehumidifier(self) -> None:
        if self._dehumidifier_switch is None:
            return
        self.hass.async_create_task(
            self.hass.services.async_call(
                "switch", "turn_on", {"entity_id": self._dehumidifier_switch}
            )
        )

    def turn_off_dehumidifier(self) -> None:
        if self._dehumidifier_switch is None:
            return
        self.hass.async_create_task(
            self.hass.services.async_call(
                "switch", "turn_off", {"entity_id": self._dehumidifier_switch}
            )
        )

    def log_humidity_recovered(self) -> None:
        """Log that humidity has returned to the light-on baseline."""
        self._log_fan_decision("Humidity recovered; post-run timeout started.")

    def _log_fan_decision(self, message: str) -> None:
        """Write a controller decision to Home Assistant's Activity log."""
        if not self.hass.services.has_service("logbook", "log"):
            return
        self.hass.async_create_task(
            self.hass.services.async_call(
                "logbook",
                "log",
                {
                    "name": self.entry.title,
                    "message": (
                        f"{message} Current humidity: "
                        f"{self._format_humidity(self._current_humidity)}. "
                        f"Light-on baseline: "
                        f"{self._format_humidity(self._humidity_light_on)}. "
                        f"Reference: {self._format_humidity(self.humidity_reference)}. "
                        f"Start threshold: "
                        f"{self._format_humidity(self.humidity_start_threshold)}."
                    ),
                    "entity_id": self._fan_entity,
                    "domain": "fan",
                },
            )
        )

    @staticmethod
    def _format_humidity(value: float | None) -> str:
        """Format a humidity value for a human-readable Activity entry."""
        return "unknown" if value is None else f"{value:.1f}%"

    def set_timer(self, seconds: float) -> None:
        self.cancel_timer()
        self._timer_expires_at = dt_util.utcnow() + timedelta(seconds=seconds)
        self._schedule_timer(seconds)

    def _schedule_timer(self, seconds: float) -> None:
        @callback
        def _timer_fired(_now) -> None:
            self._timer_unsub = None
            self._timer_expires_at = None
            self.hass.async_create_task(self._async_handle_timer_expiry())

        self._timer_unsub = async_call_later(
            self.hass,
            seconds,
            HassJob(_timer_fired, cancel_on_shutdown=True),
        )

    async def _async_handle_timer_expiry(self) -> None:
        self.machine.timer_update()
        self._notify_state_change()

    def cancel_timer(self) -> None:
        if self._timer_unsub is not None:
            self._timer_unsub()
            self._timer_unsub = None
        self._timer_expires_at = None

    def get_fan_timeout_seconds(self) -> float:
        return float(
            self.entry.options.get(CONF_FAN_TIMEOUT, DEFAULT_FAN_TIMEOUT)
        )

    def get_max_timeout_seconds(self) -> float:
        return float(
            self.entry.options.get(CONF_MAX_TIMEOUT, DEFAULT_MAX_TIMEOUT)
        ) * 60.0

    def get_humidity_threshold_ratio(self) -> float:
        return float(
            self.entry.options.get(CONF_HUMIDITY_THRESHOLD, DEFAULT_HUMIDITY_THRESHOLD)
        )

    def record_humidity_light_on(self) -> None:
        state = self.hass.states.get(self._humidity_sensor)
        if state is not None and state.state not in ("unavailable", "unknown", ""):
            try:
                self._humidity_light_on = float(state.state)
            except (ValueError, TypeError):
                pass

    def record_humidity_fan_on(self) -> None:
        state = self.hass.states.get(self._humidity_sensor)
        if state is not None and state.state not in ("unavailable", "unknown", ""):
            try:
                self._humidity_fan_on = float(state.state)
            except (ValueError, TypeError):
                pass
