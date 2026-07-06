"""WebSocket endpoint for real-time notifications and updates."""
import asyncio
import json
import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, async_session_factory
from app.core.redis import redis_client
from app.models.user import User
from app.core.security import decode_token

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active: dict[str, list[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active:
            self.active[user_id] = []
        self.active[user_id].append(websocket)
        logger.info(f"WebSocket connected: user={user_id}")

    def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in self.active:
            self.active[user_id] = [ws for ws in self.active[user_id] if ws != websocket]
            if not self.active[user_id]:
                del self.active[user_id]
        logger.info(f"WebSocket disconnected: user={user_id}")

    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.active:
            for ws in self.active[user_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    pass

    async def broadcast(self, message: dict):
        for user_id in list(self.active.keys()):
            await self.send_to_user(user_id, message)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await manager.connect(user_id, websocket)

    try:
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(f"user:{user_id}")

        async def read_redis():
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await websocket.send_json(data)
                    except Exception:
                        pass

        async def read_ws():
            while True:
                try:
                    data = await websocket.receive_json()
                    if data.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                except WebSocketDisconnect:
                    break

        await asyncio.gather(read_redis(), read_ws())
    except Exception:
        pass
    finally:
        await pubsub.unsubscribe(f"user:{user_id}")
        await pubsub.close()
        manager.disconnect(user_id, websocket)


async def notify_user(user_id: str, event: str, data: dict):
    message = {"type": event, "data": data}
    await redis_client.publish(f"user:{user_id}", json.dumps(message))
    await manager.send_to_user(user_id, message)
