
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
    'sic woman': '11',
    'sick woman': '11',
    'baby tv': '48',
}

def switch_channel_number(hass, entity_id, channel):
    service_data = { "entity_id": entity_id, "media_content_id": channel, "media_content_type": "channel" }
    hass.services.call('media_player','play_media', service_data, False)

if channel in meo_channels:
    dic_channel = meo_channels[channel]
    switch_channel_number(hass, entity_id, dic_channel)
else:
    switch_channel_number(hass, entity_id, channel)
