import hassapi as hass

from datetime import datetime

HOUSE_MODE_EVENT_PRESENCE       = 0
HOUSE_MODE_EVENT_LIGHT          = 1
HOUSE_MODE_EVENT_LIGHT_AWAKE    = 2
HOUSE_MODE_EVENT_MOTION         = 3
HOUSE_MODE_EVENT_NO_MOTION      = 4
HOUSE_MODE_EVENT_NO_LIGHT       = 5
HOUSE_MODE_EVENT_TIME           = 6


class ClimateControl():

    def initializeClimateControl(self):
        self.climate_entity = "climate.heating"

    def saveState(self):
        self.heating_state = self.get_state( self.climate_entity )
        self.heating_temperature = self.get_state( self.climate_entity, "temperature" )

        if self.get_state( self.climate_entity, "preset_mode" ) == "none":
            self.normal_temperature = self.heating_temperature

    def updateClimateMode(self, newMode ):
        if newMode == "Off":
            self.modeAway()
        else:
            self.modeHome()

    def modeAway(self):
        self.saveState()
        self.call_service("climate/set_preset_mode", entity_id = self.climate_entity, preset_mode = "away")
        away_temperature = str( int(self.normal_temperature) - 1 )
        self.call_service("climate/set_temperature", entity_id = self.climate_entity, temperature = away_temperature)

    def modeHome(self):
        self.call_service("climate/set_preset_mode", entity_id = self.climate_entity, preset_mode = "none")


class HouseMode(hass.Hass,ClimateControl):

    def initialize(self):

        self.initializeClimateControl()

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
            "binary_sensor.motion_sensor_kitchen",
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
        self.listen_state(self.house_mode_callback, "input_select.house_mode")

        self.timer = None

        self.run_at(self.update_house_mode_at_given_time, "21:30:00")

    def house_mode_callback(self, entity, attribute, old, new, kwargs):
        self.updateClimateMode(new)
        self.house_mode = new

    def is_lights_on(self):
        for entity in self.trackLights:
            if self.get_state( entity ) == "on":
                return True
        return False
    
    def new_house_mode_off(self, trigger ):
        newMode = "Off"
        if self.anyone_home(person=True):
            if self.now_is_between("21:00:00", "09:00:00"):
                newMode = "Night"
            else:
                newMode = "On"
        return newMode

    def new_house_mode_on(self, trigger ):
        newMode = "On"
        if trigger == HOUSE_MODE_EVENT_TIME:
            if self.now_is_between("21:00:00", "09:00:00"):
                newMode = "Night"
        return newMode

    def new_house_mode_night(self, trigger ):
        newMode = "Night"
        if trigger == HOUSE_MODE_EVENT_LIGHT:
            if self.now_is_between("09:00:00", "21:00:00"):
                newMode = "On"
        if trigger == HOUSE_MODE_EVENT_NO_MOTION:
            if self.now_is_between("23:00:00", "09:00:00"):
                newMode = "Sleep"
        return newMode

    def new_house_mode_sleep(self, trigger ):
        newMode = "Sleep"
        if trigger == HOUSE_MODE_EVENT_LIGHT:
            if self.now_is_between("19:00:00", "09:00:00"):
                newMode = "Night"
            else:
                newMode = "On"
        return newMode



    def set_new_house_mode_from_trigger(self, trigger ):

        newMode = self.house_mode
        if self.noone_home(person=True):
            newMode = "Off"
        else:
            if self.house_mode == "Off":
                newMode = self.new_house_mode_off( trigger )
            elif self.house_mode == "On":
                newMode = self.new_house_mode_on( trigger )
            elif self.house_mode == "Night":
                newMode = self.new_house_mode_night( trigger )
            elif self.house_mode == "Sleep":
                newMode = self.new_house_mode_sleep( trigger )
                
        if newMode == "Sleep" and self.is_lights_on():
            newMode = "Night"

        self.select_option("input_select.house_mode", newMode )
        return

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

    def update_house_mode_at_given_time(self, kwargs):
        self.set_new_house_mode_from_trigger( HOUSE_MODE_EVENT_TIME )




# kate: space-indent on; indent-width 4; mixedindent off; indent-mode cstyle;
