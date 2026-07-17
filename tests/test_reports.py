import sqlite3

from fastapi.testclient import TestClient

from app.routers import reports


def test_sales_report_returns_matching_items_and_total(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop", "formula": "total"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "category": "Laptop",
        "items": [
            {
                "id": 1,
                "name": "Zenbook 14 OLED",
                "category": "Laptop",
                "price": 42900.0,
            }
        ],
        "total": 42900.0,
    }


def test_sales_report_does_not_allow_sql_injection(client: TestClient) -> None:
    category = "Laptop' OR 1=1 --"

    response = client.get("/reports/sales", params={"category": category})

    assert response.status_code == 200
    assert response.json() == {"category": category, "items": [], "total": 0}


def test_sales_report_rejects_code_in_formula(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop", "formula": "total.__class__"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "formula"]


def test_sales_report_does_not_disclose_database_errors(
    client: TestClient,
    monkeypatch,
) -> None:
    database_error = "database failed at /internal/private/catalog.db"

    def fail_to_create_database() -> sqlite3.Connection:
        raise sqlite3.OperationalError(database_error)

    monkeypatch.setattr(reports, "create_database", fail_to_create_database)

    response = client.get("/reports/sales", params={"category": "Laptop"})

    assert response.status_code == 500
    assert response.json() == {"detail": "Unable to generate sales report"}
    assert database_error not in response.text
