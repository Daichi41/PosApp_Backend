from __future__ import annotations
from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine, pool
from dotenv import load_dotenv
load_dotenv()  # .env を環墁E��数に取り込む
import os, sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

# Alembic Config
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ==== DB URL ====
db_url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")

# ==== メタチE�Eタ ====
from app.models.base import Base  # noqa: E402
# ==== メタチE�Eタ ====
# Base は models 層から直接 import�E�Eb.py 経由は避ける�E�Efrom app.models.base import Base  # noqa: E402
import app.models  # noqa: F401,E402  # モチE��定義をimportしてチE�Eブル登録
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = create_engine(db_url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
