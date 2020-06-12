"""
LIST OF ROOMS / LISTA DE DIVISÔES

The first position is the name of the room. 
These names target voice assistant, therefore a dictionary is created
to provide more than one name to each room, and thus support 
for different languages
  
The second position is the entity_id name and valetudo zone id
The third column is the room_id in the oficial firmware or Valetudo RE app

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

application_name = "valetudo_re" # or "xiaomi" or "valetudo"

vaccum_room_list = [                                          
    (['sala', 'living room'],              'LivingRoom',   [16]),
    (['corredor', 'hallway'],              'Hallway',      [17]),
    (['cozinha', 'kitchen'],               'Kitchen',      [18]),
    (['casa de banho', 'bathroom'],        'Bathroom',     [23]),
    (['quarto', 'bedroom'],                'Bedroom',      [21, 22]),     
    (['escritório', 'office'],             'Office',       [20]),      
    (['quarto do fundo', 'guest bedroom'], 'GuestBedroom', [19])
]

# Get vacuum entity_id (if more than one)
entity_id = data.get("entity_id", 'vacuum.roborock')

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
            if application_name == "xiaomi" or application_name == "valetudo_re":
                vaccum_room_param.extend( r[2] )
            elif application_name == "valetudo":
                vaccum_room_param.append( r[1] )

else:
    # Single room
    for r in vaccum_room_list:
        if room in r[0]:
            if application_name == "xiaomi":
                for i in range( runs ):
                    vaccum_room_param.extend( r[2] )
            elif application_name == "valetudo_re":
                vaccum_room_param.extend( r[2] )
            elif application_name == "valetudo":
                vaccum_room_param.append( r[1] )


if application_name == "xiaomi":
    # Service call when using the original xiaomi app
    service_data = { "entity_id": entity_id, "command": "app_segment_clean", "params": vaccum_room_param } 
elif application_name == "valetudo_re":
    # Service call when using the valetudo app
    service_data = { "entity_id": entity_id, "command": "segmented_cleanup", "params": { 'segment_ids': vaccum_room_param, 'repeats': runs } } 
elif application_name == "valetudo":
    # Service call when using the valetudo app
    service_data = { "entity_id": entity_id, "command": "zoned_cleanup", "params": { 'zone_ids': vaccum_room_param } } 


hass.services.call('vacuum','send_command', service_data, False)
