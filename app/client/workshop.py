from typing import List

from client_api import login_pydantic, add_to_basket, get_basket, search_products
from models import BasketSummary, ProductSearch, LoginModel

def main():


    #Login to service
    user = LoginModel(
        username = "Version1",
        password = "Version1"
    )
    user_token = login_pydantic(user)
    print(f"login_pydantic got token: {user_token.access_token}")


    #Search for items in the shop
    search_terms = ["emulsion", "screws", "drill"]
    chosen_ids: List[int] = []

    for term in search_terms:
        results = search_products(ProductSearch(search_str=term))
        if not results:
            print(f"[search] '{term}' - no results, skipping")
            continue
        top = results[0]
        chosen_ids.append(top.id)
        print(f"[search] '{term}' - picked: {top.id} | {top.name} (${top.price})")
    

    #Add items to basket
    for pid in chosen_ids:
        basket_after = add_to_basket(user_token.access_token, product_id=pid, quantity=2)
        print(f"[basket] added product_id={pid}; basket now has {len(basket_after.items)} item(s)")  


    basket = get_basket(user_token.access_token)
    print(f"Current basket: {basket}")

    # Print basket summary
    for it in basket.items:
        line_total = round(it.unit_price * it.quantity, 2)
        print(f" - {it.product_id}: {it.name} x{it.quantity} @ £{it.unit_price} = £{line_total}")





    # Print basket summary
    summary = BasketSummary(items=basket.items)
    print(f"\nBasket summary: total_quantity={summary.total_quantity}, total=£{summary.total}")
    

if __name__ == "__main__":
    main()
