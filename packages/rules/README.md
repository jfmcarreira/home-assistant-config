# Task-reminder event

`event_remain_task_todo.yaml` emits `event_remaind_task_todo` at minute 30 of each
hour, when either resident arrives home, or when the kitchen door opens.

The event producer does not check due tasks or notification eligibility. The
task blueprints consume it and apply due-state, presence, do-not-disturb and
throttling rules. Preserve the existing event spelling when following or editing
consumers; the filename and event name are not identical.
