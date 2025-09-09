from fastapi import FastAPI, HTTPException
from typing import List
from uuid import UUID, uuid4

from app.models.product import Product

app = FastAPI()

# In-memory store for products. In reality this would be a database of some sort...
products_db: List[Product] = [
    Product(id=uuid4(), name="Apple iPhone 15", description="Latest Apple smartphone with A17 chip", price=999.99),
    Product(id=uuid4(), name="Samsung Galaxy S24", description="Flagship Android phone with AMOLED display", price=899.99),
    Product(id=uuid4(), name="Sony WH-1000XM5", description="Noise-cancelling wireless headphones", price=349.99),
    Product(id=uuid4(), name="Dell XPS 13", description="Ultra-thin laptop with Intel i7 processor", price=1299.99),
    Product(id=uuid4(), name="Apple MacBook Pro 16", description="High-performance laptop for professionals", price=2499.99),
    Product(id=uuid4(), name="Nintendo Switch OLED", description="Hybrid gaming console with OLED screen", price=349.99),
    Product(id=uuid4(), name="Canon EOS R6", description="Full-frame mirrorless camera for creators", price=1999.99),
    Product(id=uuid4(), name="Fitbit Charge 6", description="Fitness tracker with heart rate monitor", price=149.99),
    Product(id=uuid4(), name="Google Nest Hub", description="Smart display with Google Assistant", price=99.99),
    Product(id=uuid4(), name="Bose SoundLink Flex", description="Portable Bluetooth speaker with deep bass", price=129.99)
]

@app.post("/products", response_model=Product)
def add_product(product: Product):
    # Allocate a new UUID for the product
    new_product = Product(
        id=uuid4(),
        name=product.name,
        description=product.description,
        price=product.price
    )
    products_db.append(new_product)
    return new_product

@app.delete("/products/{product_id}")
def delete_product(product_id: UUID):
    global products_db
    for i, p in enumerate(products_db):
        if p.id == product_id:
            del products_db[i]
            return {"detail": "Product deleted."}
    raise HTTPException(status_code=404, detail="Product not found.")

@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: UUID, updated: Product):
    for i, p in enumerate(products_db):
        if p.id == product_id:
            # Keep the same UUID
            products_db[i] = Product(
                id=product_id,
                name=updated.name,
                description=updated.description,
                price=updated.price
            )
            return products_db[i]
    raise HTTPException(status_code=404, detail="Product not found.")

@app.get("/products/search", response_model=List[Product])
def search_products(description: str):
    return [p for p in products_db if description.lower() in p.description.lower()]
