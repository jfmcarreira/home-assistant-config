import hassapi as hass

class ControllingLight:
    def __init__(self, name ):
        self.entity = name
        self.manual_on = True
        self.just_turn_on = False
        self.is_in_room = True
        self.use_to_turn_off = True
        self.use_to_turn_on = False
        self.trigger_event = None
        self.is_auxiliary = False
        self.sync_off_with_other = False
        self.timeout_off = 0
        self.timer = None

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
        try:
            self.timeout_off = int( light_dict["timeout_off"] )
        except KeyError:
            pass


class RoomLightControl():

    def init_room_light_control(self):

        self.room_lights = []
        self.room_lights_dict = {}

        self.lights_controller = True
        try:
            self.listen_state(self.lights_controller_callback, self.args['switch'])
            self.lights_controller = self.get_state( self.args['switch'] )
        except KeyError:
            pass

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


    def add_logbook_entry(self, light, action, manual, trigger ):
        log_message = action
        if manual:
            log_message += " manualmente"
        else:
            if trigger is not None:
                try:
                    log_message += " por " + self.get_state( trigger, "friendly_name" )
                except:
                    log_message += " por " + trigger

        try:
            log_name = self.get_state( light.entity, "friendly_name" )
        except:
            log_name = light.entity

        self.call_service("logbook/log", domain = "light", entity_id = light.entity, name = log_name, message = log_message)

    def lights_controller_callback(self, entity, attribute, old, new, kwargs):
        self.lights_controller = ( new == "on" )

    def turn_on_light(self, light, manual = True, trigger = None):
        if not self.get_state( light.entity ) == "on":
            if not manual:
                light.just_turn_on = True
            self.run_in(self.just_turn_on_reset_callback, 3, light = light)
            self.turn_on( light.entity )
            self.add_logbook_entry( light, "ligada", manual, trigger )
            light.manual_on = manual

            if light.timeout_off > 0:
                light.timer_timeout_off = self.run_in(self.light_timer_callback, light.timeout_off, light = light)

    def just_turn_on_reset_callback(self, kwargs):
        light = kwargs["light"]
        light.just_turn_on = False

    def turn_off_light(self, light, trigger = None, manual = False):
        if not self.get_state( light.entity ) == "off":
            self.turn_off( light.entity )
            light.manual_on = False
            self.add_logbook_entry( light, "desligada", manual, trigger )

            if manual and self.lights_controller:
                for l in self.room_lights:
                    if ( not l == light ) and l.sync_off_with_other:
                        self.turn_off_light( l, manual = False, trigger = "sincronização" )

    def light_timer_callback(self, kwargs):
        light = kwargs["light"]
        light.timer_timeout_off = None
        self.turn_off_light(light, trigger = "Temporizador")

    def light_event_callback(self, event_name, data, kwargs):
        light = kwargs["light"]

        # Avoid toggle light when it just turn on
        if light.just_turn_on:
            return

        action = "toggle"
        try:
            action = data["action"]
        except KeyError:
            pass
        if action == "toggle":
            if self.get_state( light.entity ) == "on":
                self.turn_off_light( light, manual = True )
            else:
                self.turn_on_light( light, manual = True)
        elif action == "turn_on":
            self.turn_on_light( light, manual = True)
        elif action == "turn_off":
            self.turn_off_light( light, manual = True)
        else:
            assert()

    def room_lights_callback(self, entity, attribute, old, new, kwargs):
        light = kwargs["light"]
        self.last_trigger = entity
        if new == "on" and not light.is_auxiliary and self.lights_controller:
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

        self.timeout = int( self.args['auto_timeout'] )
        self.no_motion_timeout = int( self.args['no_motion_timeout'] )
        self.short_timeout = 10

        self.number_of_auto_on_events = 0

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
            if type(trigger) == dict:
                trigger_name = trigger["name"]
                trigger_state = trigger["to_state"]
            else:
                trigger_name = trigger
                trigger_state = "on"

            self.listen_state(self.trigger_callback, trigger_name, new = trigger_state )


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

        if self.get_state( "input_boolean.automation_sw_all_motion_lights" ) == "off" or not self.lights_controller:
            return False

        # Only turn on this light if others are off
        for l in self.room_lights:
            if ( not l == self.presence_light ) and l.is_in_room and self.get_state( l.entity ) == "on":
                return False

        if self.lux_sensor is not None:
            # Check Lux
            shouldTurnOn = shouldTurnOn and ( float( self.get_state( self.lux_sensor ) ) < 10.0 )
        else:
            # Sun condition - Below horizon
            shouldTurnOn = shouldTurnOn and ( int (self.get_state( "sun.sun", "elevation" ) ) < 0 )

        if shouldTurnOn:
            light = light = self.presence_light
            if not self.use_always_presence and self.house_mode == "On":
                light = self.main_light

            # Increment counter if timer not running
            if self.timer is None:
                self.number_of_auto_on_events += 1

            self.current_light = light

            self.turn_on_light(light, manual = False, trigger = self.last_trigger )
            self.listen_state(self.light_callback, light.entity, new = "off", oneshot = True )

            self.set_timer( self.number_of_auto_on_events * self.timeout )


    def house_mode_callback(self, entity, attribute, old, new, kwargs):
        if not new == "On":
            self.last_trigger = entity
            self.turn_off_automatic_lights()
            self.number_of_auto_on_events = 0
        self.house_mode = new

    def set_timer(self, timeout):
        if self.timer is not None:
            self.cancel_timer(self.timer)
        self.timer = self.run_in(self.timer_callback, str(timeout))

    def timer_callback(self, kwargs):
        self.last_trigger = "Temporizador"
        self.turn_off_automatic_lights()
        self.timer = None

    def no_motion_timeout_timer_callback(self, kwargs):
        if self.lights_controller:
            for l in self.room_lights:
                if l.is_in_room:
                    self.turn_off_light(l)

    def trigger_callback(self, entity, attribute, old, new, kwargs):
        if self.lights_controller:
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
            self.number_of_auto_on_events = 0
            self.cancel_timer(self.timer)
        self.timer = None

    def room_lights_auto_callback(self, entity, attribute, old, new, kwargs):
        light = kwargs["light"]
        self.last_trigger = entity
        if self.lights_controller:
            if new == "on":
                if light.use_to_turn_off == True and light is not self.current_light:
                    self.turn_off_automatic_lights()
                    self.number_of_auto_on_events = 0
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
