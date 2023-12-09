#!/usr/local/bin/python
# coding: utf8
import datetime
import argparse
## on homeassistant container:
## pip install pymysql
import pymysql
#import mysql.connector as mysql
import warnings

def main(args):
  with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    if args.value == "unavailable":
      return

    try:
      if args.write_str:
        db_value = str(args.value)
      else:
        db_value = float(args.value)
    except:
      ValueError("Cannot parse value to write")
      return


    #try:
    dt = datetime.datetime.now()
    if args.date is not None:
        dt = datetime.datetime.strptime(args.date, "%Y-%m-%d %H:%M:%S")
    if args.use_date_time:
      formatted_date = dt.strftime("%Y-%m-%d %H:%M")
      date_type = "DATETIME"
    else:
      formatted_date = dt.strftime("%Y-%m-%d")
      date_type = "DATE"
    # except:
    #   ValueError("Cannot parse date time to write")
    #   return

    #print(date_type)

    colname = (args.col if args.col is not None else "value")


    connection = pymysql.connect(
      host=args.host,
      user=args.user,
      password=args.password,
      db=args.db,
      charset="utf8mb4"#,
      #cursorclass=pymysql.cursors.DictCursor
    )

    # connection = mysql.connect(
    #   host=args.host,
    #   user=args.user,
    #   password=args.password,
    #   database=args.db,
    # )


    try:
      with connection.cursor() as cursor:
        sql = """CREATE TABLE IF NOT EXISTS `{table}` (
          `date` {dtype} NOT NULL,
          PRIMARY KEY (`date`))
          COLLATE='utf8mb4_unicode_ci'
          ENGINE=InnoDB;""".format(table=args.table,dtype=date_type)
        cursor.execute(sql)

        sql = "ALTER TABLE `{table}` ADD COLUMN IF NOT EXISTS `{col}` FLOAT NULL DEFAULT NULL;".format(table=args.table, col=colname)
        cursor.execute(sql)

        sql = "INSERT INTO `{table}` (`date`, `{col}`) VALUES (%s, %s) ON DUPLICATE KEY UPDATE {col}=%s;".format(table=args.table, col=colname)
        sql_data = (formatted_date, db_value, db_value)
        cursor.execute(sql, sql_data)

      connection.commit()

    finally:
      connection.close()
    # except:
    #   ValueError("Cannot comunicate with DB")



if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Insert kWh value of current day to mariadb database. This creates table if not exists.")
  parser.add_argument('--host', type=str, required=True, help='REQUIRED: DB Host')
  parser.add_argument('--user', type=str, required=True, help='REQUIRED: DB User')
  parser.add_argument('--password', type=str, required=True, help='REQUIRED: DB Password')
  parser.add_argument('--db', type=str, required=True, help='REQUIRED: DB Name')
  parser.add_argument('--table', type=str, required=True, help='REQUIRED: DB Table')
  parser.add_argument('--value', type=str, required=False, help='OPTIONAL: Value to insert')
  parser.add_argument('--write_str', type=bool, required=False, help='OPTIONAL: Select between float and string', default=False)
  parser.add_argument('--col', type=str, required=False, help='OPTIONAL: Column name. Defaults to `value`')
  parser.add_argument('--date', type=str, required=False, help='OPTIONAL: Date string. Defaults to today')
  parser.add_argument('--use_date_time', type=bool, required=False, help='OPTIONAL: Use full date', default=False)
  args = parser.parse_args()

  try:
    main(args)
  except IndexError:
    raise ValueError("Argument required")
