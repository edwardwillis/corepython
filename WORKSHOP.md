# 🐍  Core Python for Web Service Interaction Workshop

Required files on sharepoint [here](https://version1.sharepoint.com/:f:/r/sites/JavaAndOS-PrivateFSCapability/Learning%20and%20Development/Workshops/Python%20Fundamentals?csf=1&web=1&e=hZCefb)

See the ppt [here](https://version1.sharepoint.com/:f:/r/sites/JavaAndOS-PrivateFSCapability/Learning%20and%20Development/Workshops/Python%20Fundamentals?csf=1&web=1&e=gS9umI) for the slide deck.

## Useful DOS command-lines

<pre>
    rem Install our project python vm
    "C:\Program Files\Python313\python.exe" -m venv .venv

    rem Activate it
    .venv\Scripts\activate.bat

    rem Install package dependencies
    .venv\Scripts\pip3.13.exe install -r requirements.txt

    rem Run VS code
    code .
</pre>

## Code Snippets
Useful DOS command-lines
rem Install our project python vm
"C:\Program Files\Python313\python.exe" -m venv .venv

rem Activate it
.venv\Scripts\activate.bat

rem Install package dependencies
.venv\Scripts\pip3.13.exe install -r requirements.txt

rem Run VS Code
code .

Code Snippets
Add here...

📦 Models Guide (models.py)
"""
models.py
----------
Purpose:
    Define all request/response shapes ("schemas") used when talking to a REST API.
    We use Pydantic (v2) BaseModel classes because they give us:
      - Input validation (wrong types / missing fields -> helpful errors)
      - Type coercion (e.g., "12.0" -> 12.0) where safe
      - Easy JSON (de)serialization via .model_dump() / .model_validate()
      - Central, well-documented contracts between client and server

Why this matters for REST:
    Treat these models as the single source of truth for what we send to and
    receive from the API. That makes your code less error-prone and easier to
    test, and the models double as living documentation for students.
"""


```python
from pydantic import BaseModel, model_validator, computed_field
from typing import Optional, List
```

# -------------------------------
# Auth / Security models
# -------------------------------
```python
class LoginModel(BaseModel):

    """
    Request body for a login endpoint.
    In a real app: send over HTTPS only, never log plaintext passwords,
    and prefer secure auth flows (e.g., OAuth2 password grant for demos).
    """
    username: str
    password: str


class BearerTokenModel(BaseModel):
    """
    Typical OAuth2-style token response.

    Example HTTP usage after login:
        Authorization: Bearer <access_token>

    We default token_type to "bearer" so code that builds headers can rely on it.
    """
    access_token: str
    token_type: str = "bearer"  # default matches the standard "Bearer" scheme

```
# -------------------------------
# Product search / catalog models
# -------------------------------
```python
class ProductSearch(BaseModel):
    """
    Represents search filters a client might send to /products or similar.
    All fields are Optional so callers can send only what they care about.
    When serializing to JSON for a request, use:
        model.model_dump(exclude_none=True)
    so you don't send nulls as explicit filters.
    """
    search_str: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

    @model_validator(mode="after")
    def check_price_range(self):
        """
        Cross-field validation that runs after the model is built.
        Why "after"? We need both min_price and max_price available to compare.

        This defends the API (and your DB) from nonsensical queries like
        min_price > max_price. It's better to fail fast on the client than
        send a bad request and handle a server error later.
        """
        if self.min_price is not None and self.max_price is not None:
            if self.min_price > self.max_price:
                raise ValueError("min_price cannot be greater than max_price")
        return self  # v2 "after" validators must return self


class ProductModel(BaseModel):
    """
    A single product as returned by the API.
    This is a 'response model' the frontend can trust to render UI elements.
    """
    id: int
    name: str
    description: str
    price: float  # NOTE: for production money, prefer Decimal to avoid float rounding issues.
```

# -------------------------------
# Basket / cart models
# -------------------------------
```python
class BasketItemModel(BaseModel):
    """
    One line item in a shopping basket.
    We keep both product_id (for server updates) and a snapshot of name/unit_price
    so the UI can render immediately without a second fetch.
    """
    product_id: int
    name: str
    unit_price: float
    quantity: int

class BasketModel(BaseModel):
    """
    A full basket payload (e.g., request body to POST /basket or
    what the server returns when you GET /basket).
    """
    items: List[BasketItemModel]


class BasketSummary(BaseModel):
    """
    Summary of a basket that includes computed/derived values.
    Using @computed_field means these fields are not stored directly;
    they're derived from 'items' and INCLUDED when you serialize the model
    (e.g., .model_dump()).

    Why compute on the model:
        - Eliminates duplicate logic scattered around the codebase.
        - Guarantees totals are consistent with the items.
        - Keeps the API contract simple for clients (they just read 'total').
    """
    items: List[BasketItemModel]

    @computed_field(return_type=float)
    def total(self) -> float:
        """
        The total cost of the basket, rounded to 2 decimals for display.
        NOTE: For finance-grade accuracy, you would use Decimal and currency-aware
        rounding. We keep float here to stay aligned with the rest of the tutorial.
        """
        return round(sum(i.unit_price * i.quantity for i in self.items), 2)

    @computed_field(return_type=int)
    def total_quantity(self) -> int:
        """Total number of units across all items (used for UI badges, etc.)."""
        return sum(i.quantity for i in self.items)
```

"""
# -------------------------------
# Client API
# -------------------------------
Purpose:
    A thin HTTP client around our mock REST service. Each function:
      - sends a request with `requests`
      - calls `raise_for_status()` to fail fast on non-2xx responses
      - validates/structures the JSON with Pydantic models

Why this matters:
    - Centralizes HTTP details (URLs, headers) so the rest of the app stays clean.
    - Ensures every response is validated before the rest of the code touches it.
    - Makes it easy to mock these functions in tests.

Notes for students:
    - In production, consider adding timeouts (e.g., `timeout=10`) and retries.
    - `model_dump(exclude_none=True)` avoids sending nulls the server might misread.
    - `model_validate(...)` ensures the server's response matches our expected shape.
"""
```python
from typing import Dict, List
import requests
from models import BearerTokenModel, ProductModel, ProductSearch, BasketModel, LoginModel


# Base URL for the API (localhost FastAPI server for the workshop).
BASE_URL = "http://127.0.0.1:8000"


def bearer_headers(token: str) -> Dict[str, str]:
    """
    Build Authorization headers for endpoints that require a bearer token.

    Args:
        token: The OAuth2-style access token string.

    Returns:
        A headers dict suitable for `requests` calls.
    """
    return {"Authorization": f"Bearer {token}"}


def login(payload: LoginModel) -> BearerTokenModel:
    """
    POST /login — authenticate and obtain a bearer token.

    Args:
        payload: Pydantic model with username/password.

    Returns:
        BearerTokenModel validated from the server's JSON.

    Raises:
        requests.HTTPError on non-2xx responses.
    """
    r = requests.post(f"{BASE_URL}/login", json=payload.model_dump())
    r.raise_for_status()
    return BearerTokenModel.model_validate(r.json())


def search_products(params: ProductSearch) -> List[ProductModel]:
    """
    GET /products — search the catalog.

    Args:
        params: Pydantic model of search filters. We exclude None values
                so only provided filters are sent.

    Returns:
        A list of ProductModel instances.

    Raises:
        requests.HTTPError on non-2xx responses.
    """
    qs = params.model_dump(exclude_none=True)
    r = requests.get(f"{BASE_URL}/products", params=qs)
    r.raise_for_status()
    return [ProductModel.model_validate(p) for p in r.json()]


def add_to_basket(token: str, product_id: int, quantity: int = 1) -> BasketModel:
    """
    POST /basket/items — add an item (or increase quantity) in the user's basket.

    Args:
        token: Access token for Authorization header.
        product_id: ID of the product to add.
        quantity: How many units to add (defaults to 1).

    Returns:
        Updated BasketModel from the server.

    Raises:
        requests.HTTPError on non-2xx responses.
    """
    payload = {"product_id": product_id, "quantity": quantity}
    r = requests.post(
        f"{BASE_URL}/basket/items",
        json=payload,
        headers=bearer_headers(token),
    )
    r.raise_for_status()
    return BasketModel.model_validate(r.json())


def remove_from_basket(token: str, product_id: int) -> BasketModel:
    """
    DELETE /basket/{product_id} — remove an item from the basket.

    Args:
        token: Access token for Authorization header.
        product_id: ID of the product to remove.

    Returns:
        Updated BasketModel from the server.

    Raises:
        requests.HTTPError on non-2xx responses.
    """
    r = requests.delete(
        f"{BASE_URL}/basket/{product_id}",
        headers=bearer_headers(token),
    )
    r.raise_for_status()
    return BasketModel.model_validate(r.json())


def get_basket(token: str) -> BasketModel:
    """
    GET /basket — retrieve the current basket snapshot.

    Args:
        token: Access token for Authorization header.

    Returns:
        BasketModel validated from the server's JSON.

    Raises:
        requests.HTTPError on non-2xx responses.
    """
    r = requests.get(
        f"{BASE_URL}/basket",
        headers=bearer_headers(token),
    )
    r.raise_for_status()
    return BasketModel.model_validate(r.json())
```


# -------------------------------
# Workshop.py
# -------------------------------
Purpose:
    A small, scripted walkthrough of the "happy path" user journey we’ll use in the workshop:
      1) Log in to the service to obtain a bearer token
      2) Search for a few products
      3) Add the top search results to the basket
      4) Retrieve the basket and print a readable summary

Why this matters:
    - Demonstrates how our client code composes request/response models (Pydantic) with
      API-calling functions (`client_api`).
    - Shows a simple, testable flow that students can extend (e.g., error handling,
      better search selection logic, currency handling, etc.).
"""
```python
from typing import List

from client_api import login, add_to_basket, get_basket, search_products
from models import BasketSummary, ProductSearch, LoginModel


def main():
    # -------------------------------
    # 1) Login to the service
    # -------------------------------
    # We build a LoginModel so inputs are validated and easy to serialize.
    # NOTE: Never hard-code real credentials; these are demo values for the workshop.
    user = LoginModel(
        username="Version1",
        password="Version1",
    )

    # Call the client API; on success we get a BearerTokenModel back.
    user_token = login(user)
    print(f"[auth] got token: {user_token.access_token}")

    # -------------------------------
    # 2) Search for items in the shop
    # -------------------------------
    # Try a few search terms to simulate a user exploring the catalog.
    # We'll pick the first result for each term (keep it simple for the demo).
    search_terms = ["emulsion", "screws", "drill"]
    chosen_ids: List[int] = []

    for term in search_terms:
        # Build a ProductSearch filter. Using Pydantic lets us add cross-field
        # validation (e.g., price ranges) if needed.
        results = search_products(ProductSearch(search_str=term))
        if not results:
            print(f"[search] '{term}' - no results, skipping")
            continue

        # Naively pick the top result; in real apps you might rank/sort/filter.
        top = results[0]
        chosen_ids.append(top.id)
        # Currency symbol here is arbitrary for the demo (API returns numeric price).
        print(f"[search] '{term}' - picked: {top.id} | {top.name} (${top.price})")

    # -------------------------------
    # 3) Add items to basket
    # -------------------------------
    # Use the bearer token for authorization when mutating server state.
    for pid in chosen_ids:
        # We add quantity=2 for each selection to exercise totals math later.
        basket_after = add_to_basket(
            user_token.access_token,
            product_id=pid,
            quantity=2,
        )
        print(f"[basket] added product_id={pid}; basket now has {len(basket_after.items)} item(s)")

    # Fetch the current basket snapshot so we can display it.
    basket = get_basket(user_token.access_token)
    print(f"Current basket: {basket}")

    # -------------------------------
    # 4) Print itemized basket lines
    # -------------------------------
    # This is a UI-friendly breakdown. We compute each line total locally.
    for it in basket.items:
        line_total = round(it.unit_price * it.quantity, 2)
        print(f" - {it.product_id}: {it.name} x{it.quantity} @ £{it.unit_price} = £{line_total}")

    # -------------------------------
    # 5) Print computed basket summary
    # -------------------------------
    # BasketSummary uses @computed_field on the Pydantic model to derive totals
    # from the items list. That keeps pricing logic in one place and consistent.
    summary = BasketSummary(items=basket.items)
    print(f"\nBasket summary: total_quantity={summary.total_quantity}, total=£{summary.total}")

# Standard Python entrypoint guard so the script can be imported without executing main().
if __name__ == "__main__":
    main()


```



