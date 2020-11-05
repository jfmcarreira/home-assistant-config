import hassapi as hass

class VacuumBooleans(hass.Hass):
    def initialize(self):
        self.input_boolean_switches = self.args['input_boolean_switches']
        self.sw_queue = []
        for sw in self.input_boolean_switches:
            self.listen_state(self.input_sw_callback, sw )
            
    def input_sw_callback(self, entity, attribute, old, new, kwargs):
        if old == "on" and new == "off":
            if entity in self.sw_queue:
              self.sw_queue.remove( entity )
        elif old == "off" and new == "on":
            self.sw_queue.append( entity )
            if len( self.sw_queue ) > 5:
                self.turn_off( self.sw_queue.pop(0) )
          
  
