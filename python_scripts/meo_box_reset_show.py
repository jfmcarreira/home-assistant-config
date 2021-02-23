entity_id = data.get("entity_id", 'media_player.living_room_tv_meo_box')
show = data.get("show").lower()

if show == "current":
  command_list = ["INFO", "RIGHT", "ENTER"]
elif show == "previous":
  command_list = ["EXIT", "UP", "LEFT", "ENTER", "ENTER"]

meo_box_state = hass.states.get( entity_id ).state

for i in command_list:
  if meo_box_state == 'unavailable':
      service_data = { "entity_id": "remote.universal_remote_living_room_remote", "device": "meo", "command": i, "num_repeats": 1 }
      hass.services.call("remote","send_command", service_data, False)
  else:
      service_data = { "entity_id": entity_id, "media_content_id": i, "media_content_type": "channel" }
      hass.services.call('media_player','play_media', service_data, False)
  time.sleep(2)
