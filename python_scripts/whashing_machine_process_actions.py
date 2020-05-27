wet_clothes = bool( hass.states.get('binary_sensor.wash_machine_wet_clothes').state )
dry_clothes = bool( hass.states.get('binary_sensor.wash_machine_dry_clothes').state )
if wet_clothes:
    hass.services.call('script','task_laundry_remove_wet_clothes' )

elif dry_clothes:
    hass.services.call('script','task_laundry_remove_dry_clothes' )
