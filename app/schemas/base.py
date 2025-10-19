# app/schemas/base.py  （Pydantic v2 専用）

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """SQLAlchemy ORMオブジェクトからの生成を許可（v2）"""
    # v1の `Config.orm_mode = True` 相当
    model_config = ConfigDict(from_attributes=True)


def model_dump(model: BaseModel) -> dict:
    """Pydantic v2 の辞書化をラップ（将来の互換用フック）"""
    return model.model_dump()
