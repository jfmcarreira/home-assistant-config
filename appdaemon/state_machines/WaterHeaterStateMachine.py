from statemachine import StateMachine, State

class WaterStateMachine(StateMachine):
    off = State(initial=True)
    idle = State()
    cold = State()
    heating = State()
    hot = State()

    time_update = (
        off.to(hot, cond=["is_active_time", "is_hot", "house_occupied"])
        | off.to(heating, cond=["is_solar_panel_heating", "house_occupied"])
        | off.to(cold, cond=["is_active_time", "is_cold"])
        | off.to(idle, unless=["house_occupied"])
        | off.to(cold, cond=["is_active_time", "house_occupied"], unless=["is_solar_panel_heating", "is_hot"])
        | off.to.itself()
        | heating.to(off, unless=["is_active_time"])
        | idle.to(off, unless=["is_active_time"])
        | hot.to(off, unless=["is_active_time"])
        | cold.to(off, unless=["is_active_time"])
        | hot.to.itself()
        | cold.to.itself()
        | idle.to.itself()
        | heating.to.itself()
    )

    to_off = (
        off.to(off, unless=["is_active_time"])
        | heating.to(off, unless=["is_active_time"])
        | idle.to(off, unless=["is_active_time"])
        | hot.to(off, unless=["is_active_time"])
        | cold.to(off, unless=["is_active_time"])
    )

    to_cold = (
        off.to(cold, cond=["is_cold"], unless=["is_active_time"])
        | heating.to(cold, cond=["is_cold"], unless=["is_active_time"])
        | idle.to(cold, cond=["is_cold"], unless=["is_active_time"])
        | hot.to(cold, cond=["is_cold"], unless=["is_active_time"])
        | cold.to(cold, cond=["is_cold"], unless=["is_active_time"])
    )

    to_hot = (
        off.to(hot, cond=["is_hot"])
        | heating.to(hot, cond=["is_hot"])
        | idle.to(hot, cond=["is_hot"])
        | hot.to(hot, cond=["is_hot"])
        | cold.to(hot, cond=["is_hot"])
    )

    state_update = ( to_off | to_cold | to_hot |
          off.to(hot, cond=["is_active_time", "is_hot", "house_occupied"])
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


if __name__ == "__main__":
    machine._graph()
    machine = WaterStateMachine(self)
