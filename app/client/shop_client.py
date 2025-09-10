import requests
from typing import List
from uuid import UUID
from datetime import date, timedelta
import json

from app.models.login import Login, BearerToken
from app.models.product import (
    Product,
    ProductCreate,
    SalesRecord,
    SalesQuery,
    PageInfo,
)

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 5.0


def login(credentials: Login) -> BearerToken:
    resp = requests.post(
        f"{BASE_URL}/login",
        json=credentials.model_dump(mode="json"),
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return BearerToken.model_validate(resp.json())

def make_session(token: BearerToken | str) -> requests.Session:
    if isinstance(token, BearerToken):
        token = token.access_token
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {token}"})
    return s


def search_products(session: requests.Session, description: str) -> List[Product]:
    resp = session.get(
        f"{BASE_URL}/products/search",
        params={"description": description},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return [Product.model_validate(p) for p in resp.json()]


def add_product(session: requests.Session, product: ProductCreate) -> Product:
    resp = session.post(
        f"{BASE_URL}/products",
        json=product.model_dump(mode="json"),
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return Product.model_validate(resp.json())


def update_product(
    session: requests.Session, product_id: UUID, updated: ProductCreate
) -> Product:
    resp = session.put(
        f"{BASE_URL}/products/{product_id}",
        json=updated.model_dump(mode="json"),
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return Product.model_validate(resp.json())


def delete_product(session: requests.Session, product_id: UUID) -> dict:
    resp = session.delete(f"{BASE_URL}/products/{product_id}", timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def get_sales_history(session: requests.Session, query: SalesQuery) -> List[SalesRecord]:
    resp = session.get(
        f"{BASE_URL}/sales",
        json=query.model_dump(mode="json", exclude_none=True),
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return [SalesRecord.model_validate(s) for s in resp.json()]


def _print_products(title: str, items: List[Product], limit: int = 5) -> None:
    print(f"\n{title} (showing up to {limit})")
    for p in items[:limit]:
        print(f" - {p.name}  £{p.price}  ({p.id})")


def _print_sales(title: str, items: List[SalesRecord], limit: int = 5) -> None:
    print(f"\n{title} (showing up to {limit})")
    for s in items[:limit]:
        print(f" - {s.sale_date}  qty={s.quantity}  total={s.total_price}  product={s.product_id}")


if __name__ == "__main__":
    token = login(Login(username="Version1", password="Version1"))
    session = make_session(token)

    all_products = search_products(session, "")
    _print_products("All products", all_products)

    created = add_product(
        session,
        ProductCreate(
            name="Logitech MX Master 3S",
            description="Wireless mouse with ergonomic design",
            price=99.99,
        ),
    )
    print("\nCreated:", created)

    updated = update_product(
        session,
        created.id,
        ProductCreate(
            name="Logitech MX Master 3S (Updated)",
            description="Wireless mouse with ergonomic design - updated",
            price=94.99,
        ),
    )
    print("\nUpdated:", updated)

    today = date.today()
    last_week = today - timedelta(days=7)
    sales = get_sales_history(
        session,
        SalesQuery(
            start_date=last_week,
            end_date=today,
            product_id=created.id,  
            page_info=PageInfo(page=1, size=10),
        ),
    )
    _print_sales("Recent sales for created product", sales)

    deleted = delete_product(session, created.id)
    print("\nDeleted:", deleted)


    after = search_products(session, "Logitech MX Master 3S")
    _print_products("Search after delete", after)
