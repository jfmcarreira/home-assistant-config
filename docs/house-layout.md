# House layout and naming

The ground-floor living area uses floor ID `living_floor`; the upstairs bedroom
floor uses `bedrooms`. `outside` is used for exterior control targets. There are
also house-wide and seasonal areas that do not represent an individual room.

| Physical space | Configuration names | Notes |
| --- | --- | --- |
| Ground-floor living room | `living_room` | Includes table and window lighting, TV/media and arrival-path controls. |
| Ground-floor hallway | `hallway`, `hallway_presence`, `doorway` | Distinct from the upstairs `hall`; presence lighting is coordinated with nearby main lights. |
| Kitchen and pantry | `kitchen`, `kitchen_pantry` | The kitchen door is part of arrival/departure and exterior-light sequences. |
| Laundry | `laundry` | Appliance completion and clothes-removal tracking are separate tasks. |
| Office | `office` | Office Assist satellite, voice player and MacBook-related presence logic. |
| Ground-floor bedroom / storage bedroom | `bedroom_rc` | Labelled Quarto de Arrumos in controls; distinct from exterior `storage`. |
| Ground-floor bathroom | `bathroom_rc` | Its shutter is `cover.bathroom`, because this is the only bathroom with a shutter. |
| Upstairs hall | `hall` | Hall AC, tablet and speaker; some older aliases refer to Sótão. |
| Upstairs main bathroom | `main_bathroom`, area target `bathroom_main` | Entity and area naming differ in existing control targets. |
| Master bedroom and ensuite | `master_bedroom`, `master_bedroom_bathroom` | Bedside lights and ensuite have separate controls. |
| Children's bedrooms | `bedroom_ricardo`, `bedroom_henrique` | Individual shutters, climate units and baby-monitor rules. |
| Stairs | `stairs`, `stairs_down`, `stairs_wall`, `stairs_lamp` | Connect floors; the shutter is included in the upstairs cover group. |
| Exterior storage | `storage` | Outside the house, not the ground-floor storage bedroom. |
| Exterior entrances | `gate`, `gate_door`, `front_door`, `kitchen_door` | Vehicle gate, pedestrian gate and two house doors are different devices. |

## Shutter group naming

[`packages/covers/first_floor.yaml`](../packages/covers/first_floor.yaml) controls
the ground-floor shutters despite its name: living room, kitchen, laundry,
`bathroom`, `bedroom_rc` and office.
[`second_floor.yaml`](../packages/covers/second_floor.yaml) controls the master
bedroom, children's bedrooms and stairs. Each group acts only on rooms whose
group-selection helpers are on.

## Exterior orientation

The existing heat-control workflows classify kitchen/master-bedroom shutters as
west-facing and stairs/ground-floor bedroom/laundry as south-facing. This is the
classification encoded by the automation targets, not a surveyed floor plan.
The driveway image-analysis script describes its view as the gate entrance,
west facade and area near the kitchen; front-camera analysis is a separate view.

## Presence is not room motion

`binary_sensor.notify_home` combines Joao, Bianca and guest presence. Guest state
also includes the cleaning calendar. Motion sensors can detect cats, so Sleep
and absence restrictions are meaningful lighting controls, not redundant checks.
Room occupancy, manual lighting and household presence answer different questions.
