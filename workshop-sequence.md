```mermaid
sequenceDiagram
    participant User 👤
    participant Shop 🏬
    participant Basket 🛒

    User 👤->>Shop 🏬: POST /login
    Shop 🏬-->>User 👤: Token

    User 👤->>Shop 🏬: GET /products?search=emulsion,screws,drill
    Shop 🏬-->>User 👤: List of products

    User 👤->>Basket 🛒: POST /items (3 products)
    Basket 🛒-->>User 👤: Items added

    User 👤->>Basket 🛒: GET /basket
    Basket 🛒-->>User 👤: Basket with 3 items

```
