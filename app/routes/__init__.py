"""FastAPI route modules."""

from app.routes import auth, health, orders, products, reports

__all__ = [
    "auth",
    "health",
    "orders",
    "products",
    "reports",
]
