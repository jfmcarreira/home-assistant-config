import hassapi as hass
from statemachine import StateMachine, State

MAX_FAN_TIME_ON = 20 * 60

TIMEOUT_ENTITY = "input_number.bathroom_fan_timeout"
MAX_TIMEOUT_ENTITY = "input_number.bathroom_fan_max_timeout"
THRESHOLD_HUMIDITY = "input_number.bathroom_fan_humidity_threshold"

AUTO_TIME_BEGIN = "07:00:00"
AUTO_TIME_END = "22:00:00"

class MovingAverage:
    average = 0.0
    points = []
    size = 0

    def __init__(self, size, value):
        for i in range(size):
            self.points.append(value/size)
        self.average = value
        self.size = size

    def add_point(self, value):
        new_point = value / self.size
        value_to_remove = self.points.pop(0)
        self.points.append(new_point)
        self.average = self.average - value_to_remove + new_point


    def get(self):
        return self.average


class BathroomFanMachine(StateMachine):
    off = State(initial=True)
    fan_manual_on = State()
    light_on = State()
    light_on_fan_on = State()
    fan_on_high_humidity = State()
    fan_on_timeout = State()

    state_update = (
        off.to(light_on_fan_on, cond=["is_fan_on", "is_light_on"])
        | off.to(fan_manual_on, cond=["is_fan_on"])
        | off.to(light_on, cond=["is_light_on"])
        | fan_manual_on.to(light_on_fan_on, cond=["is_light_on", "is_fan_on"])
        | light_on.to(light_on_fan_on, cond=["is_fan_on"])
        | light_on_fan_on.to(
            fan_on_high_humidity,
            cond=["is_fan_on", "is_high_humidity"],
            unless=["is_light_on"],
        )
        | light_on_fan_on.to(fan_on_timeout, cond=["is_fan_on"], unless=["is_light_on"])
        | light_on_fan_on.to(light_on, cond=["is_light_on"], unless=["is_fan_on"])
        | fan_on_high_humidity.to(light_on_fan_on, cond=["is_light_on"])
        | fan_on_timeout.to(light_on_fan_on, cond=["is_light_on"])
        | off.from_(light_on, unless=["is_light_on", "is_fan_on"])
        | off.from_(fan_manual_on, unless=["is_fan_on"])
        | off.from_(light_on_fan_on, unless=["is_light_on", "is_fan_on"])
        | off.from_(fan_on_high_humidity, unless=["is_light_on", "is_fan_on"])
        | off.from_(fan_on_timeout, unless=["is_light_on", "is_fan_on"])
        | off.to.itself()
        | fan_manual_on.to.itself()
        | light_on.to.itself()
        | light_on_fan_on.to.itself()
        | fan_on_high_humidity.to.itself()
        | fan_on_timeout.to.itself()
    )

    humidity_update = (
        # this will keep fan turning on
        # off.to(fan_on_high_humidity, cond=["is_high_humidity"]) |
        light_on.to(
            light_on_fan_on, cond=["is_high_humidity"], unless=["is_auto_on_disabled"]
        )
        | fan_on_high_humidity.to(fan_on_timeout, unless=["is_high_humidity"])
        | fan_on_timeout.to(fan_on_high_humidity, cond=["is_high_humidity"])
        | off.to.itself()
        | fan_manual_on.to.itself()
        | light_on.to.itself()
        | light_on_fan_on.to.itself()
        | fan_on_high_humidity.to.itself()
        | fan_on_timeout.to.itself()
    )

    timer_update = (
        fan_manual_on.to(off)
        | fan_on_high_humidity.to(off)
        | fan_on_timeout.to(off)
        | off.to.itself(internal=True)
        | light_on.to.itself()
        | light_on_fan_on.to.itself()
        | fan_on_high_humidity.to.itself()
        | fan_on_timeout.to.itself()
    )


class BathroomFan(hass.Hass):
    timer_machine_handle = None

    def initialize(self):
        self.fan_entity = self.args["fan_entity"]
        self.light_entity = self.args["light_entity"]


        self.humidity_light_on = self.get_average_humidity()
        self.current_humidity = self.get_humidity()
        self.average_humidity = MovingAverage(
            360, float(self.get_state(self.args["average_humidity_entity"]))
        )

        self.humidity_when_light_turned_on = None
        self.timer_machine_handle = None

        self.machine = BathroomFanMachine(self)
        self.machine.state_update()

        self.listen_state(self.state_changed, self.fan_entity)
        self.listen_state(self.state_changed, self.light_entity)
        self.listen_state(self.humidity_state_changed, self.args["humidity_entity"])

        self.run_every(self.humidity_update_timer, "now", interval=30)

        self.log("State is " + str(self.machine.current_state), level="INFO")

    ######## Getters
    def get_fan_timeout(self):
        return float(self.get_state(TIMEOUT_ENTITY))

    def get_fan_max_timeout(self):
        return float(self.get_state(MAX_TIMEOUT_ENTITY)) * 60.0

    def get_humidity_threshold_ratio(self):
        return float(self.get_state(THRESHOLD_HUMIDITY))

    def get_humidity(self):
        return float(self.get_state(self.args["humidity_entity"]))

    def get_average_humidity(self):
        return float(self.get_state(self.args["average_humidity_entity"]))

    def is_auto_on_disabled(self):
        return not (self.get_state(self.args["toggle"]) == "on")

    def is_quiet_time(self):
        return not self.now_is_between(AUTO_TIME_BEGIN, AUTO_TIME_END)

    def is_light_on(self):
        return self.get_state(self.light_entity) == "on"


    def is_fan_on(self):
        return self.get_state(self.fan_entity) == "on"

    def is_high_humidity(self):
        threshold_ratio = self.get_humidity_threshold_ratio()
        humidity = min(self.get_average_humidity(), self.humidity_light_on)
        humidity_threshold = max(100 - humidity, 0.0) * self.get_humidity_threshold_ratio()
        humidity_difference = self.current_humidity - humidity
        is_high_humidity = humidity_difference > humidity_threshold
        self.log("Min humidity is " + str(humidity), level="INFO")
        self.log("High humidity is " + str(is_high_humidity), level="INFO")
        return is_high_humidity

    ######## State Change Callbacks
    def state_changed(self, entity, attribute, old, new, kwargs):
        self.machine.state_update()

    def humidity_state_changed(self, entity, attribute, old, new, kwargs):
        self.current_humidity = float(new)
        self.machine.humidity_update()

    def humidity_update_timer(self, kwargs):
        if self.machine.current_state.id == "off":
            self.average_humidity.add_point(self.current_humidity)

    def state_update_timer(self, kwargs):
        self.machine.timer_update()

    ######## State Machine
    def on_enter_state(self, source, target, event):
        if source is None or source == target:
            return
        self.log(f"Changing from {source.id} to {target.id} by {event}", level="INFO")
        if source == target:
            return
        if self.timer_running(self.timer_machine_handle):
            self.cancel_timer(self.timer_machine_handle)

    def on_enter_off(self, source):
        if source is None or source.id == "off":
            return
        self.turn_off(self.fan_entity)

    def on_enter_light_on(self, source):
        if source is None or source.id == "off":
            self.humidity_light_on = self.current_humidity

    def on_enter_fan_manual_on(self):
        self.timer_machine_handle = self.run_in(
            self.state_update_timer, self.get_fan_max_timeout()
        )

    def on_enter_light_on_fan_on(self):
        self.turn_on(self.fan_entity)
        return

    def on_enter_fan_on_timeout(self):
        self.turn_on(self.fan_entity)
        self.timer_machine_handle = self.run_in(
            self.state_update_timer, self.get_fan_timeout()
        )

    def on_enter_fan_on_high_humidity(self):
        self.turn_on(self.fan_entity)
        self.timer_machine_handle = self.run_in(
            self.state_update_timer, self.get_fan_max_timeout()
        )
