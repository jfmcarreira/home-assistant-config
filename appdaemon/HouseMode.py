import hassapi as hass

from enum import Enum, auto
from datetime import datetime


class Event(Enum):
    PRESENCE = auto()
    WORKING_LIGHT_OFF = auto()
    LIGHT_ON = auto()
    MOTION = auto()
    NO_MOTION = auto()
    COVERS = auto()
    TIME = auto()
    STATE_TRANSISTION_DELAY = auto()


class HouseMode(hass.Hass):
    def initialize(self):
        self.house_mode = self.get_state("input_select.house_mode")

        self.trackCovers = [
            "cover.master_bedroom",
            "cover.bedroom_ricardo",
            "cover.bedroom_henrique",
        ]

        self.trackWorkingLights = [
            "light.living_room",
            "light.kitchen",
            "light.office",
            "light.bedroom_rc",
            "light.laundry",
            "light.hall_group",
            "light.bathroom_rc",
            "light.main_bathroom",
        ]

        self.trackLights = [
            "light.hallway",
            "light.living_room_group",
            "light.all_bedrooms",
            "light.all_bathrooms",
        ]

        self.trackMotion = [
            "binary_sensor.motion_sensor_stairs",
            "binary_sensor.motion_sensor_office",
            "binary_sensor.motion_sensor_kitchen",
            "binary_sensor.motion_sensor_hallway",
            "binary_sensor.motion_sensor_living_room",
            "binary_sensor.motion_sensor_laundry",
            "binary_sensor.motion_sensor_bathroom_rc",
        ]

        self.trackState = [
            "media_player.living_room_tv",
            "binary_sensor.joao_mac_book_active_home"
        ]

        self.listen_state(self.tracking_callback, "person.joao_carreira")
        self.listen_state(self.tracking_callback, "person.bianca_pires")

        for entity in self.trackLights:
            self.listen_state(self.light_callback, entity)
            self.listen_state(self.light_callback_awake_up,
                                entity, new="on", duration=120)

        for entity in self.trackWorkingLights:
            self.listen_state(self.working_light_callback, entity)
            self.listen_state(self.light_callback_awake_up,
                                entity, new="on", duration=120)

        self.listen_state(self.light_callback_awake_up,
                            "light.master_bedroom", new="on", duration=30)
        self.listen_state(self.light_callback_awake_up,
                            "light.bedroom_ricardo", new="on", duration=2*60)
        self.listen_state(self.light_callback_awake_up,
                            "light.bedroom_henrique", new="on", duration=2*60)
        self.listen_state(self.light_callback_awake_up,
                            "light.living_room_group", new="on", duration=2*60)

        for entity in self.trackMotion:
            self.listen_state(self.motion_callback, entity)

        for entity in self.trackCovers:
            self.listen_state(self.cover_state_callback, entity)

        self.listen_state(self.house_mode_callback, "input_select.house_mode")

        self.state_change_delay_timer = None
        self.lights_motion_timer = None
        self.door_closed_delay = True
        self.door_timer = None
        self.listen_state(self.door_changed_callback, "binary_sensor.kitchen_door")

        self.run_daily(self.update_house_mode_at_given_time, "08:05:00")
        self.run_daily(self.update_house_mode_at_given_time, "09:05:00")
        self.run_daily(self.update_house_mode_at_given_time, "10:05:00")
        self.run_daily(self.update_house_mode_at_given_time, "21:05:00")
        self.run_daily(self.update_house_mode_at_given_time, "21:35:00")
        self.run_daily(self.update_house_mode_at_given_time, "22:05:00")
        self.run_daily(self.update_house_mode_at_given_time, "00:05:00")
        self.run_daily(self.update_house_mode_at_given_time, "01:05:00")

        self.set_new_house_mode_from_trigger(Event.TIME)

    def house_mode_callback(self, entity, attribute, old, new, kwargs):
        self.house_mode = new

    def cancel_tracking_timer(self):
        if self.lights_motion_timer is not None and self.timer_running(self.lights_motion_timer):
            self.cancel_timer(self.lights_motion_timer)
        self.lights_motion_timer = None

    def cancel_door_timer(self):
        if self.door_timer is not None and self.timer_running(self.door_timer):
            self.cancel_timer(self.door_timer)
        self.door_timer = None

    def timer_delay(self):
        if self.now_is_between("01:00:00", "07:00:00"):
            return 2 * 60
        else:
            return 36 * 60

    def is_device_on(self):
        for l in self.trackLights:
            if self.get_state(l) == "on":
                return True
        for entity in self.trackState:
            if self.get_state(entity) == "on":
                return True
        return False

    def is_lights_on(self):
        for entity in self.trackLights:
            if self.get_state(entity) == "on":
                return True
        return False

    def preffered_house_mode(self):
        newMode = "On"
        if self.now_is_between("06:30:00", "07:30:00"):
            newMode = "Evening"
        elif self.now_is_between("19:30:00", "21:30:00"):
            newMode = "Evening"
        elif self.now_is_between("21:30:00", "08:00:00"):
            guest_mode = self.get_state('binary_sensor.house_guest') == "on"
            if guest_mode:
                newMode = "Evening"
            else:
                newMode = "Night"
        return newMode

    def is_sleep_time(self):
        return self.now_is_between("00:00:00", "07:00:00")

    def new_house_mode_from_off(self, trigger):
        newMode = "Off"
        if self.anyone_home(person=True):
            newMode = self.preffered_house_mode()
        return newMode

    def new_house_mode_from_on(self, trigger):
        newMode = "On"
        if trigger == Event.TIME:
            newMode = self.preffered_house_mode()
        return newMode

    def new_house_mode_from_evening(self, trigger):
        newMode = "Evening"
        preffered_mode = self.preffered_house_mode()
        if trigger == Event.WORKING_LIGHT_OFF:
            newMode = preffered_mode
        elif trigger == Event.NO_MOTION:
            newMode = preffered_mode
            if not self.is_device_on() and self.is_sleep_time() and self.door_closed_delay:
                newMode = "Sleep"
        elif trigger == Event.TIME:
            if preffered_mode == "On":
                newMode = "On"
        elif trigger == Event.STATE_TRANSISTION_DELAY:
            if self.now_is_between("06:00:00", "019:00:00"):
                newMode = "On"
        return newMode

    def new_house_mode_from_night(self, trigger):
        newMode = "Night"
        #if trigger == Event.LIGHT_ON:
        #    newMode = self.preffered_house_mode()
        if trigger == Event.NO_MOTION:
            if not self.is_device_on() and self.is_sleep_time() and self.door_closed_delay:
                newMode = "Sleep"
        if trigger == Event.TIME:
            newMode = self.preffered_house_mode()
        return newMode


    def new_house_mode_from_sleep(self, trigger):
        newMode = "Sleep"
        if trigger == Event.LIGHT_ON or trigger == Event.PRESENCE or trigger == Event.COVERS:
            newMode = self.preffered_house_mode()
        return newMode

    def set_new_house_mode_from_trigger(self, trigger):
        oldMode = self.house_mode
        newMode = self.house_mode
        if self.noone_home(person=True):
            newMode = "Off"
        else:
            if self.house_mode == "Off":
                newMode = self.new_house_mode_from_off(trigger)
            elif self.house_mode == "On":
                newMode = self.new_house_mode_from_on(trigger)
            elif self.house_mode == "Evening":
                newMode = self.new_house_mode_from_evening(trigger)
            elif self.house_mode == "Night":
                newMode = self.new_house_mode_from_night(trigger)
            elif self.house_mode == "Sleep":
                newMode = self.new_house_mode_from_sleep(trigger)

        self.select_option("input_select.house_mode", newMode)

        if oldMode != newMode:
            self.state_change_delay_timer = self.run_in(self.timeout_state_changed, 20*60)

    def tracking_callback(self, entity, attribute, old, new, kwargs):
        self.set_new_house_mode_from_trigger(Event.PRESENCE)

    def cover_state_callback(self, entity, attribute, old, new, kwargs):
        if not new == "open":
            return
        self.set_new_house_mode_from_trigger(Event.COVERS)

    def motion_callback(self, entity, attribute, old, new, kwargs):
        haveMotion = False
        for entity in self.trackMotion:
            haveMotion = haveMotion or self.get_state(entity) == "on"
        if not haveMotion:
            self.lights_motion_timer = self.run_in(self.timeout_callback_no_motion, self.timer_delay())
        else:
            self.cancel_tracking_timer()
            self.set_new_house_mode_from_trigger(Event.MOTION)

    def light_callback(self, entity, attribute, old, new, kwargs):
        isLightsOn = False
        for l in self.trackLights:
            isLightsOn = isLightsOn or self.get_state(l) == "on"
        self.cancel_tracking_timer()
        if not isLightsOn:
            self.lights_motion_timer = self.run_in(self.timeout_callback_no_motion, self.timer_delay())

    def working_light_callback(self, entity, attribute, old, new, kwargs):
        isLightsOn = False
        for l in self.trackWorkingLights:
            isLightsOn = isLightsOn or self.get_state(l) == "on"
        self.cancel_tracking_timer()
        if not isLightsOn:
            self.set_new_house_mode_from_trigger(Event.WORKING_LIGHT_OFF)
            self.lights_motion_timer = self.run_in(self.timeout_callback_working_lights_off, self.timer_delay())


    def door_changed_callback(self, entity, attribute, old, new, kwargs):
        isDoorClosed = self.get_state(entity)
        self.door_closed_delay = False
        if isDoorClosed:
            self.door_timer = self.run_in(self.timeout_door_closed, 10*60)
        else:
            self.cancel_door_timer()

    def light_callback_awake_up(self, entity, attribute, old, new, kwargs):
        if new == "on":
            self.set_new_house_mode_from_trigger(Event.LIGHT_ON)

    def timeout_callback_no_motion(self, kwargs):
        self.set_new_house_mode_from_trigger(Event.NO_MOTION)

    def timeout_door_closed(self, kwargs):
        self.door_closed_delay = True

    def timeout_state_changed(self, kwargs):
        self.set_new_house_mode_from_trigger(Event.STATE_TRANSISTION_DELAY)

    def timeout_callback_working_lights_off(self, kwargs):
        self.set_new_house_mode_from_trigger(Event.WORKING_LIGHT_OFF)

    def update_house_mode_at_given_time(self, kwargs):
        self.set_new_house_mode_from_trigger(Event.TIME)
