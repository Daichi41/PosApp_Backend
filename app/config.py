import os
from functools import lru_cache
from pathlib import Path
from typing import Dict

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_file(path: Path | None = None) -> None:
    env_path = path or (BASE_DIR / ".env")
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


class Settings:
    def __init__(self) -> None:
        _load_env_file()
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.database_url = self._build_database_url()
        self.secret_key = self._resolve_secret_key()
        self.access_token_expire_minutes = self._resolve_access_token_expire_minutes()

    def _build_database_url(self) -> str:
        url = os.getenv("DATABASE_URL")
        if url:
            return url
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        name = os.getenv("DB_NAME")
        if all([user, password, host, name]):
            extras: list[str] = []
            ssl_ca = os.getenv("DB_SSL_CA")
            if ssl_ca:
                extras.append(f"ssl_ca={ssl_ca}")
            query = f"?{'&'.join(extras)}" if extras else ""
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}{query}"
        # fallback to local sqlite for convenience (e.g. during tests)
        return "sqlite+pysqlite:///./app.db"

    def _resolve_secret_key(self) -> str:
        key = os.getenv("SECRET_KEY")
        if key:
            return key
        return "dev-secret-key"

    def _resolve_access_token_expire_minutes(self) -> int:
        raw_value = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
        try:
            return int(raw_value) if raw_value is not None else 30
        except ValueError:
            return 30

    @property
    def sqlalchemy_engine_options(self) -> Dict[str, object]:
        options: Dict[str, object] = {"future": True, "pool_pre_ping": True}
        if self.database_url.startswith("sqlite"):
            options["connect_args"] = {"check_same_thread": False}
        return options


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def reset_settings_cache() -> None:
    get_settings.cache_clear()
