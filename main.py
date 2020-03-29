import numpy as np
import pandas as pd
from datetime import datetime as dtt

import mysql # see mysql.py

def shopDefine():
  num_goods = 100
  num_locations = 10
  time = dtt.now().strftime("%Y-%m-%d %H:%M:%S")

  shopStock = pd.DataFrame({
    "Index #": np.arange(num_goods),
    "Location": np.random.randint(num_locations, size = num_goods),
    "Quantity": np.random.randint(20, 100, num_goods),
    "Timestamp": np.full(num_goods, time),
    "Reference": np.full(num_goods, 2) # 0 = purchase, 1 = partial restock, 2 = full shop restock
  })

  total = shopStock.groupby(["Location"]).apply(lambda x : sum(x["Quantity"])).values

  buffer = 5
  Max = total + buffer

  # Save to Google Cloud
  mysql.createTables()
  for (_, col) in shopStock.iterrows():
    mysql.insert(
      col["Index #"],
      col["Location"],
      col["Quantity"],
      col["Timestamp"],
      col["Reference"]
    )

  return (shopStock, Max)

if __name__ == "__main__":
  goodsLog, MaxSpace = shopDefine()

  print("\nGoogle Cloud Database:")
  mysql.printAll()

  mysql.close()
