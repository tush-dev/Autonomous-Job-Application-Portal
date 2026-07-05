from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token,
    decode_token, generate_mfa_secret, get_mfa_uri, verify_mfa_code, generate_mfa_qr_code,
)
from app.core.exceptions import (
    UnauthorizedException, ConflictException, NotFoundException,
    ValidationException, RateLimitException,
)
from app.models.user import User, RefreshToken, UserSettings
from app.schemas.auth import (
    SignupRequest, LoginRequest, RefreshTokenRequest, AuthResponse, UserResponse,
    TokenResponse, ForgotPasswordRequest, ResetPasswordRequest,
    VerifyEmailRequest, MfaSetupResponse, MfaVerifyRequest,
    GoogleLoginRequest, UpdateProfileRequest,
)
from app.api.deps import get_current_user
from app.services.auth_service import AuthService

router = APIRouter()
logger = structlog.get_logger()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    result = await service.signup(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
    )
    return result


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    result = await service.login(email=request.email, password=request.password)
    return result


@router.post("/google", response_model=AuthResponse)
async def google_login(request: GoogleLoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    result = await service.google_login(code=request.code, redirect_uri=request.redirect_uri)
    return result


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    result = await service.refresh_token(request.refresh_token)
    return result


@router.post("/logout")
async def logout(
    request: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.logout(current_user.id, request.refresh_token)
    return {"success": True, "message": "Logged out successfully"}


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.forgot_password(request.email)
    return {"success": True, "message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.reset_password(token=request.token, new_password=request.password)
    return {"success": True, "message": "Password reset successfully"}


@router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.verify_email(request.token)
    return {"success": True, "message": "Email verified successfully"}


@router.post("/mfa/setup", response_model=MfaSetupResponse)
async def setup_mfa(
    current_user: User = Depends(get_current_user),
):
    service = AuthService()
    result = await service.setup_mfa(current_user)
    return result


@router.post("/mfa/verify")
async def verify_mfa(
    request: MfaVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.enable_mfa(current_user, request.code)
    return {"success": True, "message": "MFA enabled successfully"}


@router.post("/mfa/disable")
async def disable_mfa(
    request: MfaVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.disable_mfa(current_user, request.code)
    return {"success": True, "message": "MFA disabled successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    user = await service.update_profile(current_user, request)
    return user
