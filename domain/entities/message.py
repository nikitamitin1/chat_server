# domain/entities/message.py
from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum, auto
from typing import List

from domain.entities.attachment import Attachment


class MessageStatus(Enum):
    SENT = auto()
    DELIVERED = auto()
    READ = auto()
    DELETED = auto()                # мягкое удаление


@dataclass
class Message:
    id: UUID
    chat_id: UUID
    sender_id: UUID
    text: str

    reply_to_id: UUID | None = None
    attachments: List[Attachment] = field(default_factory=list)

    created_at: datetime = field(default_factory=datetime.utcnow)
    edited_at: datetime | None = None
    deleted_at: datetime | None = None
    status: MessageStatus = MessageStatus.SENT


    def edit(self, new_text: str) -> None:
        self._ensure_not_deleted()
        if not new_text:
            raise ValueError("Message text cannot be empty")
        if new_text == self.text:
            return
        self.text = new_text
        self.edited_at = datetime.utcnow()

    def mark_delivered(self) -> None:
        if self.status == MessageStatus.SENT:
            self.status = MessageStatus.DELIVERED

    def mark_read(self) -> None:
        if self.status in {MessageStatus.SENT, MessageStatus.DELIVERED}:
            self.status = MessageStatus.READ

    def add_attachment(self, att: Attachment) -> None:
        self._ensure_not_deleted()
        if any(a.id == att.id for a in self.attachments):
            raise ValueError(f"Attachment {att.id} already added")
        self.attachments.append(att)

    def remove_attachment(self, att_id: UUID) -> None:
        self._ensure_not_deleted()
        before = len(self.attachments)
        self.attachments = [a for a in self.attachments if a.id != att_id]
        if len(self.attachments) == before:
            raise ValueError(f"Attachment {att_id} not found")

    def soft_delete(self) -> None:
        if self.status == MessageStatus.DELETED:
            return
        self.deleted_at = datetime.utcnow()
        self.status = MessageStatus.DELETED

    def restore(self) -> None:
        if self.status != MessageStatus.DELETED:
            raise ValueError("Message not deleted")
        self.deleted_at = None
        self.status = MessageStatus.SENT

    def is_deleted(self) -> bool:
        return self.status == MessageStatus.DELETED

    def _ensure_not_deleted(self) -> None:
        if self.is_deleted():
            raise ValueError("Cannot modify a deleted message")

    @staticmethod
    def new(chat_id: UUID, sender_id: UUID, text: str,
            reply_to: UUID | None = None) -> "Message":
        if not text:
            raise ValueError("Message text cannot be empty")
        return Message(
            id=uuid4(),
            chat_id=chat_id,
            sender_id=sender_id,
            text=text,
            reply_to_id=reply_to,
        )
