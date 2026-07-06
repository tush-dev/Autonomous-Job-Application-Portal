from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.models.user import User
from app.schemas.application import CoverLetterGenerateRequest, CoverLetterResponse
from app.api.deps import get_current_user
from app.services.cover_letter_service import CoverLetterService

router = APIRouter()
logger = structlog.get_logger()


@router.get("")
async def list_cover_letters(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CoverLetterService(db)
    cover_letters = await service.list_cover_letters(current_user.id)
    return cover_letters


@router.post("/generate", response_model=CoverLetterResponse, status_code=status.HTTP_201_CREATED)
async def generate_cover_letter(
    request: CoverLetterGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CoverLetterService(db)
    cover_letter = await service.generate_cover_letter(
        user_id=current_user.id,
        application_id=request.application_id,
        tone=request.tone,
        custom_instructions=request.custom_instructions,
    )
    return cover_letter


@router.get("/{cover_letter_id}", response_model=CoverLetterResponse)
async def get_cover_letter(
    cover_letter_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CoverLetterService(db)
    cover_letter = await service.get_cover_letter(current_user.id, cover_letter_id)
    return cover_letter


@router.delete("/{cover_letter_id}")
async def delete_cover_letter(
    cover_letter_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CoverLetterService(db)
    await service.delete_cover_letter(current_user.id, cover_letter_id)
    return {"success": True, "message": "Cover letter deleted"}


@router.patch("/{cover_letter_id}", response_model=CoverLetterResponse)
async def update_cover_letter(
    cover_letter_id: str,
    content: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CoverLetterService(db)
    cover_letter = await service.update_cover_letter(
        user_id=current_user.id,
        cover_letter_id=cover_letter_id,
        content=content,
    )
    return cover_letter
