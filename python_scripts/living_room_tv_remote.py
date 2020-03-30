entity_id = data.get("entity_id", 'media_player.living_room_tv')
button = data.get("button").upper()
if button == 'OK':
    button = 'ENTER'
service_data = { "entity_id": entity_id, "button": button }
hass.services.call('webostv','button', service_data, False)