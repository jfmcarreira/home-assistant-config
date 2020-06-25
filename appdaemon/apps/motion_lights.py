import hassapi as hass

class MotionLight(hass.Hass):

    def initialize(self):
        self.motion_sensor = self.args['motion_sensor']
        self.other_lights = self.args['other_lights']
        self.light = self.args['light']
        self.timeout = self.args['timeout']
        self.short_timeout = 10

        self.timer = None
        self.listen_state(self.motion_callback, self.motion_sensor, new = "on")
        self.listen_state(self.light_callback, self.light, new = "off")

        for l in self.other_lights:
            self.listen_state(self.other_light_callback, l)
            
        self.set_timer(self.timeout)
    
    def should_light_turn_on(self):
      
        turnOn = True

        # Sun condition - Below horizon
        turnOn = turnOn and ( self.get_state( "sun.sun", "elevation" ) < 0 )

        # Only turn on this light if others are off
        for l in self.other_lights:
           turnOn = turnOn and self.get_state( l ) == "off"

        # Only start this is the light is off
        turnOn = turnOn and self.get_state( self.light ) == "off"
        
        if self.timer is not None:
            turnOn = turnOn or True
            
        return turnOn
      
    def set_timer(self, timeout):
        if self.timer is not None:
            self.cancel_timer(self.timer)
        self.timer = self.run_in(self.timeout_callback, timeout)

    def motion_callback(self, entity, attribute, old, new, kwargs):
       
        if self.should_light_turn_on():
            self.turn_on(self.light)
            self.set_timer(self.timeout)

    def timeout_callback(self, kwargs):
        self.timer = None
        self.turn_off(self.light)

    def light_callback(self, entity, attribute, old, new, kwargs):
        if self.timer is not None:
            self.cancel_timer(self.timer)
        self.timer = None

    def other_light_callback(self, entity, attribute, old, new, kwargs):
        if new == "off":
            if self.should_light_turn_on():
                self.turn_on(self.light)
                self.set_timer(self.short_timeout)
        else:
            self.turn_off(self.light)
