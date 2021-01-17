import hassapi as hass
import constant

from datetime import datetime

HOUSE_MODE_EVENT_PRESENCE       = 0
HOUSE_MODE_EVENT_LIGHT          = 1
HOUSE_MODE_EVENT_LIGHT_AWAKE    = 2
HOUSE_MODE_EVENT_MOTION         = 3
HOUSE_MODE_EVENT_NO_MOTION      = 4
HOUSE_MODE_EVENT_NO_LIGHT       = 6

class ClimateControl:

    def __init__(self):
        self.entity = "climate.heating"

    def saveState(self):
        self.heating_state = self.get_state( self.entity )
        self.heating_temperature = self.get_state( "climate.heating", "temperature" )

        if self.get_state( self.entity, "preset_mode" ) == "none":
            self.normal_temperature = self.heating_temperature

    def updateMode(self, newMode ):
        if newMode == "Off":
            self.modeAway()
        else:
            self.modeHome()

    def modeAway(self):
        self.saveState()
        self.call_service("climate/set_preset_mode", entity_id = self.entity, preset_mode = "away")
        away_temperature = str( int(self.normal_temperature) - 1 )
        self.call_service("climate/set_temperature", entity_id = self.entity, temperature = away_temperature)

    def modeHome(self):
        self.call_service("climate/set_preset_mode", entity_id = self.entity, preset_mode = "none")


class HouseMode(hass.Hass):

    def initialize(self):

        self.climate = ClimateControl()

        self.trackLights = [
            "light.hallway_group",
            "light.living_room_main",
            "light.living_room_abajur",
            "light.kitchen",
            "light.office",
            "light.master_bedroom_group",
            "light.bedroom_ricardo_group"
            ]

        self.trackMotion = [
            "binary_sensor.motion_sensor_hallway",
            "binary_sensor.motion_sensor_living_room",
            "binary_sensor.motion_sensor_office"
            ]


        self.listen_state(self.tracking_callback, "person.joao")
        self.listen_state(self.tracking_callback, "person.bianca")

        self.listen_state(self.light_callback_awake_up, "light.master_bedroom_group", new = "on", duration = 0 )
        self.listen_state(self.light_callback_awake_up, "light.bedroom_ricardo", new = "on", duration = 0 )

        self.listen_state(self.light_callback_awake_up, "light.kitchen", new = "on", duration = 2*60 )
        self.listen_state(self.light_callback_awake_up, "light.living_room_main", new = "on", duration = 2*60 )
        self.listen_state(self.light_callback_awake_up, "light.office", new = "on", duration = 2*60 )

        for entity in self.trackLights:
            self.listen_state(self.light_callback, entity )

        for entity in self.trackMotion:
            self.listen_state(self.motion_callback, entity )

        self.house_mode = self.get_state( "input_select.house_mode" )
        self.timer = None

    def house_mode_callback(self, entity, attribute, old, new, kwargs):
        self.climate.updateMode(new)
        self.house_mode = new


    def new_house_mode_off(self, trigger ):
        newMode = "Off"
        current_hour = datetime.now().hour
        if self.anyone_home(person=True):
            if current_hour > 22 and current_hour < 8:
                newMode = "Night"
            else:
                newMode = "On"
        return newMode

    def new_house_mode_on(self, trigger ):
        newMode = "On"
        current_hour = datetime.now().hour
        if current_hour > 22 and current_hour < 8:
            newMode = "Night"
        return newMode

    def new_house_mode_night(self, trigger ):
        newMode = "Night"
        current_hour = datetime.now().hour
        if trigger == HOUSE_MODE_EVENT_LIGHT:
            if current_hour > 22 and current_hour < 8:
                newMode = "Night"
            else:
                newMode = "On"
        if trigger == HOUSE_MODE_EVENT_NO_MOTION:
            if current_hour > 23 and current_hour < 8:
                newMode = "Sleep"
        return newMode

    def new_house_mode_sleep(self, trigger ):
        newMode = "Sleep"
        current_hour = datetime.now().hour
        if trigger == HOUSE_MODE_EVENT_LIGHT:
            if current_hour > 22 and current_hour < 8:
                newMode = "Night"
            else:
                newMode = "On"
        return newMode


    def set_new_house_mode_from_trigger(self, trigger ):

        switcher = {
            "Off": self.new_house_mode_off,
            "On": self.new_house_mode_on,
            "Night": self.new_house_mode_night,
            "Sleep": self.new_house_mode_sleep
        }

        if self.noone_home(person=True):
            return "Off"

        new_mode_func = switcher.get(self.house_mode, lambda: "Invalid mode")
        newMode = new_mode_func( trigger )

        self.select_option("input_select.house_mode", newMode )

        return newMode

    def tracking_callback(self, entity, attribute, old, new, kwargs):
        self.set_new_house_mode_from_trigger( HOUSE_MODE_EVENT_PRESENCE )

    def motion_callback(self, entity, attribute, old, new, kwargs):
        haveMotion = False
        for entity in self.trackMotion:
            haveMotion = haveMotion or self.get_state( entity ) == "on"
        if not haveMotion:
            self.timer = self.run_in(self.timeout_callback, 30 * 60 )
        else:
            self.cancel_timer(self.timer)
            self.set_new_house_mode_from_trigger( HOUSE_MODE_EVENT_MOTION )



    def light_callback(self, entity, attribute, old, new, kwargs):
        isLightsOn = False
        for l in self.trackLights:
            isLightsOn = isLightsOn or self.get_state( l ) == "on"
        if not isLightsOn:
            self.timer = self.run_in(self.timeout_callback, 30 * 60 )
        else:
            self.cancel_timer(self.timer)

    def light_callback_awake_up(self, entity, attribute, old, new, kwargs):
        if new == "on":
            self.set_new_house_mode_from_trigger( HOUSE_MODE_EVENT_LIGHT )

    def timeout_callback(self, kwargs):
        self.set_new_house_mode_from_trigger( HOUSE_MODE_EVENT_NO_MOTION )




# kate: space-indent on; indent-width 4; mixedindent off; indent-mode cstyle;
