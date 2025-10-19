from __future__ import annotations

from pydantic import EmailStr

from app.models.user import UserRole
from app.schemas.base import ORMModel


class UserRead(ORMModel):
    id: int
    email: EmailStr
    role: UserRole
