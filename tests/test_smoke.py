from __future__ import annotations

from decimal import Decimal
from typing import Tuple

from sqlalchemy.orm import sessionmaker

from app.models import User, UserRole
from app.utils.security import hash_password

ClientAndSession = Tuple["TestClient", sessionmaker]

try:  # pragma: no cover
    from fastapi.testclient import TestClient
except ImportError:  # pragma: no cover
    TestClient = object  # type: ignore


def _create_user(session_factory: sessionmaker, email: str, password: str, role: UserRole = UserRole.CLERK) -> User:
    with session_factory() as session:  # type: ignore[call-arg]
        user = User(email=email, password_hash=hash_password(password), role=role)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def _auth_headers(client: "TestClient", email: str, password: str) -> dict[str, str]:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_healthz_returns_ok(client_and_session: ClientAndSession) -> None:
    client, _ = client_and_session
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_auth_login_success(client_and_session: ClientAndSession) -> None:
    client, session_factory = client_and_session
    user = _create_user(session_factory, "clerk@example.com", "secret")

    response = client.post("/auth/login", json={"email": user.email, "password": "secret"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["access_token"]
    assert payload["token_type"] == "bearer"
    assert payload["user"]["email"] == "clerk@example.com"


def test_product_and_order_flow(client_and_session: ClientAndSession) -> None:
    client, session_factory = client_and_session
    user = _create_user(session_factory, "cashier@example.com", "changeme")

    headers = _auth_headers(client, user.email, "changeme")

    product_response = client.post(
        "/products",
        headers=headers,
        json={
            "sku": "SKU-001",
            "name": "Bottled Water",
            "description": "500ml",
            "unit_price": "100.00",
            "tax_rate": "10.00",
            "is_active": True,
        },
    )
    assert product_response.status_code == 201, product_response.text
    product = product_response.json()

    order_response = client.post(
        "/orders",
        headers=headers,
        json={
            "user_id": user.id,  # 任意だが一致していることを確認
            "items": [
                {"product_id": product["id"], "quantity": 2},
            ],
            "payments": [
                {"method": "cash", "amount": "220.00"},
            ],
            "memo": "evening shift",
        },
    )
    assert order_response.status_code == 201, order_response.text
    order = order_response.json()

    assert order["user_id"] == user.id
    assert Decimal(order["total"]) == Decimal("220.00")
    assert Decimal(order["paid_amount"]) == Decimal("220.00")
    assert order["items"][0]["quantity"] == 2

    orders_list = client.get("/orders")
    assert orders_list.status_code == 200
    assert len(orders_list.json()) == 1

    report = client.get("/reports")
    assert report.status_code == 200
    summary = report.json()
    assert summary["total_products"] == 1
    assert summary["total_orders"] == 1
    assert Decimal(summary["total_revenue"]) == Decimal("220.00")
