import hassapi as hass

class ControllingLight:
    def __init__(self, name ):
        self.name = name
        self.master_light = True
        self.turn_on_when_off = False
        
    def init_based_on_dict(self, light_dict ):
        self.master_light = light_dict["master_light"]
        self.turn_on_when_off = light_dict["turn_on_when_off"]
      

class MotionLight(hass.Hass):

    def initialize(self):
              
        self.just_turn_off = False
        
        self.main_light = self.args['main_light']
        self.light = self.args['light']
        self.timeout = self.args['timeout']
        self.short_timeout = 10
        self.motion_sensor = self.args['motion_sensor']
        self.curr_sw = self.args['curr_sw']
        self.turn_on_when_room_off = self.args['turn_on_when_room_off']
        self.lux_sensor = self.args['lux']

        
        
        #if self.manual_trigger is not None:
        #    self.listen_state(self.motion_callback, self.motion_sensor, old = "off", new = "on")
         
        self.other_lights = []
        for light in self.args['other_lights']:
            if type(light) == dict:
                light_class = ControllingLight( light["name"] )
                light_class.init_based_on_dict( light ) 
            else:
                light_class = ControllingLight( light )
            self.other_lights.append( light_class )
              
        self.timer = None
        self.listen_state(self.motion_callback, self.motion_sensor, old = "off", new = "on")
        self.listen_state(self.light_callback, self.light, new = "off")

        for l in self.other_lights:
            self.listen_state(self.other_light_callback, l.name)
        
            
        #self.set_timer(self.timeout)
    
    def should_light_turn_on(self):
      
        turnOn = True
        
        if self.just_turn_off == True:
            self.just_turn_off = False
            return False
        
        # Do not turn on when house is off
        if self.get_state( "input_select.house_mode" ) == "Off":
            return False
        
        # Check if it should turn on while in sleep
        if self.get_state( "input_select.house_mode" ) == "Sleep" and self.args['run_while_in_sleep'] == "off":
            return False        
        
        if not self.get_state( "binary_sensor.notify_home" )  == "on":
          return False
        
        if self.get_state( "input_boolean.automation_sw_all_motion_lights" ) == "off":
          return False
        
        if self.get_state( self.curr_sw ) == "off":
          return False

        
        if not ( self.lux_sensor == "Disabled" ):
            # Check Lux
            turnOn = turnOn and ( float( self.get_state( self.lux_sensor ) ) < 8.0 )              
        else:
            # Sun condition - Below horizon
            turnOn = turnOn and ( int (self.get_state( "sun.sun", "elevation" ) ) < 0 )

        # Only turn on this light if others are off
        for l in self.other_lights:
            if l.master_light:
                turnOn = turnOn and self.get_state( l.name ) == "off"

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
            if self.get_state( "input_select.house_mode" ) == "On":
                self.turn_on(self.main_light)
            elif self.get_state( "input_select.house_mode" ) == "Night":
                self.turn_on(self.light)
            self.set_timer(self.timeout)

    def timeout_callback(self, kwargs):
        self.timer = None
        self.turn_off(self.light)
        self.just_turn_off = True

    def light_callback(self, entity, attribute, old, new, kwargs):
        if self.timer is not None:
            self.cancel_timer(self.timer)
        self.timer = None

    def other_light_callback(self, entity, attribute, old, new, kwargs):
        if new == "on":
            for l in self.other_lights:
                if l.name == entity and l.master_light == True:
                    self.turn_off(self.light)
        else:     
            trigger_on = self.turn_on_when_room_off
            for l in self.other_lights:
                if l.name == entity and l.turn_on_when_off == True:
                    trigger_on = True
                      
            if trigger_on and self.should_light_turn_on():
                self.turn_on(self.light)
                self.set_timer(self.timeout)

