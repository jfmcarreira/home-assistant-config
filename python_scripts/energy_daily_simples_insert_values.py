#!/usr/local/bin/python
# coding: utf8
import json
import datetime
import sys
import os

def main(argv):
  dt = datetime.datetime.today()
  json_file_path = '/config/data/energy_daily_simples_kw.json'
  
  if not os.path.exists(json_file_path):
    with open(json_file_path, 'w'): pass

  with open(json_file_path, 'r') as data_file:
    try:
      data = json.load(data_file)
    except ValueError:
      data = {
        str(dt.year): {
          dt.strftime("%B"): {
            str(dt.day): 0.0
          }
        }
      }
  
  with open(json_file_path, 'w') as data_file:
    for i in range(0,10):
      try:
        data[str(dt.year)][dt.strftime("%B")][str(dt.day)] = float(argv)
      except KeyError:
        data[str(dt.year)][dt.strftime("%B")] = {}
        continue
      break
    
    json.dump(data, data_file)

    

if __name__ == "__main__":
  try:
    main(sys.argv[1])
  except IndexError:
    raise ValueError("Argument required")