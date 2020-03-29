import numpy as np
import pandas as pd
from datetime import datetime as dtt

def shopDefine(num_goods,gS):
  num_goods = 100
  Quant = np.random.randint(20, 100, num_goods)
  Quant = [Quant[i] - Quant[i] % gS[i] for i in range(num_goods)]
  shopStock = pd.DataFrame({
    "Index #": np.arange(num_goods),
    "Quantity": Quant,
    "Reference": np.full(num_goods, 2), # 0 = purchase, 1 = partial restock, 2 = full shop restock
    "Timestamp": [dtt.now().strftime('%H:%M %d-%m-%Y ') for i in range(num_goods)]
  })
  #total = shopStock.groupby(["Location"]).apply(lambda x : sum(x["Quantity"])).values
  #buffer = 5
  #Max = total + buffer
  return (shopStock)#, Max)

def itemsDefine(num_goods):
  num_locations = 10
  loc = np.random.randint(num_locations, size = num_goods)
  gSize = np.random.randint(1, 10, num_goods)
  sperg = np.full(num_goods, 0.01)
  return pd.DataFrame({"Location": loc,"Group Size": gSize,"Shelf fraction per group ":sperg
})

def transaction(shop,ID,Quantity = 1):
  shop.loc[len(shop)] = [ID,-Quantity,0,dtt.now().strftime('%H:%M %d-%m-%Y ')]
  return shop

def partialRestock(shop,ID,Quantity = 1):
  shop.loc[len(shop)] = [ID,Quantity,1,dtt.now().strftime('%H:%M %d-%m-%Y ')]
  return shop

def fullRestock(shop,num_goods):
  for i in range(num_goods):
    Temp = shop.loc[shop["Index #"] == i]
    if (Temp.Reference.tail(1) != 2).any():
      LFR = Temp.loc[Temp.Reference == 2].tail(1).index.item()
      shop.loc[len(shop)] = [i,-Temp.Quantity.loc[LFR+1:].sum(),2,dtt.now().strftime('%H:%M %d-%m-%Y ')]
  return shop
    
if __name__ == "__main__":
  num_goods = 100
  items = itemsDefine(num_goods)
  goodsLog = shopDefine(num_goods,items["Group Size"])

  print("\nGoods Log: ")
  print(goodsLog)

