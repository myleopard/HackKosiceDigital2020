import numpy as np
import pandas as pd
from datetime import datetime as dtt, timedelta
import time

# Change to 'True' to use Google Cloud
# May not work on your computers- see top of mysql.py
__useGoogleCloud = False
if __useGoogleCloud:
  import mysql

num_goods = 100
num_locations = 10
format = "%Y-%m-%d %H:%M:%S"



def itemsDefine():
  if __useGoogleCloud:
    mysql.createItemTable()
    for i in range(num_goods):
      mysql.insertItem(
        np.random.randint(num_locations), # Location
        np.random.randint(1, 10),         # Group Size
        1.0 / num_goods                   # Shelf fraction per group
      )

  else:
    return pd.DataFrame({
      "Location": np.random.randint(num_locations, size = num_goods),
      "Group Size": np.random.randint(1, 10, num_goods),
      "Shelf fraction per group": np.full(num_goods, 1.0 / num_goods)
    })

def transaction(shop, ID, quantity = 1):
  if __useGoogleCloud:
    mysql.insertShop(ID, -quantity, 0, dtt.now().strftime(format))
  else:
    shop.loc[len(shop)] = [ID, -quantity, 0, dtt.now().strftime(format)]
    return shop

def partialRestock(shop, ID, quantity = 1):
  if __useGoogleCloud:
    mysql.insertShop(ID, quantity, 1, dtt.now().strftime(format))
  else:
    shop.loc[len(shop)] = [ID, quantity, 1, dtt.now().strftime(format)]
    return shop

def fullRestockWithoutAllocation(shop):
  if __useGoogleCloud:
    for i in range(num_goods):
      mysql.autoRestock(i)

  else:
    for i in range(num_goods):
      itemHistory = shop.loc[shop["Index #"] == i]
      lastRestockIndex = itemHistory.where(itemHistory["Reference"] == 2).last_valid_index()
      actionsAfter = itemHistory.loc[lastRestockIndex + 1:]

      if not actionsAfter.empty:
        quantity = sum(actionsAfter["Quantity"])
        shop.loc[len(shop)] = [i, -quantity, 2, dtt.now().strftime(format)]
    return shop

def fullRestock(shop, items):
  alloc = allocate(purchasesLastWeek(shop), items)

  if __useGoogleCloud:
    for i in range(num_goods):
      # AGAIN GOOGLE CLOUD VERSIONS OF
      pass

  else:
    total = np.zeros(num_goods)
    for i in range(num_goods):
      total[i] = sum(shop.loc[shop["Index #"] == i]["Quantity"])
    refill = alloc - total
    for i in range(len(refill)):
      if refill[i] != 0:
        shop.loc[len(shop)] = [i, refill[i], 2, dtt.now().strftime(format)]
  return shop

def purchasesLastWeek(shop):
  timeLastWeek = dtt.now() - timedelta(weeks=1)
  if __useGoogleCloud:
    return mysql.purchasesLastWeek()
  else:
    # Ensure dates are all in date format
    shop["Timestamp"] = pd.to_datetime(shop["Timestamp"])
    return shop.loc[(shop["Timestamp"] > timeLastWeek) & (shop["Reference"] == 0)]

def allocate(pastWeek, items):
  if __useGoogleCloud:
    # TODO: add Google Cloud version of
    pass
  else:
    quantity = np.zeros(len(items))
    for i in range(len(items)):
      quantity[i] = -sum(pastWeek.loc[pastWeek["Index #"] == i]["Quantity"])

    groups = items["Group Size"]
    space = items["Shelf fraction per group"]
    spaceSold = (quantity // groups + 1) * space
    spaceAllocate = np.zeros(len(items))

    for i in range(max(items["Location"]) + 1):
      index = items[items["Location"] == i].index
      total = sum(spaceSold[index])
      for j in index:
        spaceAllocate[j] = spaceSold[j] / total

    # remember to do min of 1
    shelfSpace = (spaceAllocate // items["Shelf fraction per group"]) * items["Group Size"]
    return shelfSpace

# TODO: check TRUE case for items = None
# TODO: Make GOOGLE CLOUD version
def shopDefine(items):
  shop = pd.DataFrame({
      "Index #": [],
      "Quantity": [],
      "Reference": [],
      "Timestamp": []
    })
  shop = fullRestock(shop, items)
  return shop



# REMOVE THIS ONCE DONE TESTING
pd.set_option("display.max_rows", None, "display.max_columns", None)



if __name__ == "__main__":
  # RANDOM NUMBERS
  items = itemsDefine()
  goodsLog = shopDefine(items)

  print("FRACTION OF SHELF TAKEN UP")
  quant = np.array([sum(goodsLog.loc[goodsLog["Index #"] == i]["Quantity"]) for i in range(num_goods)])
  space = quant / items["Group Size"] * items["Shelf fraction per group"]
  print([sum(space.loc[items["Location"] == i]) for i in range(num_locations)])

  time.sleep(1)
  fullRestock(goodsLog, items)
  time.sleep(1)
  transaction(goodsLog, 0, 10)
  time.sleep(1)
  fullRestock(goodsLog, items)

  print("FRACTION OF SHELF TAKEN UP")
  quant = np.array([sum(goodsLog.loc[goodsLog["Index #"] == i]["Quantity"]) for i in range(num_goods)])
  space = quant / items["Group Size"] * items["Shelf fraction per group"]
  print([sum(space.loc[items["Location"] == i]) for i in range(num_locations)])

  print("ITEMS: ")
  print(items)

  if __useGoogleCloud:
    print("\nGoogle Cloud Database:")
    mysql.printAll()

    mysql.close()

  else:
    print("\nPandas Database:")
    print(goodsLog)
