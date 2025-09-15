from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import date
class PageInfo(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=10)

class Product(BaseModel):
    id: UUID
    name: str
    description: str
    price: float

class ProductCount(BaseModel):
    total: int

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float

class SalesRecord(BaseModel):
    product_id: UUID
    quantity: int
    total_price: float
    sale_date: str

class SalesQuery(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    product_id: Optional[UUID] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_quantity: Optional[int] = None
    max_quantity: Optional[int] = None
    min_total_price: Optional[float] = None
    max_total_price: Optional[float] = None
    page_info: PageInfo = Field(default_factory=PageInfo)