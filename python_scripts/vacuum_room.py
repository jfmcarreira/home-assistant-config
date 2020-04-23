room = data.get("room").lower()
runs = int( data.get("runs", '1') )

room_param = []
if room == "sala" or room == "living room":
    room_param.append( 18 )
elif room == "cozinha" or room == "kitchen":
    room_param.append( 19 )
elif room == "escritório" or room == "office":
    room_param.append( 1 )
elif room == "quarto" or room == "bedroom":
    room_param.append( 17 )
elif room == "quarto do fundo" or room == "second bedroom":
    room_param.append( 21 )
elif room == "casa de banho principal" or room == "bathroom":
    room_param.append( 20 )
elif room == "casa de banho do quarto" or room == "private bathroom":
    room_param.append( 2 )
elif room == "quarto e cozinha" or room == "bedroom and bathroom":
    room_param.append( 17 )
    room_param.append( 2 )
else:
    exit(1)

room_array = []
if runs > 1:
    for i in range(runs):
        room_array.append( room_param[0] )
else:
    room_array = room_param

service_data = { "entity_id": "vacuum.roborock", "command": "app_segment_clean", "params": room_array } 
hass.services.call('vacuum','send_command', service_data, False)

# 1: Office
# 2: Casa de banho quarto
# 17: Quarto
# 18: Sala
# 19: Cozinha
# 20: Casa de Banho
# 21: Quarto do fundo