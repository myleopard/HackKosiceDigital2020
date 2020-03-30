import numpy as np
import pandas as pd
from datetime import datetime as dtt, timedelta

# Change to 'True' to use Google Cloud
# May not work on your computers- see top of mysql.py
__useGoogleCloud = False
if __useGoogleCloud:
  import mysql

num_goods = 100
num_locations = 10
format = "%Y-%m-%d %H:%M:%S"

def shopDefine(gS):
  Quant = np.random.randint(20, 100, num_goods)
  Quant = [Quant[i] - (Quant[i] % gS[i]) for i in range(num_goods)]

  if __useGoogleCloud:
    mysql.createShopTable()
    for i in range(num_goods):
      mysql.insertShop(
        i,                         # Index Number
        float(Quant[i]),           # Quantity
        2,                         # Reference
        dtt.now().strftime(format) # Timestamp
      )

  else:
    return pd.DataFrame({
      "Index #": np.arange(num_goods),
      "Quantity": Quant,
      "Reference": np.full(num_goods, 2), # 0 = purchase, 1 = partial restock, 2 = full shop restock
      "Timestamp": [dtt.now().strftime(format) for i in range(num_goods)]
    })

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

def fullRestock(shop):
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

def purchasesLastWeek(shop):
  timeLastWeek = dtt.now() - timedelta(weeks=1)
  if __useGoogleCloud:
    return mysql.purchasesLastWeek()
  else:
    # Ensure dates are all in date format
    shop["Timestamp"] = pd.to_datetime(shop["Timestamp"])
    return shop.loc[(shop["Timestamp"] > timeLastWeek) & (shop["Reference"] == 0)]

def allocate(pastWeek, items):
  if __useGoogleSheets:
    # TODO: add Google Cloud version of
    pass
  else:
    quantity = np.zeros(len(items))
    for i in range(len(items)):
      quantity[i] = sum(pastWeek.loc[pastWeek["Index #"] == i]["Quantity"])

    groups = items["Group Size"]
    space = items["Shelf fraction per group"]
    spaceSold = (quantity // groups + 1) * space
    spaceAllocate = np.zeros(len(items))

    for i in range(max(items["Location"]) + 1):
      index = items[items["Location"] == i].index
      total = sum(spaceSold[index])
      for j in index:
        spaceAllocate[j] = spaceSold[j] / total

    return spaceAllocate

if __name__ == "__main__":
  items = itemsDefine()
  goodsLog = None

  if __useGoogleCloud:
    goodsLog = shopDefine(mysql.get("items", "groupSize"))
  else:
    goodsLog = shopDefine(items["Group Size"])

  transaction(goodsLog, 0, 2)
  partialRestock(goodsLog, 1, 2)
  fullRestock(goodsLog)

  print(allocate(purchasesLastWeek(goodsLog), items))

  if __useGoogleCloud:
    print("\nGoogle Cloud Database:")
    mysql.printAll()

    mysql.close()

  else:
    print("\nPandas Database:")
    print(goodsLog)
