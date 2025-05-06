from __future__ import annotations
import asyncio, json, os, signal
from uuid import UUID

import uvicorn
from aiokafka import AIOKafkaConsumer
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from starlette.concurrency import run_in_threadpool

from interfaces.ws.ws_manager import WebSocketManager
from infrastructure.redis.redis_manager import RedisManager
from application.services.send_message import SendMessageService
from application.dtos.commands import SendMessageCommand
from infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from infrastructure.db.session_factory import session_factory

# ------------ bootstrap singletons -------------------------------------
redis_mgr = RedisManager()
asyncio.get_event_loop().run_until_complete(redis_mgr.connect())

ws_manager = WebSocketManager(redis_mgr)

uow_factory = lambda: SqlAlchemyUnitOfWork(session_factory)
send_service = SendMessageService(uow_factory)

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")

# ------------ FastAPI ---------------------------------------------------
app = FastAPI()

async def current_user(ws: WebSocket) -> UUID:
    uid = ws.headers.get("x-user-id")
    if not uid:
        await ws.close(); raise RuntimeError("unauth")
    return UUID(uid)

@app.websocket("/ws")
async def ws_handler(ws: WebSocket, user_id: UUID = Depends(current_user)):
    await ws_manager.register(user_id, ws)
    try:
        while True:
            msg = await ws.receive_json()
            cmd = msg.get("cmd")
            if cmd == "ping":
                await ws_manager.heartbeat(user_id)
            elif cmd == "join_chat":
                await ws_manager.add_user_to_chat(UUID(msg["chatId"]), user_id)
            elif cmd == "leave_chat":
                await ws_manager.remove_user_from_chat(UUID(msg["chatId"]), user_id)
            elif cmd == "send_message":
                chat_id = UUID(msg["chatId"])
                text = msg["text"]
                cmd_obj = SendMessageCommand(chat_id, user_id, text)
                # run sync service in thread‑pool
                await run_in_threadpool(send_service.execute, cmd_obj)
            # ignore unknown commands
    except WebSocketDisconnect:
        pass
    finally:
        await ws_manager.unregister(user_id, ws)

# ------------ Kafka listener -------------------------------------------
async def kafka_loop() -> None:
    consumer = AIOKafkaConsumer(
        "messages",
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_deserializer=lambda b: json.loads(b.decode()),
        group_id="ws-gateway",
    )
    await consumer.start()
    try:
        async for rec in consumer:
            ev = rec.value          # expects {"chat_id": "...", ...}
            await ws_manager.broadcast_chat(UUID(ev["chat_id"]), ev)
    finally:
        await consumer.stop()

# ------------ main ------------------------------------------------------
async def main() -> None:
    loop = asyncio.get_running_loop()
    loop.create_task(kafka_loop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: loop.stop())

    config = uvicorn.Config(app, host="0.0.0.0", port=8000, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
