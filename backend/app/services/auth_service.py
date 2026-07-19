import uuid
from typing import Optional
from datetime import datetime, timedelta, timezone
import secrets
import hashlib

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
import structlog
from httpx import AsyncClient

from app.core.security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token,
    decode_token, generate_mfa_secret, get_mfa_uri, verify_mfa_code, generate_mfa_qr_code,
)
from app.core.config import settings
from app.core.exceptions import (
    UnauthorizedException, ConflictException, NotFoundException,
    ValidationException,
)
from app.models.user import User, RefreshToken, UserSettings, UserRole
from app.schemas.auth import (
    AuthResponse, UserResponse, TokenResponse, MfaSetupResponse,
    UpdateProfileRequest,
)

logger = structlog.get_logger()


class AuthService:
    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db

    async def signup(self, email: str, password: str, full_name: str) -> AuthResponse:
        result = await self.db.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()
        if existing:
            raise ConflictException("Email already registered")

        user = User(
            email=email,
            password_hash=get_password_hash(password),
            full_name=full_name,
        )
        self.db.add(user)
        await self.db.flush()

        user_settings = UserSettings(user_id=user.id)
        self.db.add(user_settings)
        await self.db.flush()

        from app.models.user import EmailVerificationToken
        import secrets
        token_bytes = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token_bytes.encode()).hexdigest()
        verify_token = EmailVerificationToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        self.db.add(verify_token)
        await self.db.flush()

        access_token = create_access_token(subject=str(user.id), role=user.role.value)
        refresh_token = create_refresh_token(subject=str(user.id))

        await self._store_refresh_token(user.id, refresh_token)

        return AuthResponse(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE,
        )

    async def login(self, email: str, password: str) -> AuthResponse:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not user.password_hash or not verify_password(password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        if user.mfa_enabled:
            return AuthResponse(
                user=UserResponse.model_validate(user),
                access_token="",
                refresh_token="",
                expires_in=0,
                mfa_required=True,
            )

        user.last_login_at = datetime.now(timezone.utc)
        await self.db.flush()

        access_token = create_access_token(subject=str(user.id), role=user.role.value)
        refresh_token = create_refresh_token(subject=str(user.id))

        await self._store_refresh_token(user.id, refresh_token)

        return AuthResponse(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE,
        )

    async def google_login(self, code: str, redirect_uri: Optional[str] = None) -> AuthResponse:
        final_redirect_uri = redirect_uri or settings.GOOGLE_REDIRECT_URI
        token_url = "https://oauth2.googleapis.com/token"

        logger.info("google_oauth_token_exchange_start",
                    token_url=token_url,
                    client_id_prefix=settings.GOOGLE_CLIENT_ID[:20] + "...",
                    redirect_uri=final_redirect_uri,
                    has_client_secret=bool(settings.GOOGLE_CLIENT_SECRET),
                    code_prefix=code[:10] + "...")

        async with AsyncClient() as client:
            token_response = await client.post(
                token_url,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": final_redirect_uri,
                    "grant_type": "authorization_code",
                },
            )

            logger.info("google_oauth_token_exchange_response",
                        status_code=token_response.status_code)

            if token_response.status_code != 200:
                raise UnauthorizedException(
                    f"Google OAuth failed: {token_response.text[:200]}"
                )

            tokens = token_response.json()
            logger.info("google_oauth_userinfo_request",
                        has_access_token=bool(tokens.get("access_token")))

            user_info_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {tokens['access_token']}"},
            )

            logger.info("google_oauth_userinfo_response",
                        status_code=user_info_response.status_code)

            if user_info_response.status_code != 200:
                raise UnauthorizedException("Failed to get Google user info")

            google_user = user_info_response.json()

        google_id = google_user["id"]
        email = google_user["email"]
        full_name = google_user.get("name", "")
        avatar_url = google_user.get("picture")

        result = await self.db.execute(
            select(User).where(
                or_(User.google_id == google_id, User.email == email)
            )
        )
        user = result.scalar_one_or_none()

        if user:
            if not user.google_id:
                user.google_id = google_id
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
        else:
            user = User(
                email=email,
                full_name=full_name,
                google_id=google_id,
                avatar_url=avatar_url,
                is_verified=True,
            )
            self.db.add(user)
            await self.db.flush()

            user_settings = UserSettings(user_id=user.id)
            self.db.add(user_settings)
            await self.db.flush()

        user.last_login_at = datetime.now(timezone.utc)
        await self.db.flush()

        access_token = create_access_token(subject=str(user.id), role=user.role.value)
        refresh_token = create_refresh_token(subject=str(user.id))

        await self._store_refresh_token(user.id, refresh_token)

        return AuthResponse(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE,
        )

    async def refresh_token(self, refresh_token_str: str) -> TokenResponse:
        payload = decode_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")

        user_id = payload.get("sub")
        token_hash = hashlib.sha256(refresh_token_str.encode()).hexdigest()

        result = await self.db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.token_hash == token_hash,
                    RefreshToken.is_revoked == False,
                    RefreshToken.expires_at > datetime.now(timezone.utc),
                )
            )
        )
        stored_token = result.scalar_one_or_none()

        if not stored_token:
            await self._revoke_all_user_tokens(user_id)
            raise UnauthorizedException("Refresh token has been revoked or expired")

        stored_token.is_revoked = True
        stored_token.revoked_at = datetime.now(timezone.utc)

        result = await self.db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        new_access_token = create_access_token(subject=str(user.id), role=user.role.value)
        new_refresh_token = create_refresh_token(subject=str(user.id))

        await self._store_refresh_token(user.id, new_refresh_token)
        await self.db.flush()

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE,
        )

    async def logout(self, user_id: uuid.UUID, refresh_token_str: str):
        token_hash = hashlib.sha256(refresh_token_str.encode()).hexdigest()
        result = await self.db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.token_hash == token_hash,
                    RefreshToken.user_id == user_id,
                )
            )
        )
        token = result.scalar_one_or_none()
        if token:
            token.is_revoked = True
            token.revoked_at = datetime.now(timezone.utc)
            await self.db.flush()

    async def forgot_password(self, email: str):
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            return

        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        from app.models.user import PasswordResetToken
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        self.db.add(reset_token)
        await self.db.flush()

        logger.info("password_reset_email", user_id=str(user.id), token_preview=token[:8])

    async def reset_password(self, token: str, new_password: str):
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        from app.models.user import PasswordResetToken
        result = await self.db.execute(
            select(PasswordResetToken).where(
                and_(
                    PasswordResetToken.token_hash == token_hash,
                    PasswordResetToken.used_at.is_(None),
                    PasswordResetToken.expires_at > datetime.now(timezone.utc),
                )
            )
        )
        reset_token = result.scalar_one_or_none()
        if not reset_token:
            raise ValidationException("Invalid or expired reset token")

        result = await self.db.execute(select(User).where(User.id == reset_token.user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("User not found")

        user.password_hash = get_password_hash(new_password)
        reset_token.used_at = datetime.now(timezone.utc)
        await self._revoke_all_user_tokens(str(user.id))
        await self.db.flush()

    async def verify_email(self, token: str):
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        from app.models.user import EmailVerificationToken
        result = await self.db.execute(
            select(EmailVerificationToken).where(
                and_(
                    EmailVerificationToken.token_hash == token_hash,
                    EmailVerificationToken.used_at.is_(None),
                    EmailVerificationToken.expires_at > datetime.now(timezone.utc),
                )
            )
        )
        verification = result.scalar_one_or_none()
        if not verification:
            raise ValidationException("Invalid or expired verification token")

        result = await self.db.execute(select(User).where(User.id == verification.user_id))
        user = result.scalar_one_or_none()
        if user:
            user.is_verified = True
            verification.used_at = datetime.now(timezone.utc)
            await self.db.flush()

    async def setup_mfa(self, user: User) -> MfaSetupResponse:
        secret = generate_mfa_secret()
        uri = get_mfa_uri(secret, user.email)
        qr_code = generate_mfa_qr_code(uri)

        user.mfa_secret = secret
        await self.db.flush()

        return MfaSetupResponse(secret=secret, qr_code=qr_code, uri=uri)

    async def enable_mfa(self, user: User, code: str):
        if not user.mfa_secret:
            raise ValidationException("MFA not set up. Call /mfa/setup first")

        if not verify_mfa_code(user.mfa_secret, code):
            raise ValidationException("Invalid MFA code")

        user.mfa_enabled = True
        await self.db.flush()

    async def disable_mfa(self, user: User, code: str):
        if not user.mfa_enabled:
            raise ValidationException("MFA is not enabled")

        if not verify_mfa_code(user.mfa_secret, code):
            raise ValidationException("Invalid MFA code")

        user.mfa_enabled = False
        user.mfa_secret = None
        await self.db.flush()

    async def get_settings(self, user: User) -> dict:
        result = await self.db.execute(
            select(UserSettings).where(UserSettings.user_id == user.id)
        )
        settings = result.scalar_one_or_none()
        if not settings:
            settings = UserSettings(user_id=user.id)
            self.db.add(settings)
            await self.db.flush()
        return {
            "theme": settings.theme,
            "language": settings.language,
            "timezone": settings.timezone,
            "approval_gate": settings.approval_gate,
            "auto_submit": settings.auto_submit,
            "daily_application_limit": settings.daily_application_limit,
        }

    async def update_settings(self, user: User, updates: dict) -> dict:
        result = await self.db.execute(
            select(UserSettings).where(UserSettings.user_id == user.id)
        )
        settings = result.scalar_one_or_none()
        if not settings:
            settings = UserSettings(user_id=user.id)
            self.db.add(settings)

        allowed_fields = {"theme", "language", "timezone", "approval_gate", "auto_submit", "daily_application_limit"}
        for key, value in updates.items():
            if key in allowed_fields and hasattr(settings, key):
                setattr(settings, key, value)

        await self.db.flush()
        return {
            "theme": settings.theme,
            "language": settings.language,
            "timezone": settings.timezone,
            "approval_gate": settings.approval_gate,
            "auto_submit": settings.auto_submit,
            "daily_application_limit": settings.daily_application_limit,
        }

    async def update_profile(self, user: User, request: UpdateProfileRequest) -> User:
        if request.full_name is not None:
            user.full_name = request.full_name
        if request.avatar_url is not None:
            user.avatar_url = request.avatar_url
        await self.db.flush()
        return user

    async def _store_refresh_token(self, user_id: uuid.UUID, token: str):
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRE),
        )
        self.db.add(refresh_token)

    async def _revoke_all_user_tokens(self, user_id: str):
        result = await self.db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.user_id == uuid.UUID(user_id),
                    RefreshToken.is_revoked == False,
                )
            )
        )
        tokens = result.scalars().all()
        for token in tokens:
            token.is_revoked = True
            token.revoked_at = datetime.now(timezone.utc)
