from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Response, status
from urllib.parse import quote
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.exceptions import NotFoundException, ValidationException
from app.models.user import User
from app.schemas.resume import (
    ResumeUploadResponse, ResumeResponse, ResumeAnalysisResponse,
    ResumeTailorRequest, ResumeTailorResponse, ResumeUpdateRequest,
)
from app.api.deps import get_current_user
from app.services.resume_service import ResumeService

router = APIRouter()
logger = structlog.get_logger()


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    result = await service.upload_resume(user=current_user, file=file)
    return result


@router.get("", response_model=list[ResumeResponse])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    resumes = await service.list_resumes(current_user.id)
    return resumes


@router.get("/count")
async def count_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models.resume import Resume
    from sqlalchemy import select, func

    result = await db.execute(
        select(func.count(Resume.id)).where(
            Resume.user_id == current_user.id,
            Resume.is_active == True,
        )
    )
    count = result.scalar() or 0
    return {"count": count}


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: str,
    request: ResumeUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    return await service.update_resume(current_user.id, resume_id, request.parsed_data or {})


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    resume = await service.get_resume(current_user.id, resume_id)
    return resume


@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    content, file_name, content_type = await service.get_resume_file(
        current_user.id, resume_id
    )
    return Response(
        content=content,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quote(file_name)}"
        },
    )


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    await service.delete_resume(current_user.id, resume_id)
    return {"success": True, "message": "Resume deleted"}


@router.get("/{resume_id}/analysis", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    analysis = await service.analyze_resume(current_user.id, resume_id)
    return analysis


@router.post("/tailor", response_model=ResumeTailorResponse)
async def tailor_resume(
    request: ResumeTailorRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    result = await service.tailor_resume(
        user_id=current_user.id,
        resume_id=request.resume_id,
        job_id=request.job_id,
        format_type=request.format,
    )
    return result
