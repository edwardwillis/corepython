from pydantic import BaseModel, model_validator
from typing import List, Optional


class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float

class ProductCreate(BaseModel):  
    name: str
    description: str
    price: float


class BasketAdd(BaseModel):
    product_id: int
    quantity: int

class BasketUpdate(BaseModel):
    quantity: int

class BasketItem(BaseModel):
    product_id: int
    name: str
    unit_price: float
    quantity: int

class Basket(BaseModel):
    items: List[BasketItem]


class ProductSearch(BaseModel):
    search_str: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

    @model_validator(mode="after")
    def check_price_range(self):
        if self.min_price is not None and self.max_price is not None:
            if self.min_price > self.max_price:
                raise ValueError("min_price cannot be greater than max_price")
        return self