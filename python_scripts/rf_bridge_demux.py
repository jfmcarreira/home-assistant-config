d = { '57E10A':['washing_machine_door','ON','true'],
      '57E10E':['washing_machine_door','OFF','true'],
      '58940A':['dryer_machine_door','ON','true'],
      '58940E':['dryer_machine_door','OFF','true'],
      'E11841':['kitchen_fan_slider','ON','true'],
    }

p = data.get('payload')

if p is not None:
  if p in d.keys():
    service_data = {'topic':'binary_rf_sensors/{}'.format(d[p][0]), 'payload':'{}'.format(d[p][1]), 'qos':1, 'retain':'{}'.format(d[p][2])}
  else:
    service_data = {'topic':'binary_rf_sensors/unknown', 'payload':'{}'.format(p), 'qos':0, 'retain':'false'}
  hass.services.call('mqtt', 'publish', service_data, False)
