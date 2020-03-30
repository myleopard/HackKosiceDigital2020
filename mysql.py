#    Instructions
#
# A) run 'pip install pymysql'
# B) send public ip address so i can add you to my google cloud db
# C) This is a helper file. import it then use the functions below.


# TODO: prevent SQL injection...

import pandas as pd
import pymysql

from datetime import datetime as dtt
format = "%Y-%m-%d %H:%M:%S"

# Open database connection
db = pymysql.connect(
  "35.205.60.66",       # db ip
  "root",               # username
  input("Password: "),  # password
  "shop"                # database
)

# prepare a cursor object to interact with database
cursor = db.cursor()

def createShopTable():
  cursor.execute("DROP TABLE IF EXISTS shop")
  cursor.execute("""CREATE TABLE shop (
    id INT AUTO_INCREMENT PRIMARY KEY,
    indexNum INT NOT NULL,
    quantity INT NOT NULL,
    reference INT NOT NULL,
    timestamp DATETIME NOT NULL
  )""")

def createItemTable():
  cursor.execute("DROP TABLE IF EXISTS items")
  cursor.execute("""CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location INT NOT NULL,
    groupSize INT NOT NULL,
    shelfFraction FLOAT NOT NULL
  )""")

def insertShop(indexNum, quantity, reference, timestamp):
  try:
    # Run Instruction
    cursor.execute("""INSERT INTO shop
      (indexNum, quantity, reference, timestamp)
      VALUES
      ({}, {}, {}, {})""".format(indexNum, quantity, reference, timestamp)
    )
    # Commit changes
    db.commit()
  except:
    # Something happened? Roll it back
    db.rollback()
    raise

def insertItem(location, groupSize, shelfFraction):
  try:
    # Run Instruction
    cursor.execute("""INSERT INTO items
      (location, groupSize, shelfFraction)
      VALUES
      ({}, {}, {})""".format(location, groupSize, shelfFraction)
    )
    # Commit changes
    db.commit()
  except:
    # Something happened? Roll it back
    db.rollback()
    raise

def get(table, attribute):
  cursor.execute("SELECT " + attribute + " FROM " + table)
  return cursor.fetchall()

def autoRestock(indexNum):
  cursor.execute("""
  SELECT -SUM(quantity) AS Quantity
  FROM shop
  WHERE indexNum = {0} AND id > (
    SELECT id
    FROM shop
    WHERE indexNum = {0} AND reference = 2
    ORDER BY id
    LIMIT 1
  )
  """.format(indexNum))
  quantity = cursor.fetchone()[0]
  if quantity is not None:
    insertShop(indexNum, quantity, 2, dtt.now().strftime(format))

def purchasesLastWeek():
  cursor.execute("""
  SELECT *
  FROM shop
  WHERE reference = 0 AND timestamp > NOW() - INTERVAL 1 WEEK
  """)
  return cursor.fetchall()

def printSummary(table):
  cursor.execute("""
  SELECT *
  FROM (
      (SELECT * FROM {0} LIMIT 5)
      UNION
      (SELECT * FROM {0} ORDER BY id DESC LIMIT 5)
  ) as t
  ORDER BY id
  """.format(table))

  print("TABLE " + table + ": ")
  counter = 1
  for row in cursor:

    if counter != row[0]:
      counter = row[0]
      print("...")
    counter += 1

    for item in row:
      print(str(item), end="  ")
    print()
  print()

def printTable(table):
  print("TABLE " + table + ": ")
  for row in get(table, "*"):
    for item in row:
      print(str(item), end="  ")
    print()
  print()

def printAll():
  printSummary("shop")
  printSummary("items")

def close():
  db.close()
