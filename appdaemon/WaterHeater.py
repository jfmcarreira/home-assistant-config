import hassapi as hass
from statemachine import StateMachine, State

TEMPERATURE_COLD = 40.0
TEMPERATURE_TARGET_ENTITY = "input_number.water_heater_temperature"

SUN_ENTITY = "sun.sun"
OUTSIDE_TEMPERATURE_ENTITY = "weather.home"
WEATHER_ENTITY = "weather.home"
TEMPERATURE_TOP_ENTITY = "sensor.temperature_water_heater_top"
TEMPERATURE_BOTTOM_ENTITY = "sensor.temperature_water_heater_bottom"
SENSOR_SOLAR_PANEL_TREND_ENTITY = "binary_sensor.temperature_solar_panel_trend"
SENSOR_SOLAR_PANNEL_PUMP_ENTITY = "binary_sensor.water_heater_pump_state"
SENSOR_HOUSEOCCUPIED_ENTITY = "binary_sensor.notify_home"

WATER_HEATER_STATE = "input_select.water_heater_state"
WATER_HEATER_ENTITY = "switch.water_heater"

class WaterStateMachine(StateMachine):
    off = State(initial=True)
    idle = State()
    cold = State()
    hot = State()

    state_update = (
        # To Off
        off.to(off, unless=["is_active_time"])
        | idle.to(off, unless=["is_active_time"])
        | hot.to(off, unless=["is_active_time"])
        | cold.to(off, unless=["is_active_time"])

        # To Hot
        | off.to(hot, cond=["is_hot"])
        | idle.to(hot, cond=["is_hot"])
        | hot.to(hot, cond=["is_hot"])
        | cold.to(hot, cond=["is_hot"])

        | off.to(idle, cond=["is_solar_panel_heating"])
        | idle.to(idle, cond=["is_solar_panel_heating"])
        | hot.to(idle, cond=["is_solar_panel_heating"])
        | cold.to(idle, cond=["is_solar_panel_heating"])

        | off.to(idle, cond=["is_positive_weather_forecast"])
        | idle.to(idle, cond=["is_positive_weather_forecast"])
        | cold.to(idle, cond=["is_positive_weather_forecast"])
        | hot.to(idle, cond=["is_positive_weather_forecast"])

        | idle.to(cold)
        | hot.to(cold)

        # To Cold
        | off.to(cold, cond=["is_cold", "is_active_time"])
        | idle.to(cold, cond=["is_cold", "is_active_time"])
        | hot.to(cold, cond=["is_cold", "is_active_time"])
        | cold.to(cold, cond=["is_cold", "is_active_time"])

        # To itself
        | off.to.itself()
        | idle.to.itself()
        | cold.to.itself()
        | hot.to.itself()
    )

class WaterHeater(hass.Hass):

    timer_machine_handle = None

    def initialize(self):

        self.is_heating = False

        self.machine = WaterStateMachine(self)

        self.listen_state(self.state_changed, SUN_ENTITY)
        self.listen_state(self.state_changed, TEMPERATURE_TARGET_ENTITY)
        self.listen_state(self.state_changed, TEMPERATURE_TOP_ENTITY)
        self.listen_state(self.state_changed, TEMPERATURE_BOTTOM_ENTITY)
        self.listen_state(self.state_changed, SENSOR_SOLAR_PANEL_TREND_ENTITY)
        self.listen_state(self.state_changed, SENSOR_SOLAR_PANNEL_PUMP_ENTITY)
        self.listen_state(self.state_changed, SENSOR_HOUSEOCCUPIED_ENTITY)

        self.run_daily(self.time_bases_update, "06:01:00")
        self.run_daily(self.time_bases_update, "07:01:00")
        self.run_daily(self.time_bases_update, "08:01:00")
        self.run_daily(self.time_bases_update, "09:01:00")
        self.run_daily(self.time_bases_update, "10:01:00")
        self.run_daily(self.time_bases_update, "23:01:00")

        self.machine.state_update()
        self.log("State is " + str(self.machine.current_state), level="INFO")

        self.select_option(WATER_HEATER_STATE, self.machine.current_state.id.capitalize())


    def state_changed(self, entity, attribute, old, new, kwargs):
        if entity == SENSOR_SOLAR_PANEL_TREND_ENTITY or entity == SENSOR_SOLAR_PANNEL_PUMP_ENTITY:
            self.timer_machine_handle = self.run_in(self.machine.state_update, 60)
            return

        self.machine.state_update()

    def time_bases_update(self, kwargs):
        self.state_update()

    def is_sun_up(self):
        return self.get_state(SUN_ENTITY) == "above_horizon"

    def is_positive_weather_forecast(self):
        # Clear, night: The sky is clear during the night. clear-night.
        # Cloudy: There are many clouds in the sky. cloudy.
        # Fog: There is a thick mist or fog reducing visibility. fog.
        # Hail: Hailstones are falling. hail.
        # Lightning: Lightning/thunderstorms are occurring. lighting.
        # Lightning, rainy: Lightning/thunderstorm is occurring along with rain. lightning-rainy.
        # Partly cloudy: The sky is partially covered with clouds. partlycloudy.
        # Pouring: It is raining heavily. pouring.
        # Rainy: It is raining. rainy.
        # Snowy: It is snowing. snowy.
        # Snowy, rainy: It is snowing and raining at the same time. snowy-rainy.
        # Sunny: The sky is clear and the sun is shining. sunny.
        # Windy: It is windy. windy.
        # Windy, cloudy: It is windy and cloudy. windy-variant.
        # Exceptional: Exceptional weather conditions are occurring. exceptional.
        weather = self.get_state(WEATHER_ENTITY)

        is_pre_sun_rise =  self.now_is_between("01:00:00", "10:00:00") and not self.is_sun_up()
        if is_pre_sun_rise:
            return True

        if self.now_is_between("00:00:00", "16:00:00"):
            return weather == "partlycloudy" or weather == "sunny" or weather == "windy" or weather == "windy-variant"

        return False

    def is_active_time(self):
        return self.now_is_between("06:00:00", "23:00:00")

    def is_cold(self):
        temperature = float(self.get_state(TEMPERATURE_TOP_ENTITY))
        return temperature < TEMPERATURE_COLD

    def is_hot(self):
        target_temp = float(self.get_state(TEMPERATURE_TARGET_ENTITY))
        temperature = float(self.get_state(TEMPERATURE_TOP_ENTITY))
        if self.is_heating:
            return temperature > target_temp + 2
        return temperature > target_temp

    def is_solar_panel_heating(self):
        result = (
            self.is_sun_up() and
            (self.get_state(SENSOR_SOLAR_PANEL_TREND_ENTITY) == "on"
            or self.get_state(SENSOR_SOLAR_PANNEL_PUMP_ENTITY) == "on")
        )
        return result

    def on_enter_state(self, source, target, event):
        if source is None or source == target:
            return

        self.select_option(WATER_HEATER_STATE, target.id.capitalize())

        if target.id == "cold":
            self.turn_on(WATER_HEATER_ENTITY)
            self.is_heating = True
        else:
            self.turn_off(WATER_HEATER_ENTITY)

        self.log(f"Changing from {source.id} to {target.id} by {event}", level="INFO")

    def on_enter_off(self, source):
        if source is None or source.id == "off":
            return
