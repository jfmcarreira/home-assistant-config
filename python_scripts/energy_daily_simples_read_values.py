#!/usr/local/bin/python
# coding: utf8
import json
import datetime
import sys
import re

def main(argv):
  argm = argv[0]
  argd = argv[1]
  json_file_path = '/config/data/energy_daily_simples_kw.json'
  
  if re.match("^([Jj][Aa][Nn]|01|1)", argm):
    month = 1
  elif re.match("^([Ff][Ee][VvBb]|02|2)", argm):
    month = 2
  elif re.match("^([Mm][Aa][Rr]|03|3)", argm):
    month = 3
  elif re.match("^([Aa][BbPp][Rr]|04|4)", argm):
    month = 4
  elif re.match("^([Mm][Aa][IiYy]|05|5)", argm):
    month = 5
  elif re.match("^([Jj][Uu][Nn]|06|6)", argm):
    month = 6
  elif re.match("^([Jj][Uu][Ll]|07|7)", argm):
    month = 7
  elif re.match("^([Aa][GgUu][OoGg]|08|8)", argm):
    month = 8
  elif re.match("^([Ss][Ee][TtPp]|09|9)", argm):
    month = 9
  elif re.match("^([Oo][UuCc][Tt]|10)", argm):
    month = 10
  elif re.match("^([Nn][Oo][Vv]|11)", argm):
    month = 11
  elif re.match("^([Dd][Ee][ZzCc]|12)", argm):
    month = 12
  else:
    month = datetime.datetime.today().month
    # raise ValueError("Month unreadable, accepts portuguese or english month name, also accepts numeric")
  
  dt = datetime.datetime.today()
  # dt = dt.replace(day=int(argd), month=month)
  try:
    dt = dt.replace(day=int(argd), month=month)
  except ValueError as e:
    if str(e) == "day is out of range for month":
      #
      # Best is to print unknown, but mini-graph-card ignores unknown
      # and shows last not-unknown value. So this method isn't recommended
      #
      # print("unknown")
      print("0")
      return
    raise ValueError("Day must be an integer")
  
  with open(json_file_path, 'r') as data_file:
    try:
      data = json.load(data_file)
    except ValueError:
      raise ValueError("Json file isn't correctly formatted")
  
  try:
    # Previous year
    if datetime.datetime.today().month < month:
      dt = dt.replace(year=dt.year-1)
      print (data[str(dt.year)][dt.strftime("%B")][str(dt.day)])
      return
    # Current year
    else:
      # Current month
      if dt.month == datetime.datetime.today().month:
        if dt.day > datetime.datetime.today().day:
          # print("unknown")
          print("0")
          return
    print (data[str(dt.year)][dt.strftime("%B")][str(dt.day)])
    return

  except KeyError as e:
    print("0")

if __name__ == "__main__":
  try:
    # ARGV
    # 1 or January = month (numeric or string)
    # 2 = day (numeric)
    # Example: python file.py 2 24
    # February, 24
    if len(sys.argv) == 3:
      main(sys.argv[1:3])
    else:
      raise ValueError("Argument required")
  except IndexError:
    raise ValueError("Argument required")