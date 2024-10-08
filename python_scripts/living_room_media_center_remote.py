send_via_broadlink = False

numeric_commands_list = [ "NUMBER_1", "NUMBER_2", "NUMBER_3", "NUMBER_4", "NUMBER_5", "NUMBER_6", "NUMBER_7", "NUMBER_8", "NUMBER_9", "NUMBER_0"]

# Always conver to upper case to avoid problems
button = data.get("button").upper()

if button == "OK" or button == "OKAY":
    button = "ENTER"

tv_source = "TV"
# Always send volume to TV
if button == "VOLUME UP" or button == "VOLUME DOWN":
    tv_source = "TV"
else:
    tv_source = hass.states.get('sensor.living_room_tv_source').state

if tv_source == "MEO":

    if button == "UP":
        button = "DPAD_UP"
    elif button == "DOWN":
        button = "DPAD_DOWN"
    elif button == "LEFT":
        button = "DPAD_LEFT"
    elif button == "RIGHT":
        button = "DPAD_RIGHT"
    elif button == "ENTER":
        button = "DPAD_CENTER"
    elif button == "EXIT":
        button = "Exit"
    elif button == "INFO":
        button = "Info"
    elif button == "PLAY":
        button = "MEDIA_PLAY_PAUSE"
    elif button == "PAUSE":
        button = "MEDIA_PLAY_PAUSE"
    elif button == "SKIP-BACKWARD":
        button = "Rewind"
    elif button == "SKIP-FOWARD":
        button = "Forward"
    elif button == "PREV":
        button = "Prev"
    elif button == "NEXT":
        button = "Next"
    service_data = { "entity_id": "remote.living_room_tv_meo_box", "command": button }
    hass.services.call('remote','send_command', service_data, False)

elif tv_source == 'Kodi':

    if button == "UP":
        button = "Input.Up"
    elif button == "DOWN":
        button = "Input.Down"
    elif button == "LEFT":
        button = "Input.Left"
    elif button == "RIGHT":
        button = "Input.Right"
    elif button == "HOME":
        button = "Input.Home"
    elif button == "ENTER":
        button = "Input.Select"
    elif button == "BACK":
        button = "Input.Back"

    entity_id = "media_player.living_room_tv_kodi"
    service_data = { "entity_id": entity_id, "method": button }
    hass.services.call("kodi","call_method", service_data, False)

else:
    broadlink_device = "lgtv_sala"

    if button == 'VOLUME UP':
        button = 'VolUp'
    elif button == 'VOLUME DOWN':
        button = 'VolDown'

    entity_id = "media_player.living_room_tv"
    service_data = { "entity_id": entity_id, "button": button }
    hass.services.call("webostv","button", service_data, False)

if send_via_broadlink:
    entity_id = "remote.living_room_tv"
    service_data = { "entity_id": entity_id, "device": broadlink_device, "command": button, "num_repeats": 1 }
    hass.services.call("remote","send_command", service_data, False)
