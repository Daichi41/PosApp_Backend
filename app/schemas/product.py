from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.base import ORMModel


class ProductBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    unit_price: Decimal = Field(..., gt=Decimal("0"))
    tax_rate: Decimal = Field(default=Decimal("10"), ge=Decimal("0"), le=Decimal("100"))
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    unit_price: Decimal | None = Field(default=None, gt=Decimal("0"))
    tax_rate: Decimal | None = Field(default=None, ge=Decimal("0"), le=Decimal("100"))
    is_active: bool | None = None


class ProductRead(ORMModel):
    id: int
    sku: str
    name: str
    description: str | None
    unit_price: Decimal
    tax_rate: Decimal
    is_active: bool
