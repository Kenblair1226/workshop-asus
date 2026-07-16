from typing import Literal

from app.models import Product

PRODUCTS = [
    Product(id=1, name="Zenbook 14 OLED", category="Laptop", price=42900),
    Product(id=2, name="ROG Zephyrus G14", category="Gaming Laptop", price=62900),
    Product(id=3, name="ProArt P16", category="Creator Laptop", price=79900),
    Product(id=4, name="TUF Gaming A15", category="Gaming Laptop", price=38900),
    Product(id=5, name="ROG Ally X", category="Handheld", price=26900),
    Product(id=6, name="ProArt Display PA279CRV", category="Monitor", price=15900),
]


def list_products(
    q: str | None = None,
    max_price: float | None = None,
    sort: Literal["name", "price"] | None = None,
    order: Literal["asc", "desc"] = "asc",
) -> list[Product]:
    products = PRODUCTS.copy()
    if q is not None:
        query = q.casefold()
        products = [
            product
            for product in products
            if query in product.name.casefold() or query in product.category.casefold()
        ]
    if max_price is not None:
        products = [product for product in products if product.price <= max_price]
    if sort == "name":
        products.sort(key=lambda product: product.name, reverse=order == "desc")
    elif sort == "price":
        products.sort(key=lambda product: product.price, reverse=order == "desc")
    return products


def get_product(product_id: int) -> Product | None:
    return next((product for product in PRODUCTS if product.id == product_id), None)
