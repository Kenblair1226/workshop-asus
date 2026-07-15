from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

from app.models import Product, ProductPage
from app.repository import get_product, list_products

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductPage)
def read_products(
    q: str | None = Query(default=None, min_length=1),
    sort: Literal["name", "price"] | None = None,
    order: Literal["asc", "desc"] = "asc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=20),
) -> ProductPage:
    products = list_products()

    if q is not None:
        search_term = q.casefold()
        products = [
            product
            for product in products
            if search_term in product.name.casefold()
            or search_term in product.category.casefold()
        ]

    if sort is not None:
        reverse = order == "desc"
        if sort == "name":
            products = sorted(
                products,
                key=lambda product: product.name.casefold(),
                reverse=reverse,
            )
        else:
            products = sorted(products, key=lambda product: product.price, reverse=reverse)

    total = len(products)
    offset = (page - 1) * page_size
    page_items = products[offset : offset + page_size]

    return ProductPage(
        items=page_items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{product_id}", response_model=Product)
def read_product(product_id: int) -> Product:
    product = get_product(product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product
