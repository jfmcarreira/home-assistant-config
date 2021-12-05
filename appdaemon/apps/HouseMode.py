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

        self.house_mode = self.get_state( "input_select.house_mode" )

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
            "binary_sensor.motion_sensor_office",
            "binary_sensor.master_bedroom_motion_sensor",
            ]

        self.trackState = [
            "media_player.living_room_tv"
        ]

        self.listen_state(self.tracking_callback, "person.joao")
        self.listen_state(self.tracking_callback, "person.bianca")

        self.listen_state(self.light_callback_awake_up, "light.master_bedroom_group", new = "on", duration = 0 )
        self.listen_state(self.light_callback_awake_up, "light.bedroom_ricardo", new = "on", duration = 2*60 )

        self.listen_state(self.light_callback_awake_up, "light.kitchen", new = "on", duration = 2*60 )
        self.listen_state(self.light_callback_awake_up, "light.living_room_main", new = "on", duration = 2*60 )
        self.listen_state(self.light_callback_awake_up, "light.office", new = "on", duration = 2*60 )

        for entity in self.trackLights:
            self.listen_state(self.light_callback, entity )

        for entity in self.trackMotion:
            self.listen_state(self.motion_callback, entity )

        
        self.listen_state(self.house_mode_callback, "input_select.house_mode")

        self.timer = None
        self.run_daily(self.update_house_mode_at_given_time, "08:05:00")
        self.run_daily(self.update_house_mode_at_given_time, "21:05:00")
        self.run_daily(self.update_house_mode_at_given_time, "22:35:00")
        self.run_daily(self.update_house_mode_at_given_time, "00:05:00")
        self.run_daily(self.update_house_mode_at_given_time, "01:05:00")

        self.set_new_house_mode_from_trigger( HOUSE_MODE_EVENT_TIME )

    def house_mode_callback(self, entity, attribute, old, new, kwargs):
        self.updateClimateMode(new)
        self.house_mode = new

    def cancel_tracking_timer(self):
        if self.timer is not None and self.timer_running(self.timer):
            self.cancel_timer(self.timer)
        self.timer = None

    def timer_delay(self):
        if self.now_is_between("02:00:00", "07:00:00"):
            return 5 * 60
        else:
            return 36 * 60

    def is_device_on(self):
        for l in self.trackLights:
            if self.get_state( l ) == "on":
                return True
        for entity in self.trackState:
            if self.get_state( entity ) == "on":
                return True
        return False

    def is_lights_on(self):
        for entity in self.trackLights:
            if self.get_state( entity ) == "on":
                return True
        return False

    def preffered_house_mode(self):
        newMode = "On"
        if self.now_is_between("07:30:00", "08:30:00"):
          newMode = "Evening"
        elif self.now_is_between("21:00:00", "22:00:00"):
          newMode = "Evening"
        elif self.now_is_between("22:00:00", "08:00:00"):
          newMode = "Night"
        return newMode
    
    def is_sleep_time(self):
      return self.now_is_between("00:00:00", "07:00:00")

    def new_house_mode_from_off(self, trigger ):
        newMode = "Off"
        if self.anyone_home(person=True):
          newMode = self.preffered_house_mode()
        return newMode

    def new_house_mode_from_on(self, trigger ):
        newMode = "On"
        if trigger == HOUSE_MODE_EVENT_TIME:
            newMode = self.preffered_house_mode()
        return newMode

    def new_house_mode_from_evening(self, trigger ):
        newMode = "Evening"
        if trigger == HOUSE_MODE_EVENT_LIGHT:
            newMode = self.preffered_house_mode()
        elif trigger == HOUSE_MODE_EVENT_TIME:
            newMode = self.preffered_house_mode()
        elif trigger == HOUSE_MODE_EVENT_NO_MOTION:
            if not self.is_device_on() and self.is_sleep_time():
                newMode = "Sleep"
        return newMode

    def new_house_mode_from_night(self, trigger ):
        newMode = "Night"
        if trigger == HOUSE_MODE_EVENT_LIGHT:
            newMode = self.preffered_house_mode()
        elif trigger == HOUSE_MODE_EVENT_NO_MOTION:
            if not self.is_device_on() and self.is_sleep_time():
                newMode = "Sleep"
        elif trigger == HOUSE_MODE_EVENT_TIME:
            newMode = self.preffered_house_mode()
        return newMode

    def new_house_mode_from_sleep(self, trigger ):
        newMode = "Sleep"
        if trigger == HOUSE_MODE_EVENT_LIGHT:
            newMode = self.preffered_house_mode()
        return newMode

    def set_new_house_mode_from_trigger(self, trigger ):

        newMode = self.house_mode
        if self.noone_home(person=True):
            newMode = "Off"
        else:
            if self.house_mode == "Off":
                newMode = self.new_house_mode_from_off( trigger )
            elif self.house_mode == "On":
                newMode = self.new_house_mode_from_on( trigger )
            elif self.house_mode == "Evening":
                newMode = self.new_house_mode_from_evening( trigger )
            elif self.house_mode == "Night":
                newMode = self.new_house_mode_from_night( trigger )
            elif self.house_mode == "Sleep":
                newMode = self.new_house_mode_from_sleep( trigger )

        self.select_option("input_select.house_mode", newMode )
        return


    def tracking_callback(self, entity, attribute, old, new, kwargs):
        self.set_new_house_mode_from_trigger( HOUSE_MODE_EVENT_PRESENCE )

    def motion_callback(self, entity, attribute, old, new, kwargs):
        haveMotion = False
        for entity in self.trackMotion:
            haveMotion = haveMotion or self.get_state( entity ) == "on"
        if not haveMotion:
            self.timer = self.run_in(self.timeout_callback, self.timer_delay() )
        else:
            self.cancel_tracking_timer()
            self.set_new_house_mode_from_trigger( HOUSE_MODE_EVENT_MOTION )


    def light_callback(self, entity, attribute, old, new, kwargs):
        isLightsOn = False
        for l in self.trackLights:
            isLightsOn = isLightsOn or self.get_state( l ) == "on"
        self.cancel_tracking_timer()
        if not isLightsOn:
            self.timer = self.run_in(self.timeout_callback, self.timer_delay() )

    def light_callback_awake_up(self, entity, attribute, old, new, kwargs):
        if new == "on":
            self.set_new_house_mode_from_trigger( HOUSE_MODE_EVENT_LIGHT )

    def timeout_callback(self, kwargs):
        self.set_new_house_mode_from_trigger( HOUSE_MODE_EVENT_NO_MOTION )

    def update_house_mode_at_given_time(self, kwargs):
        self.set_new_house_mode_from_trigger( HOUSE_MODE_EVENT_TIME )




# kate: space-indent on; indent-width 4; mixedindent off; indent-mode cstyle;
