"""
List of rooms 
(Lista de divisões)
  Since these names target voice assistant a dictionary is created
  to provide more than one name to each room, and thus support 
  for different languages
"""
room_alias = {
    'Sala': 'living_room',
    'Living Room': 'living_room',
    'Cozinha': 'kitchen',
    'Kitchen': 'kitchen',
    'Escritório': 'office',
    'Office': 'office',
    'Casa de Banho': 'bathroom',
    'Casa de Banho': 'bathroom',
    'Quarto': 'master_bedroom',
    'Bedroom': 'master_bedroom',
    'Casa de Banho Privada': 'private_bathroom',
    'Private Bathroom': 'private_bathroom',
    'Quarto do Fundo': 'guest_bedroom',
    'Guest Bedroom': 'guest_bedroom',
    'Bedroom and Bathroom': 'master_bedroom_bathroom'
}

"""
Dictionary mapping id with an array of rooms in the Xiaomi app
(Mapeamento das rooms na app da Xiaomi)
"""
vaccum_room_id = {
    'living_room': [18],
    'kitchen': [19],
    'office': [1],
    'bathroom': [20],
    'master_bedroom': [17],
    'private_bathroom' [2],
    'master_bedroom_bathroom': [17, 2],
    'guest_bedroom': [21]
}

"""
In order to find the room number one can use trial and error using the following command:
    miiocli  vacuum --ip <IP> --token <TOKEN> segment_clean <integer number>
and check the output in the xiaomi app
"""

# This is the room name as per 'room_alias'
room = data.get("room").lower()

# Number of runs per room
runs = int( data.get("runs", '1') )

# Map from the room name to the vaccum room parameter
vaccum_room_param = vaccum_room_id[room_alias[room]]

vaccum_room_array = []
for r in room_param:
    for i in range(runs):
        vaccum_room_array.append( vaccum_room_param[r] )


service_data = { "entity_id": "vacuum.roborock", "command": "app_segment_clean", "params": vaccum_room_array } 
hass.services.call('vacuum','send_command', service_data, False)