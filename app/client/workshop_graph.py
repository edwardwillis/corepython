import matplotlib.pyplot as plt

from app.shop.api.models.login import Login
from app.shop.api.shop_api import annual_sales, login, make_session, annual_sales

def draw_sales_graph(total_sales_by_month: list[float], year: int) -> None:
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    x = months[:len(total_sales_by_month)]
    y = [value / 1_000_000 for value in total_sales_by_month]  # Scale to millions

    # Plot as a bar chart
    plt.bar(x, y)

    # Labels and title
    plt.xlabel(f"Month ({year})")
    plt.ylabel("Total Sales Revenue (Millions EUR)")
    plt.title(f"Monthly Sales Revenue for {year}")

    # Show the graph
    plt.show()

if __name__ == "__main__":
    token = login(Login(username="Version1", password="Version1"))
    session = make_session(token)

    year = 2025

    # Get all products
    sales_data = annual_sales(session, year=year, bucket="month")
    draw_sales_graph(sales_data, year=year)