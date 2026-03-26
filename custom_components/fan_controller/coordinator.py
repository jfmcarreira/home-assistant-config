"""Coordinator for the Fan Controller integration."""
from __future__ import annotations

import logging
from typing import Any, Protocol

from statemachine import StateMachine, State
from dataclasses import dataclass, field
from datetime import datetime, time

from homeassistant.core import HomeAssistant, HassJob, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_state_change_event, async_call_later
import homeassistant.util.dt as dt_util

from .const import (
    CONF_AVG_HUMIDITY_SENSOR,
    CONF_FAN_ENTITY,
    CONF_FAN_TIMEOUT,
    CONF_HUMIDITY_SENSOR,
    CONF_HUMIDITY_THRESHOLD,
    CONF_LIGHT_ENTITY,
    CONF_MAX_TIMEOUT,
    DEFAULT_FAN_TIMEOUT,
    DEFAULT_HUMIDITY_THRESHOLD,
    DEFAULT_MAX_TIMEOUT,
    QUIET_HOURS_END,
    QUIET_HOURS_START,
)

_LOGGER = logging.getLogger(__name__)

_QUIET_START = time(QUIET_HOURS_START, 0)
_QUIET_END = time(QUIET_HOURS_END, 0)

class FanController(Protocol):
    """Protocol defining the interface the state machine uses to query/act on state."""

    def is_fan_on(self) -> bool: ...
    def is_light_on(self) -> bool: ...
    def is_high_humidity(self) -> bool: ...
    def is_auto_on_disabled(self) -> bool: ...
    def is_quiet_time(self) -> bool: ...
    def turn_on_fan(self) -> None: ...
    def turn_off_fan(self) -> None: ...
    def set_timer(self, seconds: float) -> None: ...
    def cancel_timer(self) -> None: ...
    def get_fan_timeout_seconds(self) -> float: ...
    def get_max_timeout_seconds(self) -> float: ...
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
        | light_on_fan_on.to(fan_on_timeout, cond=["is_fan_on"], unless=["is_light_on"])
        | light_on_fan_on.to(light_on_fan_off, cond=["is_light_on"], unless=["is_fan_on"])
        | light_on_fan_off.to(light_on_fan_on, cond=["is_light_on", "is_fan_on"])
        | light_on_fan_off.to(light_on, cond=["is_light_on"], unless=["is_fan_on"])
        | light_on_fan_off.to(fan_on_high_humidity, cond=["is_high_humidity"], unless=["is_light_on"])
        | fan_on_high_humidity.to(light_on_fan_on, cond=["is_light_on"])
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
        | fan_on_high_humidity.to(fan_on_timeout, unless=["is_high_humidity"])
        | fan_on_timeout.to(fan_on_high_humidity, cond=["is_high_humidity"])
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
        self.model.turn_off_fan()

    def on_enter_light_on(self, source) -> None:
        if source is None or source.id == "off":
            self.model.record_humidity_light_on()

    def on_enter_fan_manual_on(self) -> None:
        self.model.set_timer(self.model.get_max_timeout_seconds())

    def on_enter_light_on_fan_on(self) -> None:
        self.model.turn_on_fan()

    def on_enter_light_on_fan_off(self) -> None:
        pass

    def on_enter_fan_on_timeout(self) -> None:
        self.model.turn_on_fan()
        self.model.set_timer(self.model.get_fan_timeout_seconds())

    def on_enter_fan_on_high_humidity(self) -> None:
        self.model.turn_on_fan()
        self.model.set_timer(self.model.get_max_timeout_seconds())


class FanCoordinator:
    """Coordinates entity listeners, timers, and state machine for one bathroom fan instance."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._fan_entity: str = entry.data[CONF_FAN_ENTITY]
        self._light_entity: str = entry.data[CONF_LIGHT_ENTITY]
        self._humidity_sensor: str = entry.data[CONF_HUMIDITY_SENSOR]
        self._avg_humidity_sensor: str = entry.data[CONF_AVG_HUMIDITY_SENSOR]

        self._auto_mode: bool = True
        self._humidity_light_on: float | None = None
        self._humidity_fan_on: float | None = None
        self._current_humidity: float | None = None
        self._timer_unsub = None
        self._timer_remaining: float | None = None
        self._timer_started_at: datetime | None = None
        self._timer_duration: float | None = None

        self._state_change_callbacks: list[Any] = []

        self.machine = FanStateMachine(self)

    async def async_setup(self) -> None:
        """Set up entity listeners and reconstruct initial state."""
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
                [self._humidity_sensor],
                self._handle_humidity_state_change,
            )
        )
        self.machine.state_update()

    @callback
    def _handle_fan_light_state_change(self, event) -> None:
        self.hass.async_create_task(self._async_trigger_state_update())

    async def _async_trigger_state_update(self) -> None:
        self.machine.state_update()
        self._notify_state_change()

    @callback
    def _handle_humidity_state_change(self, event) -> None:
        new_state = event.data.get("new_state")
        if new_state is None or new_state.state in ("unavailable", "unknown", ""):
            return
        try:
            self._current_humidity = float(new_state.state)
        except (ValueError, TypeError):
            return
        self.hass.async_create_task(self._async_trigger_humidity_update())

    async def _async_trigger_humidity_update(self) -> None:
        self.machine.humidity_update()
        self._notify_state_change()

    def _notify_state_change(self) -> None:
        for cb in self._state_change_callbacks:
            cb()

    def register_state_change_callback(self, cb) -> None:
        """Register a callback to be called whenever state transitions."""
        self._state_change_callbacks.append(cb)

    def unregister_state_change_callback(self, cb) -> None:
        self._state_change_callbacks.discard(cb) if hasattr(self._state_change_callbacks, 'discard') else None
        if cb in self._state_change_callbacks:
            self._state_change_callbacks.remove(cb)

    @property
    def auto_mode(self) -> bool:
        return self._auto_mode

    @auto_mode.setter
    def auto_mode(self, value: bool) -> None:
        self._auto_mode = value
        self._notify_state_change()

    @property
    def current_state_name(self) -> str:
        return self.machine.current_state.id

    @property
    def humidity_light_on(self) -> float | None:
        return self._humidity_light_on

    @property
    def humidity_fan_on(self) -> float | None:
        return self._humidity_fan_on

    @property
    def average_humidity(self) -> float | None:
        state = self.hass.states.get(self._avg_humidity_sensor)
        if state is None or state.state in ("unavailable", "unknown", ""):
            return None
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return None

    @property
    def timer_remaining(self) -> float | None:
        if self._timer_unsub is None or self._timer_started_at is None:
            return None
        elapsed = (dt_util.now() - self._timer_started_at).total_seconds()
        remaining = (self._timer_duration or 0) - elapsed
        return max(0.0, remaining)

    def is_fan_on(self) -> bool:
        state = self.hass.states.get(self._fan_entity)
        return state is not None and state.state == "on"

    def is_light_on(self) -> bool:
        state = self.hass.states.get(self._light_entity)
        return state is not None and state.state == "on"

    def is_high_humidity(self) -> bool:
        if self._humidity_light_on is None or self._current_humidity is None:
            return False
        avg = self.average_humidity
        if avg is None:
            return False
        threshold_ratio = self.get_humidity_threshold_ratio()
        baseline = min(avg, self._humidity_light_on)
        humidity_threshold = max(100 - baseline, 0.0) * threshold_ratio / 100.0
        humidity_difference = self._current_humidity - baseline
        return humidity_difference > humidity_threshold

    def is_auto_on_disabled(self) -> bool:
        return not self._auto_mode

    def is_quiet_time(self) -> bool:
        now = dt_util.now().time()
        if _QUIET_START > _QUIET_END:
            return now >= _QUIET_START or now < _QUIET_END
        return now < _QUIET_END or now >= _QUIET_START

    def turn_on_fan(self) -> None:
        self.record_humidity_fan_on()
        self.hass.async_create_task(
            self.hass.services.async_call(
                "fan", "turn_on", {"entity_id": self._fan_entity}
            )
        )

    def turn_off_fan(self) -> None:
        self.hass.async_create_task(
            self.hass.services.async_call(
                "fan", "turn_off", {"entity_id": self._fan_entity}
            )
        )

    def set_timer(self, seconds: float) -> None:
        self.cancel_timer()
        self._timer_duration = seconds
        self._timer_started_at = dt_util.now()

        @callback
        def _timer_fired(_now) -> None:
            self._timer_unsub = None
            self._timer_started_at = None
            self._timer_duration = None
            self.hass.async_create_task(self._async_trigger_timer())

        self._timer_unsub = async_call_later(
            self.hass,
            seconds,
            HassJob(_timer_fired, cancel_on_shutdown=True),
        )

    async def _async_trigger_timer(self) -> None:
        self.machine.timer_update()
        self._notify_state_change()

    def cancel_timer(self) -> None:
        if self._timer_unsub is not None:
            self._timer_unsub()
            self._timer_unsub = None
            self._timer_started_at = None
            self._timer_duration = None

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
