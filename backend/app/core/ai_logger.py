import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.misc import AIRequest, ActivityLog, AuditLog


async def log_ai_request(
    db: AsyncSession,
    user_id: uuid.UUID,
    agent_type: str,
    status: str,
    model: str = "unknown",
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    latency_ms: int = 0,
    cost_cents: int = 0,
    error_message: Optional[str] = None,
    cache_hit: bool = False,
):
    record = AIRequest(
        user_id=user_id,
        agent_type=agent_type,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        latency_ms=latency_ms,
        cost_cents=cost_cents,
        status=status,
        error_message=error_message,
        cache_hit=cache_hit,
    )
    db.add(record)
    await db.flush()


async def log_activity(
    db: AsyncSession,
    user_id: uuid.UUID,
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    record = ActivityLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(record)
    await db.flush()


async def log_audit(
    db: AsyncSession,
    actor_id: Optional[uuid.UUID],
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    record = AuditLog(
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(record)
    await db.flush()
