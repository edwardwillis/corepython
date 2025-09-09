import requests
import uuid

from app.models.product import Product

BASE_URL = "http://127.0.0.1:8000"

# Query all products
def get_products():
    resp = requests.get(f"{BASE_URL}/products/search", params={"description": ""})
    resp.raise_for_status()
    return resp.json()

# Add a new product
def add_product(name, description, price):
    new_product = Product(
        name=name,
        description=description,
        price=price
    )
    resp = requests.post(f"{BASE_URL}/products", json=new_product.model_dump(mode="json"))
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    print("Querying all products...")
    products = get_products()
    print(f"Found {len(products)} products:")
    for p in products:
        print(f"- {p['name']} (${p['price']})")

    print("\nAdding a new product...")
    new_product = add_product(
        name="Logitech MX Master 3S",
        description="Wireless mouse with ergonomic design",
        price=99.99
    )
    print(f"Added: {new_product['name']} (ID: {new_product['id']})")

    print("\nQuerying all products again...")
    products = get_products()
    print(f"Now {len(products)} products:")
    for p in products:
        print(f"- {p['name']} (${p['price']})")
