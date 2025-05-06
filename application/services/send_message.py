"""
application/services/send_message_service.py
────────────────────────────────────────────
Synchronous use‑case that handles the complete workflow of
“user sends a text message to a chat”.

Layers it touches
─────────────────
Domain       : builds `Message` aggregate.
Application  : enforces business rules.
Unit‑of‑Work : persists message + emits MessageSent event inside 1 DB tx.
Infrastructure: *not* referenced directly (decoupled via UoW interfaces).
"""

from __future__ import annotations

from typing import Callable
from uuid import UUID
from datetime import datetime

from application.dtos.commands import SendMessageCommand
from application.unit_of_work import UnitOfWork          # sync interface
from domain.entities.message import Message
from domain.entities.message import MessageStatus
from domain.events import MessageSent           # immutable dataclass


class ForbiddenError(Exception):
    """Raised when the sender is not a member of the chat or is muted."""


class SendMessageService:
    """
    One public method `execute()`.
    Accepts a UnitOfWork *factory* so the service itself remains stateless and
    can be reused in any synchronous context (FastAPI thread, Celery task, …).
    """

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    # ----------------------------------------------------------------─ API
    def execute(self, cmd: SendMessageCommand) -> UUID:
        """
        Persist a new message and publish MessageSent to the outbox.

        Returns
        -------
        UUID  – id of the newly created message (for optimistic UI).

        Raises
        ------
        ForbiddenError  – if sender is not allowed to post into the chat.
        """
        with self._uow_factory() as uow:
            # 1.  Load chat aggregate to validate membership / mutes
            chat = uow.chats.get_by_id(cmd.chat_id)

            member = chat.get_member(cmd.sender_id)
            if not member:
                raise ForbiddenError("Sender is not a member of this chat")
            if member.is_muted():
                raise ForbiddenError("Sender is currently muted")

            # 2.  Build domain entity
            message = Message.new(
                chat_id=cmd.chat_id,
                sender_id=cmd.sender_id,
                text=cmd.text,
            )

            # 3.  Persist message
            uow.messages.save(message)

            # 4.  Emit domain event -> Outbox
            uow.outbox.save(
                MessageSent(
                    message_id=message.id,
                    chat_id=message.chat_id,
                    sender_id=message.sender_id,
                    occurred_at=datetime.utcnow(),
                )
            )

            # 5.  Transaction commits automatically on __exit__
            return message.id
