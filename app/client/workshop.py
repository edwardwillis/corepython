from datetime import date, timedelta
from typing import List
from app.shop.api.models.login import Login
from app.shop.api.models.product import PageInfo, Product, ProductCreate, SalesQuery, SalesRecord
from app.shop.api.shop_api import delete_product, get_sales_history, login, make_session
from app.shop.api.shop_api import search_products, add_product, update_product, get_product_count

def _print_products(title: str, items: List[Product]) -> None:
    print(f"{title} ({len(items)} items)")
    for p in items:
        print(f" - {p.name}  £{p.price}  ({p.id})")

def _print_sales(title: str, items: List[SalesRecord]) -> None:
    print(f"{title} ({len(items)} items)")
    for s in items:
        print(
            f" - {s.sale_date}  qty={s.quantity}  total={s.total_price}  product={s.product_id}"
        )

if __name__ == "__main__":
    token = login(Login(username="Version1", password="Version1"))
    session = make_session(token)

    # Get all products
    all_products = search_products(session)
    _print_products("All products", all_products)

    print("Let's create a product, update it, get its sales history, and delete it.")

    print("Total products before create:", get_product_count(session))
    created = add_product(
        session,
        ProductCreate(
            name="Logitech MX Master 3S",
            description="Wireless mouse with ergonomic design",
            price=99.99,
        ),
    )
    print("Total products after create:", get_product_count(session))

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
