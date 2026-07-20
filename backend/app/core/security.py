from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
import bcrypt
import pyotp
import qrcode
import qrcode.image.svg

from app.core.config import settings


def _jwt_signing_config() -> tuple[str, str]:
    if settings.JWT_PRIVATE_KEY:
        return settings.JWT_PRIVATE_KEY, settings.JWT_ALGORITHM
    return settings.APP_SECRET_KEY, "HS256"


def _jwt_verification_config() -> tuple[str, str]:
    if settings.JWT_PUBLIC_KEY:
        return settings.JWT_PUBLIC_KEY, settings.JWT_ALGORITHM
    if settings.JWT_PRIVATE_KEY:
        return settings.JWT_PRIVATE_KEY, settings.JWT_ALGORITHM
    return settings.APP_SECRET_KEY, "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(
    subject: str,
    role: str = "user",
    expires_delta: Optional[timedelta] = None,
) -> str:
    if expires_delta is None:
        expires_delta = timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRE)

    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + expires_delta,
        "type": "access",
        "iss": settings.APP_NAME,
    }
    signing_key, algorithm = _jwt_signing_config()
    return jwt.encode(payload, signing_key, algorithm=algorithm)


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    if expires_delta is None:
        expires_delta = timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRE)

    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + expires_delta,
        "type": "refresh",
        "iss": settings.APP_NAME,
    }
    signing_key, algorithm = _jwt_signing_config()
    return jwt.encode(payload, signing_key, algorithm=algorithm)


def decode_token(token: str) -> dict:
    try:
        verification_key, algorithm = _jwt_verification_config()
        payload = jwt.decode(
            token,
            verification_key,
            algorithms=[algorithm],
            issuer=settings.APP_NAME,
        )
        return payload
    except JWTError:
        return {}


def generate_mfa_secret() -> str:
    return pyotp.random_base32()


def get_mfa_uri(secret: str, email: str) -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=email,
        issuer_name=settings.APP_NAME,
    )


def verify_mfa_code(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def generate_mfa_qr_code(uri: str) -> str:
    img = qrcode.make(uri, image_factory=qrcode.image.svg.SvgImage)
    return img.to_string().decode("utf-8")
