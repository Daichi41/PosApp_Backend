from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Order, Payment, Product
from app.schemas.report import ReportSummary

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/", response_model=ReportSummary, summary="Get summary report")
def get_summary_report(db: Session = Depends(get_db)) -> ReportSummary:
    total_products = db.scalar(select(func.count(Product.id))) or 0
    total_orders = db.scalar(select(func.count(Order.id))) or 0
    total_revenue = db.scalar(select(func.coalesce(func.sum(Order.total), 0))) or Decimal("0")
    total_payments = db.scalar(select(func.coalesce(func.sum(Payment.amount), 0))) or Decimal("0")

    return ReportSummary(
        total_products=total_products,
        total_orders=total_orders,
        total_revenue=Decimal(total_revenue),
        total_payments=Decimal(total_payments),
    )
