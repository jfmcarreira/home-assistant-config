d = { '58940A':['fridge_door','ON','true'],
      '58940E':['fridge_door','OFF','true'],
      '57E10A':['wash_machine_door','ON','true'],
      '57E10E':['wash_machine_door','OFF','true'],
      #'F1E77E':['litter_box_motion','ON','false'],
      'F1E77E':['motion_sensor_office','ON','false'],
      #'BDA5B9':['sonoff_door_sensor','ON','false'],
    }

p = data.get('payload')

if p is not None:
  if p in d.keys():
    service_data = {'topic':'binary_rf_sensors/{}'.format(d[p][0]), 'payload':'{}'.format(d[p][1]), 'qos':1, 'retain':'{}'.format(d[p][2])}
  #else:
  #  service_data = {'topic':'binary_rf_sensors/unknown', 'payload':'{}'.format(p), 'qos':0, 'retain':'false'}
  #  logger.warning('<rfbridge_demux> Received unknown RF command: {}'.format(p))
  hass.services.call('mqtt', 'publish', service_data, False)
