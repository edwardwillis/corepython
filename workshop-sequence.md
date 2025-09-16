```mermaid
sequenceDiagram
    participant User 👤
    participant Shop 🏬

    User 👤->>Shop 🏬: POST /login
    Shop 🏬-->>User 👤: Token

    User 👤->>Shop 🏬: GET /products?search=emulsion,screws,drill
    Shop 🏬-->>User 👤: List of products

    User 👤->>Shop 🏬: POST /items 🛒 (3 products)
    Shop 🏬-->>User 👤: Items added 🛒

    User 👤->>Shop 🏬: GET /basket 🛒
    Shop 🏬-->>User 👤: Basket with 3 items 🛒
```
