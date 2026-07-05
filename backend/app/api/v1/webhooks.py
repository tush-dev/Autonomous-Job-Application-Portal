from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db

router = APIRouter()
logger = structlog.get_logger()


@router.post("/clerk")
async def clerk_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.json()
    logger.info("clerk_webhook", event=payload.get("type"))
    return {"success": True}
