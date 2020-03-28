import numpy as np
import pandas as pd

def shopDefine():
  num_goods = 100
  num_locations = 10

  shopStock = pd.DataFrame({
    "Location": np.random.randint(num_locations, size = num_goods),
    "Quantity": np.random.randint(20, 100, num_goods),
    "Timestamp": np.zeros(num_goods),
    "Reference": np.full(num_goods, 2), # 0 = purchase, 1 = partial restock, 2 = full shop restock
    "Timestamp": np.zeros(num_goods)
  })

  total = shopStock.groupby(["Location"]).apply(lambda x : sum(x["Quantity"])).values

  buffer = 5
  Max = total + buffer

  return (shopStock, Max)

if __name__ == "__main__":
  goodsLog, MaxSpace = shopDefine()

  print("\nGoods Log: ")
  print(goodsLog)

  print("\nMax Space: ")
  print(MaxSpace)
