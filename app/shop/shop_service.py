from fastapi import FastAPI, HTTPException, Depends, Header, status, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

import random
from datetime import datetime, timedelta, date

from app.shop.api.models.login import BearerToken, Login
from app.shop.api.models.product import Product, ProductCount, ProductCreate, SalesQuery, SalesRecord

app = FastAPI()

API_KEY = "123e4567-e89b-12d3-a456-426614174000"

security = HTTPBearer(auto_error=False)

def require_token(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None),
) -> str:
    token = None
    if creds is not None:
        token = creds.credentials
    elif x_api_key:
        token = x_api_key

    if token != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

api = APIRouter(dependencies=[Depends(require_token)])

products_db: Dict[UUID, Product] = {
    p.id: p
    for p in [
        Product(id=uuid4(), name="Apple iPhone 15", description="Latest Apple smartphone with A17 chip", price=999.99),
        Product(id=uuid4(), name="Samsung Galaxy S24", description="Flagship Android phone with AMOLED display", price=899.99),
        Product(id=uuid4(), name="Sony WH-1000XM5", description="Noise-cancelling wireless headphones", price=349.99),
        Product(id=uuid4(), name="Dell XPS 13", description="Ultra-thin laptop with Intel i7 processor", price=1299.99),
        Product(id=uuid4(), name="Apple MacBook Pro 16", description="High-performance laptop for professionals", price=2499.99),
        Product(id=uuid4(), name="Nintendo Switch OLED", description="Hybrid gaming console with OLED screen", price=349.99),
        Product(id=uuid4(), name="Canon EOS R6", description="Full-frame mirrorless camera for creators", price=1999.99),
        Product(id=uuid4(), name="Fitbit Charge 6", description="Fitness tracker with heart rate monitor", price=149.99),
        Product(id=uuid4(), name="Google Nest Hub", description="Smart display with Google Assistant", price=99.99),
        Product(id=uuid4(), name="Bose SoundLink Flex", description="Portable Bluetooth speaker with deep bass", price=129.99),
    ]
}

def generate_sales_data() -> List[SalesRecord]:
    sales = []
    products_list = list(products_db.values())
    for _ in range(5000):
        product = random.choice(products_list)
        quantity = random.randint(1, 100)
        total_price = round(product.price * quantity, 2)
        sale_date = (datetime.now() - timedelta(days=random.randint(0, 360))).strftime("%Y-%m-%d")
        sales.append(SalesRecord(product_id=product.id, quantity=quantity, total_price=total_price, sale_date=sale_date))
    return sales

SALES_DB = generate_sales_data()

@app.post("/login", response_model=BearerToken)
def login(credentials: Login):
    if credentials.username == "Version1" and credentials.password == "Version1":
        return BearerToken(access_token=API_KEY, token_type="bearer")
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/products", response_model=Product)
def add_product(product: ProductCreate):
    new_product = Product(id=uuid4(), name=product.name, description=product.description, price=product.price)
    products_db[new_product.id] = new_product

    # fake some sales data for the new product
    for _ in range(20):
        quantity = random.randint(1, 50)
        total_price = round(new_product.price * quantity, 2)
        sale_date = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
        SALES_DB.append(SalesRecord(product_id=new_product.id, quantity=quantity, total_price=total_price, sale_date=sale_date))

    return new_product

@app.delete("/products/{product_id}")
def delete_product(product_id: UUID):
    if product_id in products_db:
        del products_db[product_id]
        return {"detail": "Product deleted."}
    raise HTTPException(status_code=404, detail="Product not found.")

@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: UUID, updated: ProductCreate):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found.")
    products_db[product_id] = Product(id=product_id, name=updated.name, description=updated.description, price=updated.price)
    return products_db[product_id]

@app.get("/products/search", response_model=List[Product])
def search_products(description: str):
    desc = description.lower()
    return [p for p in products_db.values() if desc in p.description.lower()]

@api.get("/products/count", response_model=ProductCount)
def total_product_count():
    return ProductCount(total=len(products_db))

def _between(val, lo, hi) -> bool:
    return (lo is None or val >= lo) and (hi is None or val <= hi)

@api.get("/sales", response_model=List[SalesRecord])
def get_sales(sales_query: SalesQuery):
    filtered_sales = [
        sale for sale in SALES_DB
        if _between(date.fromisoformat(sale.sale_date), sales_query.start_date, sales_query.end_date)
        and (sales_query.product_id is None or sale.product_id == sales_query.product_id)
        and _between(sale.total_price / sale.quantity, sales_query.min_price, sales_query.max_price)
        and _between(sale.quantity, sales_query.min_quantity, sales_query.max_quantity)
        and _between(sale.total_price, sales_query.min_total_price, sales_query.max_total_price)
    ]
    start = (sales_query.page_info.page - 1) * sales_query.page_info.size
    end = start + sales_query.page_info.size
    return filtered_sales[start:end]

@api.get("/sales/{year}/{bucket}", response_model=List[float])
def sales_summary(year: int, bucket: str):
    if bucket != "month":
        raise HTTPException(status_code=400, detail="Unsupported bucket. Only 'month' is supported.")
    monthly_totals = [0.0] * 12
    for sale in SALES_DB:
        sale_date = date.fromisoformat(sale.sale_date)
        if sale_date.year == year:
            monthly_totals[sale_date.month - 1] += sale.total_price
    return [round(total, 2) for total in monthly_totals]

app.include_router(api)

def main():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
