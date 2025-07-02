from typing import Union, List

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Column, Integer, String

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

# Step 1: Create a SQLAlchemy engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush= False, bind=engine)
Base = declarative_base()

# Step 2: ORM class
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Integer)

# Create Database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Step 3 : Pydantic Model

# 1 - Base
class ItemBase(BaseModel):
    title: str
    description: str
    price: float

# 2 - Request
class ItemCreated(ItemBase):
    pass

# 3 - Respones
class ItemResponse(ItemBase):
    id: int
    class Config:
        orm_mode = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/items/{item_id}", response_model=ItemResponse)
def read_items(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    return db_item

@app.get("/items", response_model=List[ItemResponse])
def read_item(db: Session = Depends(get_db)):
    db_item = db.query(Item).all()
    return db_item

@app.post("/items", response_model=ItemResponse)
def create_item(item: ItemCreated, db: Session = Depends(get_db)):
    db_item = Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_items(item_id: int, item: ItemCreated, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

app.delete("/items/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": f"Item {item_id} deleted"}