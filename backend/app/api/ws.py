from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.user import User
from app.services.security import decode_token

router = APIRouter(tags=["ws"])


class _Hub:
    def __init__(self) -> None:
        self.channels: dict[str, set[WebSocket]] = defaultdict(set)
        self.lock = asyncio.Lock()

    async def join(self, channel: str, ws: WebSocket) -> None:
        async with self.lock:
            self.channels[channel].add(ws)

    async def leave(self, channel: str, ws: WebSocket) -> None:
        async with self.lock:
            self.channels[channel].discard(ws)

    async def broadcast(self, channel: str, message: dict[str, Any]) -> None:
        async with self.lock:
            sockets = list(self.channels.get(channel, set()))
        for s in sockets:
            try:
                await s.send_text(json.dumps(message))
            except Exception:
                pass


hub = _Hub()


def _user_from_token(token: str | None, db: Session) -> User | None:
    if not token:
        return None
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        return db.get(User, UUID(payload["sub"]))
    except Exception:
        return None


@router.websocket("/v1/ws/leaderboard/{contest_id}")
async def ws_leaderboard(
    websocket: WebSocket,
    contest_id: UUID,
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    user = _user_from_token(token, db)
    if user is None:
        await websocket.close(code=4401)
        return
    await websocket.accept()
    channel = f"contest:{contest_id}:leaderboard"
    await hub.join(channel, websocket)
    try:
        while True:
            await websocket.receive_text()  # heartbeat
    except WebSocketDisconnect:
        pass
    finally:
        await hub.leave(channel, websocket)


@router.websocket("/v1/ws/notifications")
async def ws_notifications(
    websocket: WebSocket,
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    user = _user_from_token(token, db)
    if user is None:
        await websocket.close(code=4401)
        return
    await websocket.accept()
    channel = f"user:{user.id}:notifications"
    await hub.join(channel, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await hub.leave(channel, websocket)
