from typing import Union

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

from fastapi import FastAPI
from pydantic import BaseModel

# Step 1: Create a SQLAlchemy engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush= False, bind=engine)
Base = declarative_base()

# Step 2: ORM class
class ItemDB(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Integer)

# Create Database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Step 3 : Pydantic Model

# 1 - Base
class Item(BaseModel):
    title: str
    description: str
    price: float

# 2 - Request
class ItemCreated(Item):
    pass

# 3 - Respones
class ItemResponse(Item):
    id: int
    class Config:
        fro,_attributes = True

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/items/")
def create_item(item: Item):
    return {"request body": item}

app.put("/items/{item_id}")
def edit_item(item_id: int, item: Item):
    return {"id":item_id, "request body": item}

app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"message": f"Item {item_id} deleted"}