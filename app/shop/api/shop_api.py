import requests
from typing import List
from uuid import UUID

from app.shop.api.models.login import BearerToken, Login
from app.shop.api.models.product import Product, ProductCount, ProductCreate, SalesQuery, SalesRecord


BASE_URL = "http://127.0.0.1:8000"  # The base URL of the shop API
TIMEOUT = 3000


def login(credentials: Login) -> BearerToken:
    """Logs into the shop API and retrieves a Bearer token.
        This function sends a POST request to the /login endpoint of the shop API
        with the provided user credentials. If the login is successful, it parses
        the JSON response to extract and return a BearerToken object containing
        the access token and token type.
        Args:
            credentials (Login): An object containing the username and password.
        Returns:
            BearerToken: An object containing the access token and token type.
        Raises:
            requests.exceptions.HTTPError: If the login request fails (e.g., invalid credentials).
            requests.exceptions.Timeout: If the request times out.
        """
    resp = requests.post(
        f"{BASE_URL}/login",
        json=credentials.model_dump(mode="json"),
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return BearerToken.model_validate(resp.json())


def make_session(token: BearerToken | str) -> requests.Session:
    """Creates and configures a requests Session with a Bearer token.
        This function takes an authorization token, which can be either a raw string
        or a BearerToken object, and prepares a `requests.Session` instance. It
        sets the 'Authorization' header to use the provided token for subsequent
        API requests made with this session.
        Args:
            token (BearerToken | str): The bearer token for authorization.
                If a `BearerToken` object is provided, its `access_token`
                attribute will be used.
        Returns:
            requests.Session: A configured `requests.Session` object with the
                'Authorization' header set.
        """

    if isinstance(token, BearerToken):
        token = token.access_token
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {token}"})
    return s


def search_products(session: requests.Session, description: str | None = None) -> List[Product]:
    """Searches for products via the API based on a description.
        Args:
            session (requests.Session): The client session used to make the request.
            description (str): The product description to search for.
        Raises:
            requests.exceptions.HTTPError: If the API returns an unsuccessful status code.
        Returns:
            List[Product]: A list of `Product` objects matching the search query.
        """

    resp = session.get(
        f"{BASE_URL}/products/search",
        params={"description": description or ""},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return [Product.model_validate(p) for p in resp.json()]

def add_product(session: requests.Session, product: ProductCreate) -> Product:
    """Adds a new product via the API.

        Args:
            session: The requests session to use for the API call.
            product: A `ProductCreate` model instance with the product data.

        Returns:
            A `Product` model instance representing the newly created product.

        Raises:
            requests.exceptions.HTTPError: If the API returns an error status code.
            requests.exceptions.Timeout: If the request times out.
        """
    # TODO: Implement this function to add a new product via the API.
    # It should send a POST request to the /products endpoint with the product data,
    # then parse and return the response as a Product object.

    raise NotImplementedError("Workshop task 1 - provide implementation")

def update_product(session: requests.Session, product_id: UUID, updated: ProductCreate) -> Product:
    """Updates an existing product via the API.

        Args:
            session: The requests session to use for the API call.
            product_id: The UUID of the product to be updated.
            updated: A `ProductCreate` model instance with the new product data.

        Returns:
            A `Product` model instance representing the updated product.

        Raises:
            requests.exceptions.HTTPError: If the API returns an error status code.
            requests.exceptions.Timeout: If the request times out.
        """
    resp = session.put(
        f"{BASE_URL}/products/{product_id}",
        json=updated.model_dump(mode="json"),
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return Product.model_validate(resp.json())

def delete_product(session: requests.Session, product_id: UUID) -> dict:
    """Deletes a product from the shop via the API.
        Args:
            session (requests.Session): The requests session object to use for the request.
            product_id (UUID): The unique identifier of the product to delete.
        Raises:
            requests.exceptions.HTTPError: If the API returns an unsuccessful status code.
        Returns:
            dict: The JSON response from the API, typically confirming deletion.
        """
    
    resp = session.delete(f"{BASE_URL}/products/{product_id}", timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def get_sales_history(session: requests.Session, query: SalesQuery) -> List[SalesRecord]:
    """Retrieves the sales history from the shop API.
        Args:
            session: The requests session object to use for making the HTTP request.
            query: An object containing the filter criteria for the sales history search.
        Returns:
            A list of sales records that match the provided query.
        Raises:
            requests.exceptions.HTTPError: If the API responds with an HTTP error status (e.g., 4xx or 5xx).
    """

    resp = session.get(
        f"{BASE_URL}/sales",
        json=query.model_dump(mode="json", exclude_none=True),
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return [SalesRecord.model_validate(s) for s in resp.json()]

def get_product_count(session: requests.Session) -> int:
    """Retrieves the total count of products from the shop API.
        Args:
            session: The requests session object to use for making the HTTP request.

        Returns:
            A ProductCount model containing the total count of products.

        Raises:
            requests.exceptions.HTTPError: If the API responds with an HTTP error status (e.g., 4xx or 5xx).
    """

    resp = session.get(f"{BASE_URL}/products/count", timeout=TIMEOUT)
    resp.raise_for_status()
    return ProductCount.model_validate(resp.json()).total

def annual_sales(session: requests.Session, year: int, bucket: str) -> list[float]:
    """Retrieves the total sales by month for a specific year.

        Args:
            session: The requests session object to use for making the HTTP request.
            year: The year for which to retrieve monthly sales data.

        Returns:
            A list of floats representing the total sales for each month (Jan-Dec) of the specified year.

        Raises:
            requests.exceptions.HTTPError: If the API responds with an HTTP error status (e.g., 4xx or 5xx).
    """

    # TODO: Implement this function to retrieve annual sales data via the API.
    # It should send a GET request to the /sales/{year}/{bucket} endpoint,
    # then parse and return the response as a list of floats.

    raise NotImplementedError("Workshop task 2 - provide implementation")