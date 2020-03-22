
entity_id = data.get("entity_id", 'media_player.living_room_tv_meo_box')
channel = data.get("channel").lower()


meo_channels = {
    'rtp1': '1',
    'rtp2': '2',
    'sic': '3',
    'sick': '3',
    'tvi': '4',
    'sic news': '5',
    'sick news': '5',
    'rtp 3': '6',
    'tvi 24': '7',
    'cmtv': '8',
    'sport tv plus': '9',
    'tv globe basic': '10',
    'sic woman': '11',
    'sick woman': '11',
    "wife ' s favorite channel": '11',
    'oporto hd': '12',
    'sic faces': '14',
    'sick faces': '14',
    'sic radical': '15',
    'sick radical': '15',
    'rtp memory': '17',
    'twenty four kitchen': '18',
    'disney channel': '50',
    "baby ' s favorite channel": '51',
    'disney junior': '51',
    'cartoon network': '53',
    'panda': '54',
    'panda bigs': '55',
    'panda biggs': '55',
    'baby tv': '56',
    'sic kids': '57',
    'sick kids': '57',
    'boomerang': '58',
    'jim jam': '59',
    'hollywood': '80',
    'hollywood hd': '81',
    'cineworld': '82',
    'cineworld sd': '83',
    'fox movies hd': '84',
    'fox movies': '85',
    'fox hd': '86',
    'fox': '87'
}

def switch_channel_number(hass, entity_id, channel):
    service_data = { "entity_id": entity_id, "media_content_id": channel, "media_content_type": "channel" }
    hass.services.call('media_player','play_media', service_data, False)

if channel in meo_channels:
    dic_channel = meo_channels[channel]
    switch_channel_number(hass, entity_id, dic_channel)
else:
    switch_channel_number(hass, entity_id, channel)