"""
LIST OF ROOMS / LISTA DE DIVISÔES

The first position is the name of the room. 
These names target voice assistant, therefore a dictionary is created
to provide more than one name to each room, and thus support 
for different languages
  
The second position is the entity_id name and valetudo zone id
The third column is the room_id in the oficial firmware or Valetudo RE app

The fourth column is for setting if it is a zone (True) or segment (False)

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

"""

application_name = "valetudo_re" # or "xiaomi" or "valetudo"

vaccum_room_list = [        
    #  Room Name                                        Room code name             Room id (name or number)       Is Zone?
    (['sala', 'living room'],                           'LivingRoom',              ["LivingRoom"],                False ),
    (['corredor', 'hallway'],                           'Hallway',                 ["Hallway"],                   False ),
    (['cozinha', 'kitchen'],                            'Kitchen',                 ["Kitchen"],                   False ),
    (['casa de banho', 'bathroom'],                     'Bathroom',                ["Bathroom"],                  False ),
    (['quarto', 'bedroom'],                             'Bedroom',                 ["Bedroom"],                   False ),
    (['casa de banho privada', 'bedroom bathroom'],     'BedroomBath',             ["PrivateBathroom"],           False ),
    (['escritório', 'office'],                          'Office',                  ["Office"],                    False ),
    (['quarto do fundo', 'guest bedroom'],              'GuestBedroom',            ["GuestBedroom"],              False ),
    (['casa de banho centro', 'bathroom center'],       'BathroomCenter',          ["BathroomSemBalanca"],        True  ),
    (['sala com tapetes', 'living room with carpet'],   'LivingRoomWithCarpet',    ["LivingRoomWithCarpet"],      True  ),
]

# Get vacuum entity_id (if more than one) (string)          
entity_id = data.get("entity_id", 'vacuum.roborock')

# This is the room name as per 'room_alias' (string)
room = data.get("room").lower()

# Define whether to clean rooms or segments (int)
is_zone = int( data.get("is_zone", -1) )

# Number of runs per room (integer)
runs = int( data.get("runs", '1') )

# Start with delay in minutes (integer) - WIP
delay = int( data.get("delay", '0') )

vaccum_room_ids = []

# Case where you want to vacuum all rooms switched on
# For this it is needed to set is_zone input
if room == "switch_based":
    # Run through all room that are vacuum friendly
    for r in vaccum_room_list:
        if is_zone == -1 or int(r[3]) == is_zone:
          entity_name = ('input_boolean.vacuum_'+r[1]).lower()
          should_vaccum = ( hass.states.get( entity_name ).state == 'on' )
          if should_vaccum:
              if is_zone == -1: # overwrite is_zone information
                  is_zone = int(r[3])
              vaccum_room_ids.extend( r[2] )

else:
    # Single room
    for r in vaccum_room_list:
        if is_zone == -1 or int(r[3]) == is_zone:
            if room in r[0]:
                if is_zone == -1: # overwrite is_zone information
                    is_zone = int(r[3])
                vaccum_room_ids.extend( r[2] )
                break


if len( vaccum_room_ids ) > 0:
    if application_name == "xiaomi":
        # Xiaomi only supports segment cleaning
        # Repeat rooms to do multiple runs
        vaccum_room_param = []
        for r in vaccum_room_ids:
            for i in range( runs ):
                vaccum_room_param.append( r )
        # Service call when using the original xiaomi app
        service_data = { "entity_id": entity_id, "command": "app_segment_clean", "params": vaccum_room_param } 
        
    elif application_name == "valetudo":
        # Multiple runs not implemented yet
        # Service call when using the valetudo app
        service_data = { "entity_id": entity_id, "command": "zoned_cleanup", "params": { "zone_ids": vaccum_room_param } } 
        
    elif application_name == "valetudo_re":
        # Service call when using the valetudo re app
        if is_zone:
            vaccum_room_param = []
            for r in vaccum_room_ids:
                for i in range( runs ):
                    vaccum_room_param.append( { "id": r, "repeats": runs } )
            service_data = { "entity_id": entity_id, "command": "zoned_cleanup", "params": { "zone_ids": vaccum_room_param } } 
        else:
            service_data = { "entity_id": entity_id, "command": "segmented_cleanup", "params": { "segment_ids": vaccum_room_ids, "repeats": runs } } 
            
        
    hass.services.call('vacuum','send_command', service_data, False)

else:
    logger.warning("No segments / zones to vacuum")
