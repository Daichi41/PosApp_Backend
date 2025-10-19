from __future__ import annotations

import os
from typing import List, Tuple

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth, health, orders, products, reports

DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
)


def _resolve_cors_settings() -> Tuple[List[str], bool]:
    raw_origins = os.getenv("CORS_ORIGINS", "")
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

    if not origins:
        origins = list(DEFAULT_CORS_ORIGINS)

    allow_credentials = True
    if "*" in origins:
        origins = ["*"]
        allow_credentials = False

    return origins, allow_credentials


def create_app() -> FastAPI:
    app = FastAPI(title="POS API", version="0.1.0")
    cors_origins, allow_credentials = _resolve_cors_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(products.router)
    app.include_router(orders.router)
    app.include_router(reports.router)

    return app


app = create_app()
