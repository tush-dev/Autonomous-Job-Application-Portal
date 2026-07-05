from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()
logger = structlog.get_logger()


@router.post("/chat")
async def chat(
    message: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return {"message": "AI chat streaming endpoint (to be implemented)", "role": "assistant", "content": "AI coaching will be available soon."}


@router.post("/analyze")
async def analyze(
    resume_id: str,
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return {"message": "AI analysis endpoint (to be implemented)"}


@router.post("/suggest")
async def suggest(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return {"message": "AI suggestion endpoint (to be implemented)"}


@router.post("/roadmap")
async def roadmap(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return {"message": "Career roadmap endpoint (to be implemented)"}
