import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
        "sim",
    }


def _as_int(name: str, default: int) -> int:
    value = os.getenv(name)

    if value is None or not value.strip():
        return default

    try:
        parsed_value = int(value)
    except ValueError as exc:
        raise RuntimeError(
            f"A variável {name} deve conter um número inteiro."
        ) from exc

    if parsed_value <= 0:
        raise RuntimeError(
            f"A variável {name} deve ser maior que zero."
        )

    return parsed_value


def _normalize_samesite(value: str | None) -> str:
    normalized = (value or "Lax").strip().lower()

    allowed_values = {
        "lax": "Lax",
        "strict": "Strict",
        "none": "None",
    }

    if normalized not in allowed_values:
        raise RuntimeError(
            "SESSION_COOKIE_SAMESITE deve ser Lax, Strict ou None."
        )

    return allowed_values[normalized]


class Config:
    APP_ENV = os.getenv("APP_ENV", "development").strip().lower()

    SECRET_KEY = os.getenv("SECRET_KEY", "chave_dev_falae")

    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        str(BASE_DIR / "uploads"),
    )

    LOG_FOLDER = os.getenv(
        "LOG_FOLDER",
        str(BASE_DIR / "logs"),
    )

    MAX_CONTENT_LENGTH = _as_int(
        "MAX_CONTENT_LENGTH",
        16 * 1024 * 1024,
    )

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = _normalize_samesite(
        os.getenv("SESSION_COOKIE_SAMESITE")
    )

    SESSION_COOKIE_SECURE = _as_bool(
        os.getenv("SESSION_COOKIE_SECURE"),
        default=APP_ENV == "production",
    )

    SESSION_REFRESH_EACH_REQUEST = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    REMEMBER_COOKIE_SAMESITE = SESSION_COOKIE_SAMESITE

    WTF_CSRF_ENABLED = _as_bool(
        os.getenv("WTF_CSRF_ENABLED"),
        default=True,
    )

    WTF_CSRF_CHECK_DEFAULT = True

    WTF_CSRF_TIME_LIMIT = _as_int(
        "WTF_CSRF_TIME_LIMIT_SECONDS",
        60 * 60 * 2,
    )

    WTF_CSRF_SSL_STRICT = _as_bool(
        os.getenv("WTF_CSRF_SSL_STRICT"),
        default=APP_ENV == "production",
    )

    TRUST_PROXY_HEADERS = _as_bool(
        os.getenv(
            "TRUST_PROXY_HEADERS",
            "false",
        )
    )

    PREFERRED_URL_SCHEME = (
        "https"
        if APP_ENV == "production"
        else "http"
    )

    @classmethod
    def validate(cls) -> None:
        allowed_environments = {
            "development",
            "testing",
            "production",
        }

        if cls.APP_ENV not in allowed_environments:
            raise RuntimeError(
                "APP_ENV inválido. Use development, testing ou production."
            )

        if cls.APP_ENV == "production":
            if not cls.SECRET_KEY or not cls.SECRET_KEY.strip():
                raise RuntimeError(
                    "SECRET_KEY de produção não configurada."
                )

            if cls.SECRET_KEY == "chave_dev_falae":
                raise RuntimeError(
                    "A SECRET_KEY padrão de desenvolvimento "
                    "não pode ser utilizada em produção."
                )

            if len(cls.SECRET_KEY) < 32:
                raise RuntimeError(
                    "A SECRET_KEY de produção deve possuir "
                    "pelo menos 32 caracteres."
                )

            if not cls.SESSION_COOKIE_SECURE:
                raise RuntimeError(
                    "SESSION_COOKIE_SECURE deve ser true em produção."
                )

            if not cls.WTF_CSRF_ENABLED:
                raise RuntimeError(
                    "WTF_CSRF_ENABLED deve ser true em produção."
                )

            if not cls.WTF_CSRF_SSL_STRICT:
                raise RuntimeError(
                    "WTF_CSRF_SSL_STRICT deve ser true em produção."
                )

        Path(cls.UPLOAD_FOLDER).mkdir(
            parents=True,
            exist_ok=True,
        )

        Path(cls.LOG_FOLDER).mkdir(
            parents=True,
            exist_ok=True,
        )