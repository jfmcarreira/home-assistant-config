import hassapi as hass

class ControllingLight:
    def __init__(self, name ):
        self.name = name
        self.is_in_room = True
        self.use_to_turn_off = True
        self.use_to_turn_on = False

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



class AutomaticLighting(hass.Hass):

    def initialize(self):

        # Auxiliary variables
        self.just_turn_off = False # temporary disable to toggle lights internally

        self.main_light = self.args['main_light']
        self.presence_light = self.args['presence_light']
        self.current_light = None

        # Listen to the state of the main light in order to turn off presence
        self.listen_state(self.main_light_callback, self.main_light )

        self.timeout = 65
        self.short_timeout = 10

        self.always_running = bool( self.args['run_while_in_sleep'] )

        # Listen for changes in the house mode
        self.house_mode = self.get_state( "input_select.house_mode" )
        self.listen_state(self.house_mode_callback, "input_select.house_mode")

        # Listen for the state of the triggers (motion, door, etc).
        # Should be from off to on
        for trigger in self.args['event_triggers']:
            self.listen_state(self.trigger_callback, trigger, old = "off", new = "on")

        # Light sensor
        try:
            self.lux_sensor = self.args['lux_sensor']
        except KeyError:
            self.lux_sensor = None


        self.room_lights = []
        for light in self.args['room_lights']:
            if type(light) == dict:
                light_class = ControllingLight( light["name"] )
                light_class.init_based_on_dict( light )
            else:
                light_class = ControllingLight( light )
            self.listen_state(self.room_lights_callback, light_class.name)
            self.room_lights.append( light_class )

        self.timer = None


    def turn_on_lights(self):
        light = None
        if self.house_mode == "On":
            light = self.main_light
        elif self.house_mode == "Night":
            light = self.presence_light
        else:
            light = self.presence_light

        if light is not None:
            self.current_light = light
            self.turn_on(light)
            self.listen_state(self.light_callback, light, new = "off", oneshot = True )
            self.set_timer(self.timeout)

    def turn_off_lights(self):
        if self.timer is not None and self.current_light is not None:
            self.turn_off(self.current_light)
        self.timer = None
        self.current_light = None

    def should_light_turn_on(self):

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
            if ( not l.name == self.presence_light ) and l.is_in_room and self.get_state( l.name ) == "on":
                return False

        if self.lux_sensor is not None:
            # Check Lux
            shouldTurnOn = shouldTurnOn and ( float( self.get_state( self.lux_sensor ) ) < 6.0 )
        else:
            # Sun condition - Below horizon
            shouldTurnOn = shouldTurnOn and ( int (self.get_state( "sun.sun", "elevation" ) ) < 0 )

        return shouldTurnOn

    def house_mode_callback(self, entity, attribute, old, new, kwargs):
        if not new == "On":
            self.turn_off_lights()
        self.house_mode = new

    def set_timer(self, timeout):
        if self.timer is not None:
            self.cancel_timer(self.timer)
        self.timer = self.run_in(self.timer_callback, timeout)

    def timer_callback(self, kwargs):
        self.turn_off_lights()

    def trigger_callback(self, entity, attribute, old, new, kwargs):
        if new == "on":
            if self.should_light_turn_on():
                self.turn_on_lights()

    def main_light_callback(self, entity, attribute, old, new, kwargs):
        if new == "on":
            self.turn_off(self.presence_light)

    def light_callback(self, entity, attribute, old, new, kwargs):
        if self.timer is not None:
            self.cancel_timer(self.timer)
        self.timer = None

    def room_lights_callback(self, entity, attribute, old, new, kwargs):
        if not self.current_light == entity:
            if new == "on":
                for l in self.room_lights:
                    if l.name == entity and l.use_to_turn_off == True:
                        self.turn_off_lights()
                        break
            else:
                trigger_on = False
                for l in self.room_lights:
                    if l.name == entity and l.use_to_turn_on == True:
                        trigger_on = True
                        break
                if trigger_on and self.should_light_turn_on():
                    self.turn_on_lights()
