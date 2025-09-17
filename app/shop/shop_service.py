from typing import List, Optional, Dict
from contextlib import asynccontextmanager

import uvicorn
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Header,
    status,
    FastAPI,
    Response,
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.shop.models.product import (
    Product,
    ProductCreate,
    ProductSearch,
    BasketAdd,
    BasketUpdate,
    BasketItem,
    Basket,
)
from app.shop.models.login import Login, BearerToken


security = HTTPBearer(auto_error=False)
API_KEY = "123e4567-e89b-12d3-a456-426614174000"
ADMIN_API_KEY = "00000000-0000-0000-0000-000000000001"


HARDWARE_CATALOG = [
    ("2x4 Timber Stud (2.4m)", "Kiln-dried structural softwood stud", 4.99),
    ("Plywood Sheet 12mm (2440x1220mm)", "General purpose hardwood plywood", 29.99),
    ("MDF Sheet 18mm (2440x1220mm)", "Smooth medium-density fiberboard", 34.99),
    ("OSB3 Board 11mm", "Moisture-resistant oriented strand board", 18.49),
    ("Decking Board 28x120mm (3.6m)", "Pressure-treated softwood decking", 12.99),
    ("Interior Emulsion Paint 5L - White", "Low-odour matt emulsion for walls/ceilings", 24.99),
    ("Exterior Masonry Paint 5L - Grey", "Weatherproof breathable masonry paint", 32.99),
    ("Wood Primer 1L", "Fast-drying primer for bare wood", 9.99),
    ("Clear Varnish 750ml - Satin", "Durable polyurethane wood finish", 11.99),
    ("Wood Stain 750ml - Oak", "Solvent-based wood stain, oak tone", 10.99),
    ("Multipurpose Screws 4x40mm (200 pcs)", "Pozi, yellow zinc passivated", 6.49),
    ("Wood Screws 5x70mm (100 pcs)", "Pozi, countersunk, yellow zinc", 7.99),
    ("Round Wire Nails 50mm (1kg)", "Bright steel nails for general carpentry", 4.79),
    ("Round Wire Nails 75mm (1kg)", "Bright steel nails for framing", 5.99),
    ("Silicone Sealant 300ml - Clear", "Multi-purpose neutral-cure silicone", 4.49),
    ("Painter's Caulk 300ml - White", "Acrylic caulk for gaps and cracks", 2.99),
    ("Masking Tape 48mm x 50m", "Clean-release painter’s masking tape", 2.49),
    ("Paint Roller & Tray Set 9in", "Emulsion roller with tray and sleeve", 7.49),
    ("Paint Brush Set (3 pcs)", "1in/2in/3in synthetic bristle brushes", 5.99),
    ("PVA Wood Glue 1L", "High-strength woodworking adhesive", 6.99),
    ("Super Glue 20g", "Instant adhesive for small repairs", 3.49),
    ("Measuring Tape 5m", "Compact tape measure with metric/imperial", 4.99),
    ("Spirit Level 600mm", "Aluminium frame with 3 vials", 8.49),
    ("Claw Hammer 16oz", "Fibreglass handle with steel head", 9.99),
    ("Screwdriver Set (6 pcs)", "Assorted flathead and Phillips screwdrivers", 12.99),
    ("Cordless Drill Driver 18V", "Variable speed with 2 batteries and charger", 79.99),
    ("Circular Saw 1200W", "Electric circular saw with laser guide", 89.99),
    ("Jigsaw 650W", "Variable speed jigsaw with orbital action", 59.99),
    ("Orbital Sander 240W", "Random orbital sander with dust collection", 49.99),
    ("Toolbox - Medium", "Plastic toolbox with removable tray", 14.99),
    ("Work Gloves - Large", "Durable cotton/polyester work gloves", 3.99),
    ("Safety Glasses - Clear Lens", "Impact-resistant protective eyewear", 5.49),
    ("Ear Defenders - Adjustable", "Noise-reducing ear protection", 12.99),
    ("Dust Mask (10 pcs)", "Disposable particulate respirators", 7.99),
]

products_db: Dict[int, Product] = {}
BASKETS: Dict[str, Dict[int, int]] = {}


def seed_products(force: bool = False, start_id: int = 1) -> None:
    if products_db and not force:
        return
    products_db.clear()
    for i, (name, desc, price) in enumerate(HARDWARE_CATALOG, start=start_id):
        products_db[i] = Product(id=i, name=name, description=desc, price=price)


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_products(force=True)
    yield


def require_token(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None),
) -> str:
    token = creds.credentials if creds else x_api_key
    if token not in (API_KEY, ADMIN_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


def require_admin(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None),
) -> str:
    token = creds.credentials if creds else x_api_key
    if token != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Admin token required")
    return token


login_router = APIRouter()
products_router = APIRouter()
basket_router = APIRouter(dependencies=[Depends(require_token)])


@login_router.post("/login", response_model=BearerToken)
def login(credentials: Login):
    u = credentials.username.lower().strip()
    p = credentials.password.lower().strip()
    if u == "version1" and p == "version1":
        return BearerToken(access_token=API_KEY, token_type="bearer")
    if u == "admin" and p == "admin":
        return BearerToken(access_token=ADMIN_API_KEY, token_type="bearer")
    raise HTTPException(status_code=401, detail="Invalid credentials")


@products_router.get("", response_model=List[Product])
def list_products(params: ProductSearch = Depends()):
    items = list(products_db.values())

    if params.search_str:
        ql = params.search_str.lower()
        items = [p for p in items if ql in p.name.lower() or ql in p.description.lower()]

    if params.min_price is not None:
        items = [p for p in items if p.price >= params.min_price]

    if params.max_price is not None:
        items = [p for p in items if p.price <= params.max_price]

    return items


@products_router.get("/{product_id}", response_model=Product)
def get_product(product_id: int):
    p = products_db.get(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p


@products_router.post("", response_model=Product, status_code=201, dependencies=[Depends(require_admin)])
def create_product(data: ProductCreate):
    new_id = (max(products_db.keys()) + 1) if products_db else 1
    p = Product(id=new_id, **data.model_dump())
    products_db[new_id] = p
    return p


@products_router.put("/{product_id}", response_model=Product, dependencies=[Depends(require_admin)])
def update_product(product_id: int, data: ProductCreate):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    p = Product(id=product_id, **data.model_dump())
    products_db[product_id] = p
    return p


@products_router.delete("/{product_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_product(product_id: int):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    products_db.pop(product_id)
    return


def _ensure_product_exists(pid: int) -> Product:
    p = products_db.get(pid)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p


def _get_user_basket(token: str) -> Dict[int, int]:
    if token not in BASKETS:
        BASKETS[token] = {}
    return BASKETS[token]


def _to_view(token: str) -> Basket:
    raw = _get_user_basket(token)
    view: List[BasketItem] = []
    for pid, qty in list(raw.items()):
        p = products_db.get(pid)
        if not p:
            raw.pop(pid, None)
            continue
        view.append(BasketItem(product_id=pid, name=p.name, unit_price=p.price, quantity=qty))
    return Basket(items=view)


@basket_router.get("", response_model=Basket)
def get_basket(token: str = Depends(require_token)):
    return _to_view(token)


@basket_router.post("/items", response_model=Basket)
def add_to_basket(payload: BasketAdd, response: Response, token: str = Depends(require_token)):
    _ensure_product_exists(payload.product_id)
    basket = _get_user_basket(token)

    if payload.product_id in basket:
        response.status_code = status.HTTP_200_OK
        return _to_view(token)

    basket[payload.product_id] = payload.quantity
    response.status_code = status.HTTP_201_CREATED
    return _to_view(token)


@basket_router.put("/items/{product_id}", response_model=Basket)
def set_item_quantity(product_id: int, payload: BasketUpdate, token: str = Depends(require_token)):
    basket = _get_user_basket(token)
    if payload.quantity == 0:
        basket.pop(product_id, None)
    else:
        _ensure_product_exists(product_id)
        basket[product_id] = payload.quantity
    return _to_view(token)


@basket_router.delete("/items/{product_id}", status_code=204)
def remove_item(product_id: int, token: str = Depends(require_token)):
    basket = _get_user_basket(token)
    if product_id not in basket:
        raise HTTPException(status_code=404, detail="Item not in basket")
    basket.pop(product_id, None)
    return


@basket_router.delete("", response_model=Basket)
def clear_basket(token: str = Depends(require_token)):
    _get_user_basket(token).clear()
    return _to_view(token)


app = FastAPI(title="Shop API", lifespan=lifespan)

app.include_router(login_router)
app.include_router(products_router, prefix="/products", tags=["products"])
app.include_router(basket_router, prefix="/basket", tags=["basket"])


def main():
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
