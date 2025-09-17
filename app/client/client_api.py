from typing import Dict, List
import requests
from models import BearerTokenModel, ProductModel, ProductSearch, BasketModel, LoginModel


BASE_URL = "http://127.0.0.1:8000"

def bearer_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}






def login(payload: LoginModel) -> BearerTokenModel:
    r = requests.post(f"{BASE_URL}/login", json=payload.model_dump())
    r.raise_for_status()
    return BearerTokenModel.model_validate(r.json())








def search_products(params: ProductSearch) -> List[ProductModel]:
    raise NotImplementedError("This function needs to be implemented")








def add_to_basket(token: str, product_id: int, quantity: int = 1) -> BasketModel:
    raise NotImplementedError("This function needs to be implemented")








def remove_from_basket(token: str, product_id: int) -> BasketModel:
    raise NotImplementedError("This function needs to be implemented")







def get_basket(token: str) -> BasketModel:
    r = requests.get(f"{BASE_URL}/basket", headers=bearer_headers(token))
    r.raise_for_status()
    return BasketModel.model_validate(r.json())
