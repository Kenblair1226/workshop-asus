from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_products(client: TestClient) -> None:
    response = client.get("/products")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 6
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert body["items"][0]["name"] == "Zenbook 14 OLED"


def test_list_products_with_max_price(client: TestClient) -> None:
    response = client.get("/products", params={"max_price": 38900})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert all(item["price"] <= 38900 for item in body["items"])
    assert [item["name"] for item in body["items"]] == [
        "TUF Gaming A15",
        "ROG Ally X",
        "ProArt Display PA279CRV",
    ]


def test_list_products_rejects_negative_max_price(client: TestClient) -> None:
    response = client.get("/products", params={"max_price": -1})

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["loc"][-1] == "max_price"
    assert error["type"] == "greater_than_equal"


def test_list_products_supports_search_sort_and_pagination(client: TestClient) -> None:
    response = client.get(
        "/products",
        params={
            "q": "gaming",
            "sort": "price",
            "order": "desc",
            "page": 1,
            "page_size": 1,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["page_size"] == 1
    assert [item["name"] for item in body["items"]] == ["ROG Zephyrus G14"]


def test_get_product(client: TestClient) -> None:
    response = client.get("/products/2")

    assert response.status_code == 200
    assert response.json()["name"] == "ROG Zephyrus G14"


def test_get_missing_product(client: TestClient) -> None:
    response = client.get("/products/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}
