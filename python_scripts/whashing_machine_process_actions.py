wet_clothes = bool( hass.states.get('binary_sensor.wash_machine_wet_clothes').state )
dry_clothes = bool( hass.states.get('binary_sensor.wash_machine_dry_clothes').state )
#logger.warning("Wet={}, Dry={}".format(wet_clothes, dry_clothes))
if wet_clothes:
    #logger.warning("Taking clothes out of the wahing machine at {}".format(time))
    service_data = { "chore_id": "4" }
    hass.services.call('grocy','execute_chore', service_data, False)

    service_data = { "message": "clear_notification", "data" : { "tag": "laundry_wet_clothes_notification" }}
    hass.services.call('notify','mobile_app_all', service_data, False)

elif dry_clothes:
    #logger.warning("Taking clothes out of the clothes hanger at {}".format(time))
    service_data = { "chore_id": "6" }
    hass.services.call('grocy','execute_chore', service_data, False)
