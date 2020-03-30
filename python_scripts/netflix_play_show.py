
entity_id = data.get("entity_id", 'media_player.living_room_tv')
show = data.get("show").lower()

common_button_seq = ['LEFT', 'UP', 'UP', 'UP', 'UP', 'UP', 'DOWN', 'ENTER']
show_list = {
    'big bang theory': ['RIGHT', 'ENTER', 'RIGHT', 'DOWN', 'ENTER', 'LEFT', 'LEFT', 'ENTER', 'UP', 'UP', 'ENTER', 'DOWN', 'RIGHT', 'ENTER', 'LEFT', 'ENTER', 'RIGHT', 'RIGHT', 'RIGHT', 'RIGHT', 'RIGHT', 'RIGHT', 'ENTER'],
}

def send_button( entity_id, button):
    logger.info("cmd %s", cmd)
    service_data = { "entity_id": entity_id, "button": cmd }
    ret = hass.services.call('webostv','button', service_data, blocking=True)
    time.sleep(.25)

if show in show_list:
    logger.info("Playing %s", show)
    button_seq = show_list[show]
    for cmd in common_button_seq:
        send_button( entity_id, cmd )
    for cmd in button_seq:
        send_button( entity_id, cmd )
    send_button( entity_id, 'ENTER' )

