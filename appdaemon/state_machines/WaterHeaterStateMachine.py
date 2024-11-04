from statemachine import StateMachine, State
from statemachine.contrib.diagram import DotGraphMachine

class WaterStateMachine(StateMachine):
    off = State(initial=True)
    idle = State()
    cold = State()
    heating = State()
    hot = State()

    state_update = (
        off.to(off, unless=["is_active_time"])
        | heating.to(off, unless=["is_active_time"])
        | idle.to(off, unless=["is_active_time"])
        | hot.to(off, unless=["is_active_time"])
        | cold.to(off, unless=["is_active_time"])

        | off.to(cold, cond=["is_cold"], unless=["is_active_time"])
        | heating.to(cold, cond=["is_cold"], unless=["is_active_time"])
        | idle.to(cold, cond=["is_cold"], unless=["is_active_time"])
        | hot.to(cold, cond=["is_cold"], unless=["is_active_time"])
        | cold.to(cold, cond=["is_cold"], unless=["is_active_time"])

        |  off.to(hot, cond=["is_hot"])
        | heating.to(hot, cond=["is_hot"])
        | idle.to(hot, cond=["is_hot"])
        | hot.to(hot, cond=["is_hot"])
        | cold.to(hot, cond=["is_hot"])

        | off.to(hot, cond=["is_active_time", "is_hot", "house_occupied"])
        | off.to(cold, cond=["is_active_time","is_cold"])
        | off.to(idle, cond=["is_positive_weather_forecast"])
        | off.to.itself()

        | idle.to(heating, cond=["is_solar_panel_heating"])

        | cold.to(heating, cond=["is_solar_panel_heating"], unless=["is_cold"])
        | cold.to(idle, unless=["house_occupied", "is_cold"])

        | heating.to(cold, unless=["house_occupied", "is_solar_panel_heating", "is_hot"])
        | heating.to(idle, unless=["house_occupied", "is_cold"])

        | hot.to(idle, unless=["house_occupied"])
        | hot.to(heating, cond=["is_solar_panel_heating"], unless=["is_cold", "is_hot"])

        | off.to.itself()
        | idle.to.itself()
        | cold.to.itself()
        | heating.to.itself()
        | hot.to.itself()
    )


class MockApp:

    def is_sun_up(self):
        return False

    def is_positive_weather_forecast(self):
        return False

    def is_active_time(self):
        return False

    def is_cold(self):
        return False

    def is_hot(self):
        return False

    def is_solar_panel_heating(self):
        return False

    def house_occupied(self):
        return False

    def on_enter_state(self, source, target, event):
        return

    def on_enter_off(self, source):
        return


if __name__ == "__main__":
    app = MockApp()
    machine = WaterStateMachine(app)
    #machine._graph()

    graph = DotGraphMachine(machine)
    dot = graph()
    dot.write_png("WaterStateMachine.png")