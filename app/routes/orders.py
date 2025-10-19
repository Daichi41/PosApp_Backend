from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.deps.auth import get_current_user
from app.db import get_db
from app.models import Order, OrderItem, OrderStatus, Payment, PaymentMethod, Product, User
from app.schemas.order import OrderCreate, OrderRead

router = APIRouter(prefix="/orders", tags=["orders"])

MONEY_QUANTIZER = Decimal("0.01")

def quantize(amount: Decimal) -> Decimal:
    return amount.quantize(MONEY_QUANTIZER, rounding=ROUND_HALF_UP)

def generate_order_no() -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    suffix = uuid.uuid4().hex[:4].upper()
    return f"{timestamp}-{suffix}"

@router.get("/", response_model=list[OrderRead], summary="List orders")
def list_orders(db: Session = Depends(get_db)) -> list[OrderRead]:
    orders = (
        db.execute(
            select(Order)
            .options(joinedload(Order.items), joinedload(Order.payments))
            .order_by(Order.created_at.desc())
        )
        .scalars()
        .unique()
        .all()
    )
    return orders

@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED, summary="Create order")
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderRead:
    if not payload.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order requires at least one item")

    if payload.user_id is not None and payload.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user_id does not match token")

    subtotal = Decimal("0")
    tax_total = Decimal("0")
    order_items: list[OrderItem] = []

    for item in payload.items:
        product = db.get(Product, item.product_id)
        if not product or not product.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {item.product_id} not available")

        unit_price = Decimal(product.unit_price)
        quantity = item.quantity
        line_subtotal = unit_price * quantity
        tax_rate = Decimal(product.tax_rate) / Decimal("100")
        line_tax = quantize(line_subtotal * tax_rate)

        subtotal += line_subtotal
        tax_total += line_tax

        order_items.append(
            OrderItem(
                product_id=product.id,
                quantity=quantity,
                unit_price=quantize(unit_price),
                line_total=quantize(line_subtotal + line_tax),
            )
        )

    subtotal = quantize(subtotal)
    tax_total = quantize(tax_total)
    total = quantize(subtotal + tax_total)

    payment_models = payload.payments or []
    payments: list[Payment] = []
    paid_amount = Decimal("0")

    if not payment_models:
        payments.append(Payment(method=PaymentMethod.CASH, amount=total))
        paid_amount = total
    else:
        for payment in payment_models:
            amount = quantize(Decimal(payment.amount))
            if amount <= Decimal("0"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment amount must be positive")
            payments.append(
                Payment(method=payment.method, amount=amount, transaction_id=payment.transaction_id)
            )
            paid_amount += amount

    paid_amount = quantize(paid_amount)
    change_amount = quantize(paid_amount - total) if paid_amount >= total else quantize(Decimal("0"))
    status_value = OrderStatus.PAID if paid_amount >= total else OrderStatus.DRAFT

    order = Order(
        order_no=generate_order_no(),
        user_id=current_user.id,
        subtotal=subtotal,
        tax_total=tax_total,
        total=total,
        paid_amount=paid_amount,
        change_amount=change_amount,
        status=status_value,
        memo=payload.memo,
        items=order_items,
        payments=payments,
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return order
