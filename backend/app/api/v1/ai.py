import time
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.ai import gateway
from app.core.ai_logger import log_ai_request
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()
logger = structlog.get_logger()


class ChatRequest(BaseModel):
    message: str


class AnalyzeRequest(BaseModel):
    resume_text: str
    job_description: str | None = None


class CoverLetterRequest(BaseModel):
    resume_text: str
    job_title: str
    company_name: str
    job_description: str
    tone: str = "professional"


class CareerSuggestRequest(BaseModel):
    resume_text: str
    preferences: str | None = None


class InterviewPrepRequest(BaseModel):
    job_title: str
    company_name: str
    job_description: str
    resume_text: str


@router.post("/chat")
async def chat(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start = time.monotonic()
    try:
        response = await gateway.generate(
            body.message,
            system_prompt="You are an expert AI Career Coach helping users with job search, resume optimization, interview preparation, and career advice. Be concise, practical, and encouraging.",
        )
        latency = int((time.monotonic() - start) * 1000)
        await log_ai_request(
            db=db, user_id=current_user.id, agent_type="chat", status="success",
            model=response.model, prompt_tokens=response.tokens_in or 0,
            completion_tokens=response.tokens_out or 0, latency_ms=latency,
            cache_hit=response.cached or False,
        )
        return {"role": "assistant", "content": response.content, "provider": response.provider, "cached": response.cached}
    except Exception as e:
        latency = int((time.monotonic() - start) * 1000)
        await log_ai_request(
            db=db, user_id=current_user.id, agent_type="chat", status="error",
            latency_ms=latency, error_message=str(e),
        )
        raise


@router.post("/analyze")
async def analyze(
    body: AnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start = time.monotonic()
    try:
        result = await gateway.analyze_resume(body.resume_text, body.job_description)
        latency = int((time.monotonic() - start) * 1000)
        await log_ai_request(
            db=db, user_id=current_user.id, agent_type="resume_analysis", status="success",
            latency_ms=latency,
        )
        return result
    except Exception as e:
        latency = int((time.monotonic() - start) * 1000)
        await log_ai_request(
            db=db, user_id=current_user.id, agent_type="resume_analysis", status="error",
            latency_ms=latency, error_message=str(e),
        )
        raise


@router.post("/cover-letter")
async def cover_letter(
    body: CoverLetterRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start = time.monotonic()
    try:
        content = await gateway.generate_cover_letter(
            body.resume_text, body.job_title, body.company_name, body.job_description, body.tone
        )
        latency = int((time.monotonic() - start) * 1000)
        await log_ai_request(
            db=db, user_id=current_user.id, agent_type="cover_letter", status="success",
            latency_ms=latency,
        )
        return {"content": content}
    except Exception as e:
        latency = int((time.monotonic() - start) * 1000)
        await log_ai_request(
            db=db, user_id=current_user.id, agent_type="cover_letter", status="error",
            latency_ms=latency, error_message=str(e),
        )
        raise


@router.post("/career-suggest")
async def career_suggest(
    body: CareerSuggestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start = time.monotonic()
    try:
        result = await gateway.suggest_career_path(body.resume_text, body.preferences)
        latency = int((time.monotonic() - start) * 1000)
        await log_ai_request(
            db=db, user_id=current_user.id, agent_type="career_suggestion", status="success",
            latency_ms=latency,
        )
        return result
    except Exception as e:
        latency = int((time.monotonic() - start) * 1000)
        await log_ai_request(
            db=db, user_id=current_user.id, agent_type="career_suggestion", status="error",
            latency_ms=latency, error_message=str(e),
        )
        raise


@router.post("/interview-prep")
async def interview_prep(
    body: InterviewPrepRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start = time.monotonic()
    try:
        result = await gateway.interview_prep(
            body.job_title, body.company_name, body.job_description, body.resume_text
        )
        latency = int((time.monotonic() - start) * 1000)
        await log_ai_request(
            db=db, user_id=current_user.id, agent_type="interview_prep", status="success",
            latency_ms=latency,
        )
        return result
    except Exception as e:
        latency = int((time.monotonic() - start) * 1000)
        await log_ai_request(
            db=db, user_id=current_user.id, agent_type="interview_prep", status="error",
            latency_ms=latency, error_message=str(e),
        )
        raise
