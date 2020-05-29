"""
List of rooms 
(Lista de divisões)
  Since these names target voice assistant a dictionary is created
  to provide more than one name to each room, and thus support 
  for different languages
  The second position is the id in the vaccum app
"""
#    Room Name                                       Room code name    Room id
vaccum_room_list = [                                                   
    (['sala', 'living room'],                       'living_room',     [18]),
    (['cozinha', 'kitchen'],                        'kitchen',         [19]),
    (['escritório', 'office'],                      'office',          [1]),
    (['casa de banho', 'bathroom'],                 'bathroom',        [20]),
    (['quarto', 'bedroom'],                         'bedroom',         [17]),
    (['casa de banho privada', 'private bathroom'], 'private_bath',    [2]),
    (['quarto do fundo', 'guest bedroom'],          'guest_bedroom',   [21]),
]

"""
In order to find the room id one can use trial and error using the following command:
    miiocli  vacuum --ip <IP> --token <TOKEN> segment_clean <integer number>
and check the output in the xiaomi app
"""

# This is the room name as per 'room_alias'
room = data.get("room").lower()

# Number of runs per room
runs = int( data.get("runs", '1') )

vaccum_room_param = []
if room == "all":
    # Run through all room that are vaccum friendly
    for r in vaccum_room_list:
        should_vaccum = hass.states.get( 'input_boolean.vaccum_'+r[1] ).state == 'on'
        if should_vaccum:
            vaccum_room_param.extend( r[2] )

else:
    # Single run
    for r in vaccum_room_list:
        if room in r[0]:
            vaccum_room_param.extend( r[2] )


vaccum_room_array = []
for r in vaccum_room_param:
    for i in range(runs):
        vaccum_room_array.append( r )


service_data = { "entity_id": "vacuum.roborock", "command": "app_segment_clean", "params": vaccum_room_array } 
hass.services.call('vacuum','send_command', service_data, False)
