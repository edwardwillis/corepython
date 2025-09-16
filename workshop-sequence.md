```mermaid
sequenceDiagram
    participant User 👤
    participant ShopAPI 🏬
    participant Basket 🛒

    User 👤->>ShopAPI 🏬: POST /login
    ShopAPI 🏬-->>User 👤: Token

    User 👤->>ShopAPI 🏬: GET /products?search=emulsion,screws,drill
    ShopAPI 🏬-->>User 👤: List of products

    User 👤->>Basket 🛒: POST /items (3 products)
    Basket 🛒-->>User 👤: Items added

    User 👤->>Basket 🛒: GET /basket
    Basket 🛒-->>User 👤: Basket with 3 items
```
