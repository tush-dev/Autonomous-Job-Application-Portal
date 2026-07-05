from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from typing import List, Optional


class Settings(BaseSettings):
    APP_NAME: str = "JobAgent"
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "change-me"
    DEBUG: bool = True

    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+asyncpg://jobagent:jobagent_dev@postgres:5432/jobagent"
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 5

    REDIS_URL: RedisDsn = Field(default="redis://:redis_dev@redis:6379/0")
    REDIS_CACHE_TTL: int = 1800

    JWT_PRIVATE_KEY: str = ""
    JWT_PUBLIC_KEY: str = ""
    JWT_ALGORITHM: str = "RS256"
    JWT_ACCESS_TOKEN_EXPIRE: int = 900
    JWT_REFRESH_TOKEN_EXPIRE: int = 604800

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""

    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    AI_DEFAULT_MODEL: str = "gpt-4o-mini"
    AI_FALLBACK_MODEL: str = "gpt-4o-mini"

    S3_ENDPOINT: str = "http://minio:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "jobagent-uploads"
    S3_REGION: str = "us-east-1"

    SMTP_HOST: str = "mailpit"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@jobagent.local"

    SENTRY_DSN: Optional[str] = None

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://frontend:3000",
    ]

    TRUSTED_HOSTS: List[str] = [
        "localhost",
        "frontend",
        "api",
        "*.jobagent.ai",
    ]

    PASSWORD_BCRYPT_ROUNDS: int = 12
    PASSWORD_MIN_LENGTH: int = 12

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: int = 100
    RATE_LIMIT_WINDOW: int = 60

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("TRUSTED_HOSTS", mode="before")
    @classmethod
    def parse_trusted_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
