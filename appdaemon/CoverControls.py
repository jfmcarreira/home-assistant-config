import hassapi as hass

import datetime
import time
from enum import Enum, auto

class CoverControls(hass.Hass):
    def initialize(self):

        self.sunrise_processed = False
        self.sunset_processed = False
        self.sun_south_position_processed = False
        self.sun_west_position_processed = False

        self.cover_name = self.args["cover_name"]
        self.cover_orientation = self.args["cover_orientation"]

        self.run_daily(self.reset_daily_state, "04:00:00")
        self.run_every(self.callback_time, "now", datetime.timedelta(minutes = 15).total_seconds())
        # self.run_at_sunrise(self.callback_sunrise, offset = datetime.timedelta(minutes = 15).total_seconds())
        # self.run_at_sunset(self.callback_sunset)

    def is_house_occupied(self) -> bool:
        return self.get_state("binary_sensor.notify_home")

    def get_cover_entity(self):
        return self.get_entity("cover." +  self.cover_name)

    def get_action_master_control_switch(self, action_name) -> bool:
        return self.get_state("input_boolean.cover_master_control_" + action_name)

    def get_action_control_switch(self, action_name) -> bool:
        return self.get_state("input_boolean.cover_control_" + action_name +  "_" + self.cover_name)

    def get_sun_elevation(self) -> float:
        return self.get_state("sun.sun", attribute="elevation")

    def get_sun_azimuth(self) -> float:
        return self.get_state("sun.sun", attribute="azimuth")

    def get_outside_temperature(self) -> float:
        return self.get_state("sensor.temperature_outside")

    def open_cover(self):
        self.get_cover_entity().call_service("open_cover")

    def close_cover(self):
        self.get_cover_entity().call_service("close_cover")

    def reset_daily_state(self, kwargs):
        self.sunrise_processed = False
        self.sunset_processed = False
        self.sun_south_position_processed = False
        self.sun_west_position_processed = False

    def callback_time(self, kwargs):
        sun_elevation = self.get_sun_elevation()
        # if sun_elevation > 0:
        #     self.action_sunrise()
        # else:
        #     self.action_sunset()

        self.action_sun_south()
        self.action_sun_west()

    # def callback_sunrise(self, kwargs):
    #     self.action_sunrise()

    # def callback_sunset(self, kwargs):
    #     self.action_sunset()

    # def action_sunrise(self):
    #     if self.sunrise_processed: return

    #     if not self.get_action_master_control_switch("open_sunsise"): return

    #     if not self.now_is_between("08:00:00", "12:00:00"): return
    #     if self.get_sun_elevation() < 0: return

    #     self.sunrise_processed = True

    #     if not self.get_action_control_switch("open_sunrise"): return

    #     self.open_cover()

    # def action_sunset(self):
    #     if self.sunset_processed: return

    #     if not self.get_action_master_control_switch("close_sunset"): return

    #     if self.get_sun_elevation() > 0: return
    #     if self.is_house_occupied(): return

    #     self.sunset_processed = True

    #     if not self.get_action_control_switch("close_sunset"): return

    #     self.close_cover()

    def action_sun_south(self):
        if self.sun_south_position_processed: return

        if not self.get_action_master_control_switch("close_south"): return

        if not self.now_is_between("10:00:00", "16:00:00"): return
        if self.get_sun_elevation() < 0: return
        if self.get_sun_azimuth() > 180: return
        if self.get_sun_azimuth() < 30: return
        if self.is_house_occupied(): return
        if self.get_outside_temperature() < 25: return

        self.sun_south_position_processed = True

        if not self.cover_orientation == "south": return

        self.close_cover()

    def action_sun_west(self):
        if self.sun_west_position_processed: return

        if not self.get_action_master_control_switch("close_west"): return

        if self.get_sun_elevation() < 0: return
        if self.get_sun_azimuth() < 180: return
        if self.get_sun_azimuth() > 270: return
        if self.is_house_occupied(): return
        if self.get_outside_temperature() < 25: return

        self.sun_west_position_processed = True

        if not self.cover_orientation == "west": return

        self.close_cover()






