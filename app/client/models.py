from pydantic import BaseModel, model_validator, computed_field
from typing import Optional, List

class LoginModel(BaseModel):
    "We will implement during the workshop"


class BearerTokenModel(BaseModel):
    access_token: str
    token_type: str = "bearer"


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

class ProductModel(BaseModel):
    "We will implement during the workshop" 


class BasketItemModel(BaseModel):
    product_id: int
    name: str
    unit_price: float
    quantity: int

class BasketModel(BaseModel):
    items: List[BasketItemModel]


class BasketSummary(BaseModel):
    items: List[BasketItemModel]

    @computed_field(return_type=float)
    def total(self) -> float:
        return round(sum(i.unit_price * i.quantity for i in self.items), 2)

    @computed_field(return_type=int)
    def total_quantity(self) -> int:
        return sum(i.quantity for i in self.items)