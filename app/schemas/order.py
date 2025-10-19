from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.order import OrderStatus
from app.models.payment import PaymentMethod
from app.schemas.base import ORMModel


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)


class PaymentCreate(BaseModel):
    method: PaymentMethod = PaymentMethod.CASH
    amount: Decimal = Field(..., ge=Decimal("0"))
    transaction_id: str | None = None


class OrderCreate(BaseModel):
    user_id: int | None = None
    items: list[OrderItemCreate]
    payments: list[PaymentCreate] | None = None
    memo: str | None = None


class OrderItemRead(ORMModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class PaymentRead(ORMModel):
    id: int
    method: PaymentMethod
    amount: Decimal
    transaction_id: str | None
    created_at: datetime


class OrderRead(ORMModel):
    id: int
    order_no: str
    user_id: int
    subtotal: Decimal
    tax_total: Decimal
    total: Decimal
    paid_amount: Decimal
    change_amount: Decimal
    status: OrderStatus
    memo: str | None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemRead]
    payments: list[PaymentRead]
