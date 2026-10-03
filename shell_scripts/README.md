# External commands

These files run outside Home Assistant's Python-script sandbox. Package
`shell_command` definitions supply their command lines and installation-specific
parameters; filenames alone do not establish that a command is scheduled.

| File | Purpose |
| --- | --- |
| `daily_insert_mysql.py` | External database-insertion adapter used by task/meter persistence. |
| `meo_box_reset_program.py` | External MEO program-control helper. |
| `proxmox_control_vm.bash` | Proxmox VM control helper. |
| `clean_snapshots.bash` | Snapshot maintenance. |
| `commit_changes.bash` | Configuration-repository maintenance helper. |

Database calls are wired from `packages/base/external_db.yaml` and consumed by
task blueprints and utility-meter automations. These commands depend on the
execution environment and external services; documenting them does not run them.
