
entity_id = data.get("entity_id", 'media_player.living_room_tv')
show_name = data.get("show").lower()

common_button_seq = ['LEFT', 'LEFT', 'LEFT', 'LEFT', 'LEFT', 'LEFT', 'LEFT', 'LEFT', 'LEFT', 'LEFT', 'LEFT', 'LEFT', 'LEFT', 'UP', 'UP', 'UP', 'UP', 'UP', 'DOWN', 'ENTER']
shortcut_list = {
    "the big bang theory": "the big",
}

series_requiring_pin = [
    "blacklist",
]


def send_button( entity_id, button):
    service_data = { "entity_id": entity_id, "button": button }
    ret = hass.services.call('webostv','button', service_data, blocking=True)
    time.sleep(.2)
    
def move_cursor( entity_id, x, y ):
    x_pos, y_pos = 0,0
    while( x_pos > x  ):
        send_button( entity_id, "LEFT" )
        x_pos = x_pos - 1
    
    while( y_pos > y  ):
        send_button( entity_id, "UP" )
        y_pos = y_pos - 1
    
    while( y_pos < y  ):
        send_button( entity_id, "DOWN" )
        y_pos = y_pos + 1
        
    while( x_pos < x  ):
        send_button( entity_id, "RIGHT" )
        x_pos = x_pos + 1
    

def get_letter_coordinates( letter ):
    letter_idx = int(ord( letter )) # ASCII Table
    if letter_idx == 32:
      return 0,-1
    if letter_idx >= 97 and letter_idx <= 122:
        letter_idx = letter_idx - 97
    else:
        letter_idx = letter_idx + 48
        letter_idx = letter_idx + 6 * 4 + 2
    y = math.floor( letter_idx / 6 )
    x = letter_idx - y * 6
    return x,y
  
requires_pin = False
if show_name in series_requiring_pin:    
    requires_pin = True
  
# Change source if not in Netflix
tv_state = hass.states.get(entity_id)
if tv_state == "off":
    hass.services.call('media_player','turn_on', { "entity_id": entity_id }, blocking=True)
    time.sleep(5)

tv_source = hass.states.get(entity_id).attributes.get('source')
if not tv_source == "Netflix":
    service_data = { "entity_id": entity_id, "source": "Netflix" }
    hass.services.call('media_player','select_source', service_data, blocking=True)
    time.sleep(5)
    send_button( entity_id, "ENTER" )
    time.sleep(1)
    send_button( entity_id, "BACK" )
    #logger.info("Switching %s to Netflix", entity_id)

# Send TV to search menu
#logger.info("Send common button list")
for cmd in common_button_seq:
    send_button( entity_id, cmd )


# Send backspace 20 times to clear possible buffer
#logger.info("Enter show name")
move_cursor( entity_id, 1, -1 )
for i in range(0,25):
    send_button( entity_id, "ENTER" )
move_cursor( entity_id, -1, 1)


# Enter show name
if show_name in shortcut_list:
    show_name = shortcut_list[show_name]



x_pos, y_pos = 0,0
for letter in show_name:
    x,y = get_letter_coordinates(letter)
    move_cursor( entity_id, x-x_pos, y-y_pos )
    x_pos, y_pos = x,y
    send_button( entity_id, "ENTER" )
    


    
  
# Return to letter 'a'
move_cursor( entity_id, 0-x_pos, 0-y_pos )
x_pos, y_pos = 0,0
move_cursor( entity_id, 6, 0 )
send_button( entity_id, "ENTER" )
time.sleep(1)
send_button( entity_id, "ENTER" )

if requires_pin:
    time.sleep(1)
    
    send_button( entity_id, "ENTER" )
    
    send_button( entity_id, "RIGHT" )
    send_button( entity_id, "RIGHT" )
    send_button( entity_id, "DOWN" )
    send_button( entity_id, "DOWN" )
    send_button( entity_id, "ENTER" )
    
    send_button( entity_id, "LEFT" )
    send_button( entity_id, "LEFT" )
    send_button( entity_id, "ENTER" )
    
    send_button( entity_id, "RIGHT" )
    send_button( entity_id, "RIGHT" )
    send_button( entity_id, "ENTER" )
    
    send_button( entity_id, "DOWN" )
    send_button( entity_id, "DOWN" )
    send_button( entity_id, "ENTER" )
