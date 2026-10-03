# Household tasks and appliance state

Task completion history is stored in an external database, rather than inferred
solely from the current device state. Root task automations use the tracked-task
and two-step-machine blueprints to record completion and refresh sensors.

## Appliance lifecycle

Washing machine, dryer and dishwasher packages combine:

1. A running-state binary sensor based on power consumption.
2. A last-cycle-completed timestamp and an emptied/removed timestamp.
3. A pending task when the completion timestamp is newer than the removal timestamp.
4. A display sensor combining door, running and pending-task states.

The shared power blueprint turns on above 50 W after one minute and turns off
below 3 W after two minutes. Its hysteresis prevents pauses within a cycle from
immediately declaring the appliance finished.

Machine completion records task timing and energy. Removing items is a second
event: door-open duration or a notification action records it. Root washing/dryer
instances disable mobile reminders; the dishwasher instance enables them and
requires a two-minute open door for automatic emptying confirmation.

## Other tracked work

Cat-litter cleaning/replacement, water-filter maintenance and vitamin D have
separate due-state logic. Litter replacement and filter replacement also consume
Grocy stock through their root task automation's extra actions.
`tracker.yaml` combines selected outstanding tasks into `binary_sensor.tasks`;
it is not a count or an exhaustive aggregation of every task in the folder.

The misspelled `event_remaind_task_todo` event is the existing contract between
[`rules/`](../rules/README.md) and reminder blueprints. Reminders select residents
at home and apply their own do-not-disturb, time and throttling conditions.
Explicit completion requests can bypass due-state conditions in caller scripts.
