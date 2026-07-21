import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on", "sim"}


class Config:
    APP_ENV = os.getenv("APP_ENV", "development").lower()
    SECRET_KEY = os.getenv("SECRET_KEY", "chave_dev_falae")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024)))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = _as_bool(os.getenv("SESSION_COOKIE_SECURE"), default=APP_ENV == "production")
    PREFERRED_URL_SCHEME = "https" if APP_ENV == "production" else "http"

    @classmethod
    def validate(cls) -> None:
        if cls.APP_ENV == "production" and cls.SECRET_KEY == "chave_dev_falae":
            raise RuntimeError("SECRET_KEY de produção não configurada. Defina uma chave forte no arquivo .env.")
        Path(cls.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
        (BASE_DIR / "logs").mkdir(parents=True, exist_ok=True)
