"""
List of rooms 
LIST OF ROOMS / LISTA DE DIVISÔES

Since these names target voice assistant a dictionary is created
to provide more than one name to each room, and thus support 
for different languages
  
The second position is the entity_id name and valetudo zone id
The third column is the room_id in the oficial firmware

When using original firmware:
In order to find the room id one can use trial and error using the following command:
    `miiocli  vacuum --ip <IP> --token <TOKEN> segment_clean <integer number>`
and check the output in the xiaomi app
To run this command install `python-miio`

Array example:
#    Room Name                                       Room code name    Room id
vaccum_room_list = [                                                   
    (['sala', 'living room'],                       'living_room',     [18]),
    (['cozinha', 'kitchen'],                        'kitchen',         [19]),
]

vaccum_room_list = [                                                   
    (['sala', 'living room'],                       'living_room'   ),
    (['cozinha', 'kitchen'],                        'kitchen'       ),
]
"""

application_name = "valetudo"

vaccum_room_list = [                                                   
    (['sala', 'living room'],                       'LivingRoom'   ),
    (['corredo', 'hallway'],                        'Hallway'      ),
    (['cozinha', 'kitchen'],                        'Kitchen'      ),
    (['casa de banho', 'bathroom'],                 'Bathroom'     ),
    (['quarto', 'bedroom'],                         'Bedroom'      ),
    (['escritório', 'office'],                      'Office'       ),
    (['quarto do fundo', 'guest bedroom'],          'GuestBedroom' )
]

# This is the room name as per 'room_alias'
room = data.get("room").lower()

# Number of runs per room
runs = int( data.get("runs", '1') )

# Start with delay
delay = int( data.get("delay", '0') )

vaccum_room_param = []
if room == "switch_based":
    # Run through all room that are vacuum friendly
    for r in vaccum_room_list:
        entity_name = ('input_boolean.vaccum_'+r[1]).lower()
        should_vaccum = ( hass.states.get( entity_name ).state == 'on' )
        if should_vaccum:
            if application_name == "xiaomi":
                vaccum_room_param.extend( r[2] )
            else:
                vaccum_room_param.append( r[1] )

else:
    # Single run
    for r in vaccum_room_list:
        if room in r[0]:
            if application_name == "xiaomi":
                vaccum_room_param.extend( r[2] )
            else:
                vaccum_room_param.append( r[1] )


vaccum_room_array = []
for r in vaccum_room_param:
    for i in range(runs):
        vaccum_room_array.append( r )

# TODO: Check how to do this
#time.sleep( delay * 60 )

if application_name == "xiaomi":
    # Service call when using the original xiaomi app
    service_data = { "entity_id": "vacuum.roborock", "command": "app_segment_clean", "params": vaccum_room_array } 
else:
    # Service call when using the valetudo app
    service_data = { "entity_id": "vacuum.roborock", "command": "zoned_cleanup", "params": { 'zone_ids': vaccum_room_array } } 

logger.info('vacuum.send_command {}'.format(service_data))
hass.services.call('vacuum','send_command', service_data, False)
