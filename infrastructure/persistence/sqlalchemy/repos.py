"""
infrastructure/persistence/sqlalchemy/repositories.py
Concrete SQLAlchemy repositories.
Imports:
    • models    – ORM declarations for every table
    • mappers   – helpers entity ⇄ ORM
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from domain.events import DomainEvent
from domain.repositories import (
    MessageRepository,
    ChatRepository,
    UserRepository,
    NotificationRepository,
    AttachmentRepository,
    OutboxRepository,
)

# local imports (same directory)
from . import models as mdl          # models.py
from . import mappers as map_        # mappers.py


# ───────────────────────────────────────────────────────────────────────────
#  Message repository
# ───────────────────────────────────────────────────────────────────────────

class SqlMessageRepository(MessageRepository):
    def __init__(self, session: Session):
        self.session = session

    # write
    def save(self, message):
        self.session.merge(map_.message_to_model(message))

    def delete(self, msg_id: UUID):
        self.session.execute(delete(mdl.MessageModel).where(mdl.MessageModel.id == msg_id))

    def update_text(self, msg_id: UUID, new_text: str):
        self.session.execute(
            mdl.MessageModel.__table__
            .update()
            .where(mdl.MessageModel.id == msg_id)
            .values(text=new_text, edited_at=datetime.utcnow())
        )

    # read
    def get_by_id(self, msg_id: UUID):
        row = self.session.get(mdl.MessageModel, msg_id)
        if row is None:
            raise KeyError("Message not found")
        return map_.model_to_message(row)

    def list_by_chat(self, chat_id: UUID, cursor: Optional[UUID], limit: int):
        q = (
            select(mdl.MessageModel)
            .where(mdl.MessageModel.chat_id == chat_id)
            .order_by(mdl.MessageModel.created_at.desc())
            .limit(limit)
        )
        if cursor:
            pivot = self.session.get(mdl.MessageModel, cursor)
            q = q.where(mdl.MessageModel.created_at < pivot.created_at)
        return [map_.model_to_message(r) for r in self.session.scalars(q).all()]


# ───────────────────────────────────────────────────────────────────────────
#  Chat repository
# ───────────────────────────────────────────────────────────────────────────

class SqlChatRepository(ChatRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, chat):
        self.session.add(map_.chat_to_model(chat))

    def get_by_id(self, chat_id: UUID):
        row = self.session.get(mdl.ChatModel, chat_id)
        if row is None:
            raise KeyError("Chat not found")
        return map_.model_to_chat(row)

    def update_title(self, chat_id: UUID, title: str):
        self.session.execute(
            mdl.ChatModel.__table__
            .update()
            .where(mdl.ChatModel.id == chat_id)
            .values(title=title, updated_at=datetime.utcnow())
        )

    def add_user(self, chat_id: UUID, membership):
        self.session.add(map_.membership_to_model(membership))

    def remove_user(self, chat_id: UUID, user_id: UUID):
        self.session.execute(
            delete(mdl.ChatMemberModel).where(
                (mdl.ChatMemberModel.chat_id == chat_id)
                & (mdl.ChatMemberModel.user_id == user_id)
            )
        )

    def list_for_user(self, user_id: UUID, cursor: Optional[UUID], limit: int):
        sub = (
            select(mdl.ChatMemberModel.chat_id)
            .where(mdl.ChatMemberModel.user_id == user_id)
            .subquery()
        )
        q = (
            select(mdl.ChatModel)
            .where(mdl.ChatModel.id.in_(sub))
            .order_by(mdl.ChatModel.updated_at.desc())
            .limit(limit)
        )
        rows = self.session.scalars(q).all()
        return [map_.model_to_chat(r) for r in rows]


# ───────────────────────────────────────────────────────────────────────────
#  User repository
# ───────────────────────────────────────────────────────────────────────────

class SqlUserRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, user):
        self.session.merge(map_.user_to_model(user))
    def get_by_id(self, user_id: UUID):
        row = self.session.get(mdl.UserModel, user_id)
        if row is None:
            raise KeyError
        return map_.model_to_user(row)
    
    def get_by_username(self, username: str):
        row = self.session.scalar(select(mdl.UserModel).where(mdl.UserModel.username == username))
        if row is None:
            raise KeyError
        return map_.model_to_user(row)

    def update_profile(self, user_id: UUID, display_name: str | None, avatar_url: str | None):
        self.session.execute(
            mdl.UserModel.__table__
            .update()
            .where(mdl.UserModel.id == user_id)
            .values(display_name=display_name, avatar_url=avatar_url)
        )

    def verify_credentials(self, username: str, password_hash: str) -> bool:
        row = self.session.scalar(select(mdl.UserModel).where(mdl.UserModel.username == username))
        return bool(row and row.password_hash == password_hash)


# ───────────────────────────────────────────────────────────────────────────
#  Notification repository
# ───────────────────────────────────────────────────────────────────────────

class SqlNotificationRepository(NotificationRepository):
    def __init__(self, session: Session):
        self.session = session

    def push(self, notification):
        self.session.add(map_.notification_to_model(notification))

    def list_for_user(self, user_id: UUID, cursor: Optional[UUID], limit: int):
        q = (
            select(mdl.NotificationModel)
            .where(mdl.NotificationModel.user_id == user_id)
            .order_by(mdl.NotificationModel.created_at.desc())
            .limit(limit)
        )
        if cursor:
            pivot = self.session.get(mdl.NotificationModel, cursor)
            q = q.where(mdl.NotificationModel.created_at < pivot.created_at)
        rows = self.session.scalars(q).all()
        return [map_.model_to_notification(r) for r in rows]

    def mark_as_read(self, notification_id: UUID):
        self.session.execute(
            mdl.NotificationModel.__table__
            .update()
            .where(mdl.NotificationModel.id == notification_id)
            .values(read_at=datetime.utcnow())
        )


# ───────────────────────────────────────────────────────────────────────────
#  Attachment repository
# ───────────────────────────────────────────────────────────────────────────

class SqlAttachmentRepository(AttachmentRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, attachment):
        self.session.merge(map_.attachment_to_model(attachment))

    def get_by_id(self, att_id: UUID):
        row = self.session.get(mdl.AttachmentModel, att_id)
        if row is None:
            raise KeyError
        return map_.model_to_attachment(row)

    def list_by_message(self, message_id: UUID, limit: int):
        rows = self.session.scalars(
            select(mdl.AttachmentModel)
            .where(mdl.AttachmentModel.message_id == message_id)
            .limit(limit)
        ).all()
        return [map_.model_to_attachment(r) for r in rows]

    def delete(self, att_id: UUID):
        self.session.execute(delete(mdl.AttachmentModel).where(mdl.AttachmentModel.id == att_id))


# ───────────────────────────────────────────────────────────────────────────
#  Outbox repository
# ───────────────────────────────────────────────────────────────────────────

class SqlOutboxRepository(OutboxRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, event: DomainEvent):
        self.session.add(
            mdl.OutboxModel(
                id=event.id,
                type=event.__class__.__name__,
                payload=event.to_dict(),
                occurred_at=event.occurred_at,
                dispatched=False,
            )
        )

    def fetch_pending(self, limit: int):
        rows = self.session.scalars(
            select(mdl.OutboxModel)
            .where(mdl.OutboxModel.dispatched.is_(False))
            .limit(limit)
        ).all()
        return [DomainEvent.from_dict(r.payload) for r in rows]

    def mark_dispatched(self, event_id: UUID):
        self.session.execute(
            mdl.OutboxModel.__table__
            .update()
            .where(mdl.OutboxModel.id == event_id)
            .values(dispatched=True, dispatched_at=datetime.utcnow())
        )
