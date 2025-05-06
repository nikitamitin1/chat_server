from __future__ import annotations
import asyncio, json
from typing import Dict, Set
from uuid import UUID
from fastapi import WebSocket
from infrastructure.redis.redis_manager import RedisManager

ONLINE_TTL = 40               # seconds; refreshed each ping

class WebSocketManager:
    """
    • Local map:   _user_sockets[user_id] -> set[WebSocket]
    • Redis sets:  chat:{chat_id}         -> members
    • Redis key:   online:{user_id}       -> TTL heartbeat
    """

    def __init__(self, redis: RedisManager):
        self.redis = redis
        self._user_sockets: Dict[UUID, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    # ----------- connect / disconnect -----------------------------------
    async def register(self, user_id: UUID, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._user_sockets.setdefault(user_id, set()).add(ws)
        await self.redis.set_json(f"online:{user_id}", 1, ex=ONLINE_TTL)

    async def unregister(self, user_id: UUID, ws: WebSocket) -> None:
        async with self._lock:
            self._user_sockets.get(user_id, set()).discard(ws)
            if not self._user_sockets.get(user_id):
                self._user_sockets.pop(user_id, None)
        # Let TTL expire naturally for presence

    async def heartbeat(self, user_id: UUID) -> None:
        await self.redis.expire(f"online:{user_id}", ONLINE_TTL)

    # ----------- chat membership in Redis -------------------------------
    async def add_user_to_chat(self, chat_id: UUID, user_id: UUID) -> None:
        await self.redis.sadd(f"chat:{chat_id}", str(user_id))

    async def remove_user_from_chat(self, chat_id: UUID, user_id: UUID) -> None:
        await self.redis.srem(f"chat:{chat_id}", str(user_id))

    # ----------- sending helpers ----------------------------------------
    async def _send_local(self, user_id: UUID, payload: dict) -> None:
        for ws in self._user_sockets.get(user_id, set()).copy():
            try:
                await ws.send_json(payload)
            except Exception:
                await self.unregister(user_id, ws)

    async def send_to_user(self, user_id: UUID, payload: dict) -> None:
        await self._send_local(user_id, payload)        # may have sockets on this node

    async def broadcast_chat(self, chat_id: UUID, payload: dict) -> None:
        members = await self.redis.smembers(f"chat:{chat_id}")
        await asyncio.gather(*(self._send_local(UUID(uid), payload) for uid in members))
