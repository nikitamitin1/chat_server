# application/services/send_message.py
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID
from typing import Protocol

from application.dtos.commands import SendMessageCommand          # ⇦ already defined
from application.unit_of_work import UnitOfWork                            # ⇦ interface in application layer
from domain.entities.message import Message
from domain.events import MessageSent                # ⇦ domain event dataclass


# ───────────────────────────────────────────────────────────────────────
#  Custom error returned to controllers / UI
# ───────────────────────────────────────────────────────────────────────
class ForbiddenError(Exception):
    """Raised when the sender is not a member of the target chat."""


# ───────────────────────────────────────────────────────────────────────
#  Service / Use‑case
# ───────────────────────────────────────────────────────────────────────
class SendMessageService:
    """
    Application‑layer orchestrator: one public method `execute`.
    Does NOT know about SQL, WebSocket, HTTP – only repos & UoW.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    # main entry point ---------------------------------------------------
    def execute(self, cmd: SendMessageCommand) -> UUID:
        """
        :param cmd:  DTO with chat_id, sender_id, text, reply_to_id
        :return:     UUID of the newly created message
        :raises ForbiddenError: if sender is not a chat member
        """
        with self.uow:                               # ← open single DB tx
            # 1. fetch aggregate
            chat = self.uow.chats.get_by_id(cmd.chat_id)

            # 2. business rule: sender must be member
            if not chat.has_member(cmd.sender_id):
                raise ForbiddenError("Sender is not a chat member")

            # 3. create domain entity
            message = Message.new(
                chat_id=cmd.chat_id,
                sender_id=cmd.sender_id,
                text=cmd.text,
                reply_to=cmd.reply_to_id,
            )

            # 4. mutate aggregate or counters if needed (here: none)

            # 5. persist through repositories
            self.uow.messages.save(message)

            # 6. raise domain event and store into outbox
            event = MessageSent(
                message_id=message.id,
                chat_id=message.chat_id,
                sender_id=message.sender_id,
            )
            self.uow.outbox.save(event)

            # 7. uow.__exit__ will commit; return the new id
            return message.id