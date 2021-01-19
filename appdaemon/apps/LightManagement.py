import hassapi as hass

class ControllingLight:
    def __init__(self, name ):
        self.entity = name
        self.manual_on = True
        self.is_in_room = True
        self.use_to_turn_off = True
        self.use_to_turn_on = False
        self.trigger_event = None
        self.is_auxiliary = False
        self.sync_off_with_other = False

    def init_based_on_dict(self, light_dict ):
        try:
            self.is_in_room = light_dict["is_in_room"]
        except KeyError:
            pass
        try:
            self.use_to_turn_off = light_dict["use_to_turn_off"]
        except KeyError:
            pass
        try:
            self.use_to_turn_on = light_dict["use_to_turn_on"]
        except KeyError:
            pass
        try:
            self.trigger_event = light_dict["trigger_event"]
        except KeyError:
            pass
        try:
            self.is_auxiliary = light_dict["is_auxiliary"]
        except KeyError:
            pass
        try:
            self.sync_off_with_other = light_dict["sync_off"]
        except KeyError:
            pass


class RoomLightControl():

    def init_room_light_control(self):

        self.room_lights = []
        self.room_lights_dict = {}

        for light_cfg in self.args['room_lights']:

            if type(light_cfg) == dict:
                light = ControllingLight( light_cfg["name"] )
                light.init_based_on_dict( light_cfg )
            else:
                light = ControllingLight( light_cfg )

            self.listen_state(self.room_lights_callback, light.entity, light = light)

            if light.trigger_event:
                self.listen_event(self.light_event_callback, event = light.trigger_event, light = light )

            self.room_lights.append( light )
            self.room_lights_dict[light.entity] = light


    def find_light(self, name):
        for light in self.room_lights:
            if name == light.entity:
                return light
        return None

    def turn_on_light(self, light, manual = True):
        self.turn_on( light.entity )
        self.manual_on = manual

        if manual:
            log_message = "ligada manualmente"
        else:
            log_message = "ligada por " + self.get_state( self.last_trigger, "friendly_name" )

        log_name = self.get_state( light.entity, "friendly_name" )
        self.call_service("logbook/log", domain = "light", entity_id = light.entity, name = log_name, message = log_message)

    def turn_off_light(self, light, trigger = None, manual = False):
        self.turn_off( light.entity )

        if manual:
            for l in self.room_lights:
                if ( not l == light ) and l.sync_off_with_other:
                    self.turn_off_light( l, manual = False, trigger = "sincronização" )

        if trigger is not None:
            log_name = self.get_state( light.entity, "friendly_name" )
            if manual:
                log_message = "desligada manualmente"
            else:
                try:
                    log_message = "desligada por " + self.get_state( trigger, "friendly_name" )
                except:
                    log_message = "desligada por " + trigger
            self.call_service("logbook/log", domain = "light", entity_id = light.entity, name = log_name, message = log_message)

        self.manual_on = False

    def light_event_callback(self, event_name, data, kwargs):
        light = kwargs["light"]
        if self.get_state( light.entity ) == "on":
            self.turn_off_light( light, manual = True )
        else:
            self.turn_on_light( light, manual = True)


    def room_lights_callback(self, entity, attribute, old, new, kwargs):
        light = kwargs["light"]
        self.last_trigger = entity
        if new == "on" and not light.is_auxiliary:
            for light in self.room_lights:
                if light.is_auxiliary:
                    self.turn_off_light( light )

class AutomaticLighting():
    def init_automation_light_control(self):

        # Auxiliary variables
        self.just_turn_off = False # temporary disable to toggle lights internally
        self.last_trigger = None

        self.main_light = self.args['main_light']
        self.presence_light = self.args['presence_light']
        self.current_light = None

        self.use_always_presence = False
        try:
            self.use_always_presence = self.args['use_always_presence']
        except KeyError:
            pass

        self.timeout = self.args['auto_timeout']
        self.no_motion_timeout = self.args['no_motion_timeout']
        self.short_timeout = 10

        self.always_running = bool( self.args['run_while_in_sleep'] )

        # Listen for changes in the house mode
        self.house_mode = self.get_state( "input_select.house_mode" )
        self.listen_state(self.house_mode_callback, "input_select.house_mode")

        for light in self.room_lights:
            if light.use_to_turn_off or light.use_to_turn_on:
                self.listen_state(self.room_lights_auto_callback, light.entity, light = light)

        self.main_light = self.room_lights_dict[self.args['main_light']]
        self.presence_light = self.room_lights_dict[self.args['presence_light']]

        # Listen for the state of the triggers (motion, door, etc).
        # Should be from off to on
        for trigger in self.args['event_triggers']:
            self.listen_state(self.trigger_callback, trigger, old = "off", new = "on")


        # Light sensor
        try:
            self.lux_sensor = self.args['lux_sensor']
        except KeyError:
            self.lux_sensor = None

        self.timer = None
        self.no_motion_timeout_timer = None


    def turn_off_automatic_lights(self):
        if self.timer is not None and self.current_light is not None:
            self.turn_off_light(self.current_light, trigger = self.last_trigger)
        self.timer = None
        self.current_light = None



    def automatic_control_lights(self):

        shouldTurnOn = True

        if self.just_turn_off == True:
            self.just_turn_off = False
            return False

        # Do not turn on when house is off
        if self.house_mode == "Off":
            return False

        # Check if it should turn on while in sleep
        if not self.always_running and self.house_mode == "Sleep":
            return False

        if self.get_state( "input_boolean.automation_sw_all_motion_lights" ) == "off" or  self.get_state( self.args['switch'] ) == "off":
            return False

        # Reset timer
        if self.timer is not None:
            return True

        # Only turn on this light if others are off
        for l in self.room_lights:
            if ( not l == self.presence_light ) and l.is_in_room and self.get_state( l.entity ) == "on":
                return False

        if self.lux_sensor is not None:
            # Check Lux
            shouldTurnOn = shouldTurnOn and ( float( self.get_state( self.lux_sensor ) ) < 6.0 )
        else:
            # Sun condition - Below horizon
            shouldTurnOn = shouldTurnOn and ( int (self.get_state( "sun.sun", "elevation" ) ) < 0 )

        if shouldTurnOn:
            light = None
            if self.use_always_presence:
                light = self.presence_light
            else:
                if self.house_mode == "On":
                    light = self.main_light
                elif self.house_mode == "Night":
                    light = self.presence_light
                else:
                    light = self.presence_light

            if light is not None:
                self.current_light = light
                self.turn_on_light(light, manual = False)
                self.listen_state(self.light_callback, light.entity, new = "off", oneshot = True )
                self.set_timer(self.timeout)

        return shouldTurnOn

    def house_mode_callback(self, entity, attribute, old, new, kwargs):
        if not new == "On":
            self.last_trigger = entity
            self.turn_off_automatic_lights()
        self.house_mode = new

    def set_timer(self, timeout):
        if self.timer is not None:
            self.cancel_timer(self.timer)
        self.timer = self.run_in(self.timer_callback, timeout)

    def timer_callback(self, kwargs):
        self.last_trigger = "Temporizador"
        self.turn_off_automatic_lights()

    def no_motion_timeout_timer_callback(self, kwargs):
        for l in self.room_lights:
            if l.is_in_room:
                self.turn_off_light(l)

    def trigger_callback(self, entity, attribute, old, new, kwargs):
        if new == "on":
            self.last_trigger = entity
            self.automatic_control_lights()


            if self.no_motion_timeout > 0:
                if self.no_motion_timeout_timer is not None:
                    self.cancel_timer(self.timer)
                self.no_motion_timeout_timer = self.run_in(self.no_motion_timeout_timer_callback, self.no_motion_timeout)

    def light_callback(self, entity, attribute, old, new, kwargs):
        self.last_trigger = entity
        if self.timer is not None:
            self.cancel_timer(self.timer)
        self.timer = None

    def room_lights_auto_callback(self, entity, attribute, old, new, kwargs):
        light = kwargs["light"]
        self.last_trigger = entity
        if new == "on":
            if light.use_to_turn_off == True and light is not self.current_light:
                self.turn_off_automatic_lights()
        else:
            if light.use_to_turn_on == True:
                self.automatic_control_lights()


class RoomLightApp(hass.Hass,RoomLightControl):
    def initialize(self):
        self.init_room_light_control()

class AutomaticLightsApp(hass.Hass,RoomLightControl,AutomaticLighting):
    def initialize(self):
        self.init_room_light_control()
        self.init_automation_light_control()