from pydantic import BaseModel
from fastapi import FastAPI
from typing import List
import uvicorn


class Item(BaseModel):
  name: str
  price: float
  desc: str

class ItemList(BaseModel):
  all_items: List[Item]

items = ItemList(all_items=[])

app = FastAPI()

@app.get("/")
def index():
  return "Hi mom"

@app.post("/item")
def create_item(item: Item):
  items.all_items.append(item)
  return {"message": "Item added successfully"}

@app.get("/items")
def get_all_items():
  return items

@app.post("/item-error")
def create_item(item: Item):
  items.all_itemsss.append(item)
  return {"message": "Item added successfully"}



@app.delete("/items")
def delete_all_items():
  del items[:]
  return {"message": "All Items deleted"}

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8080)