import hassapi as hass

import datetime
import time
from enum import Enum, auto
from statemachine import StateMachine, State

MAX_FAN_TIME_ON = 20 * 60

class FanState(Enum):
    FAN_OFF = auto()
    FAN_ON = auto()
    FAN_OFF_LIGHT_ON = auto()
    FAN_ON_LIGHT_OFF = auto()


class BathroomFan(hass.Hass):
    def initialize(self):

        self.fan_state = FanState.FAN_OFF
        self.is_fan_on = False
        self.is_light_on = False
        self.humidity = 0.0
        self.humidity_light_on = 0.0


        self.fan_entity = self.args["fan_entity"]
        self.light_entity = self.args["light_entity"]

        self.listen_state(self.fan_state_changed, self.fan_entity)
        self.listen_state(self.light_state_changed, self.light_entity)
        self.listen_state(self.humidity_state_changed, self.args["humidity_entity"])


    def get_humidity(self):
        return self.get_state(self.args["humidity_entity"])

    def update_fan_state(self):

        if self.is_fan_on:
            self.fan_state = FanState.FAN_ON if self.is_light_on else FanState.FAN_ON_LIGHT_OFF
            return




        self.fan_state = FanState.FAN_OFF_LIGHT_ON if self.is_light_on else FanState.FAN_OFF


    def state_changed_event(self):
        prev_state = self.fan_state
        self.update_fan_state()
        if self.fan_state == prev_state: return
        self.fan_off_timer.cancel()
        self.process_new_state()

    def process_new_state(self):


        match self.fan_state:
            case FAN_OFF:

            case FAN_ON:

            case FAN_OFF_LIGHT_ON:

            case FAN_ON_LIGHT_OFF:
                self.fan_off_timer = self.run_in(self.fan_off_timer_callback, self.args["max_time_on"] * 60)


    def fan_state_changed(self, entity, attribute, old, new, kwargs):
        self.is_fan_on = new == "on"
        self.update_fan_state()

    def light_state_changed(self, entity, attribute, old, new, kwargs):
        self.is_light_on = new == "on"
        if self.is_light_on:
            self.humidity_light_on = self.get_humidity()
        self.update_fan_state()

    def light_state_changed(self, entity, attribute, old, new, kwargs):
        self.humidity = new
        self.update_fan_state()

    def fan_off_timer_callback(self, kwargs):
        self.fan_entity.call_service("turn_off")





