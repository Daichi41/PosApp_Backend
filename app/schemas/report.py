from __future__ import annotations

from decimal import Decimal

from app.schemas.base import ORMModel


class ReportSummary(ORMModel):
    total_products: int
    total_orders: int
    total_revenue: Decimal
    total_payments: Decimal
