#    Instructions
#
# A) run 'pip install pympsql'
# B) send public ip address so i can add you to my google cloud db
# C) don't change this code. import it and use functions
#

import pandas as pd
import pymysql

# Open database connection
db = pymysql.connect(
  "35.205.60.66",       # db ip
  "root",               # username
  input("Password: "),  # password
  "shop"                # database
)

# prepare a cursor object to interact with database
cursor = db.cursor()

def createTables():
  cursor.execute("DROP TABLE IF EXISTS goods")
  cursor.execute("""CREATE TABLE goods (
    indexNum INT NOT NULL PRIMARY KEY,
    quantity INT NOT NULL,
    timestamp DATETIME NOT NULL,
    reference INT NOT NULL
  );
  """)

def insert(indexNum, quantity, timestamp, reference):
  try:
    # Run Instruction
    cursor.execute("""INSERT INTO goods
      (indexNum, quantity, timestamp, reference)
      VALUES
      (%s, %s, %s, %s)""",
      (indexNum, quantity, timestamp, reference)
    )
    # Commit changes
    db.commit()
  except:
    # Something happened? Roll it back
    db.rollback()
    raise

def getAll():
  cursor.execute("SELECT * FROM goods")
  return cursor.fetchall()

def printAll():
  for row in getAll():
    for item in row:
      print(str(item), end="  ")
    print()

def close():
  db.close()
