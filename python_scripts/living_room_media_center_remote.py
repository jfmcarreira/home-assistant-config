send_via_broadlink = False

numeric_commands_list = [ "NUMBER_1", "NUMBER_2", "NUMBER_3", "NUMBER_4", "NUMBER_5", "NUMBER_6", "NUMBER_7", "NUMBER_8", "NUMBER_9", "NUMBER_0"]

button = data.get("button").upper()

if button == "OK" or button == "OKAY":
    button = "ENTER" 

tv_source = "TV"
if button == "VOLUME UP" or button == "VOLUME DOWN":
    tv_source = "TV"
else:
    tv_source = hass.states.get('sensor.living_room_tv_source').state

if tv_source == "MEO":
    
    meo_box_state = hass.states.get('media_player.living_room_tv_meo_box').state

    broadlink_device = "meo"
    send_via_broadlink = True
    numeric_commands_list_meo = [ "NUMBER_1", "NUMBER_2", "NUMBER_3", "NUMBER_4", "NUMBER_5", "NUMBER_6", "NUMBER_7", "NUMBER_8", "NUMBER_9", "NUMBER_0"]
    if button in numeric_commands_list_meo or meo_box_state == 'unavailable':
        send_via_broadlink = True
    else:
        if button == "UP":
            button = "Up"
        elif button == "DOWN":
            button = "Down"
        elif button == "LEFT":
            button = "Left"
        elif button == "RIGHT":
            button = "Right"
        elif button == "HOME":
            button = "Menu"
        elif button == "ENTER":
            button = "OK"
        elif button == "BACK":
            button = "Back"
        elif button == "EXIT":
            button = "Exit"
        elif button == "INFO":
            button = "Info"
        elif button == "PLAY":
            button = "PlayPause"
        elif button == "PAUSE":
            button = "PlayPause"
        elif button == "SKIP-BACKWARD":
            button = "Rewind"
        elif button == "SKIP-FOWARD":
            button = "Forward"

        entity_id = "media_player.living_room_tv_meo_box" 
        service_data = { "entity_id": entity_id, "media_content_id": button, "media_content_type": "mediaroom" }
        hass.services.call('media_player','play_media', service_data, False)

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
    entity_id = "remote.universal_remote_living_room_remote"
    service_data = { "entity_id": entity_id, "device": broadlink_device, "command": button, "num_repeats": 1 }
    hass.services.call("remote","send_command", service_data, False)
