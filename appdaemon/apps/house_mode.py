import hassapi as hass

from datetime import datetime

class HouseMode(hass.Hass):

    def initialize(self):
              
        self.trackLights = [
            "light.hallway_group", 
            "light.living_room", 
            "light.kitchen",
            "light.office",
            "light.master_bedroom_group"
            ]
        
        self.trackMotion = [
            "binary_sensor.motion_sensor_hallway", 
            "binary_sensor.motion_sensor_living_room", 
            "binary_sensor.motion_sensor_office"
            ]
        
        
        self.listen_state(self.notify_home_callback, "binary_sensor.notify_home")
        
        self.listen_state(self.light_callback_awake_up, "light.master_bedroom_group", new = "on", duration = 2*60 )
        self.listen_state(self.light_callback_awake_up, "light.kitchen", new = "on", duration = 10*60 )
        self.listen_state(self.light_callback_awake_up, "light.living_room_main", new = "on", duration = 2*60 )
        self.listen_state(self.light_callback_awake_up, "light.bedroom_ricardo", new = "on", duration = 2*60 )
        self.listen_state(self.light_callback_awake_up, "light.office", new = "on", duration = 2*60 )
        
        for entity in self.trackLights:
            self.listen_state(self.light_callback, entity )
        
        for entity in self.trackMotion:
            self.listen_state(self.motion_callback, entity )

        self.select_option("input_select.house_mode", self.new_house_mode() )
        
            
    def new_house_mode(self):
      
        isOccupied = bool( self.get_state( "binary_sensor.notify_home" ) )
      
        if not isOccupied:
            return "Off"
            
        newMode = "On"

        current_hour = datetime.now().hour
        if current_hour > 22 and current_hour < 8:
            newMode = "Night"
            
        
        return newMode
      
    
    def notify_home_callback(self, entity, attribute, old, new, kwargs):
        if new == "on":
            self.select_option("input_select.house_mode", self.new_house_mode() )
        else:
            self.select_option("input_select.house_mode", "Off")
            
    
    def motion_callback(self, entity, attribute, old, new, kwargs):
        haveMotion = False
        for entity in self.trackMotion:
            haveMotion = haveMotion or self.get_state( entity ) == "on"
        if not haveMotion:
            self.timer = self.run_in(self.timeout_callback, 1800)
        else:
            self.cancel_timer(self.timer)
           
            
    def light_callback(self, entity, attribute, old, new, kwargs):
        isLightsOn = False
        for l in self.trackLights:
            isLightsOn = isLightsOn or self.get_state( l ) == "on"
        if not isLightsOn:
            self.timer = self.run_in(self.timeout_callback, 1800)
        else:
            self.cancel_timer(self.timer)
       
    def light_callback_awake_up(self, entity, attribute, old, new, kwargs):
        
        currentMode = self.get_state( "input_select.house_mode" )
        if new == "on" and currentMode == "Sleep":
            self.select_option("input_select.house_mode", self.new_house_mode() )
            
    def timeout_callback(self, kwargs):
        current_hour = datetime.now().hour
        if current_hour > 22 and current_hour < 8:
            self.select_option("input_select.house_mode", "Sleep")



# kate: space-indent on; indent-width 4; mixedindent off; indent-mode cstyle;
