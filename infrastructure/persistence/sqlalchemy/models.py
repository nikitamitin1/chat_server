from __future__ import annotations

import json
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import (
    Table,
    Column,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    LargeBinary,
    Enum,
    Integer,
    select,
    delete,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Session, Mapped, mapped_column, registry, relationship

from domain.entities import (
    message as ent_msg,
    chat as ent_chat,
    user as ent_user,
    notification as ent_notif,
    attachment as ent_att,
    chat_membership as ent_membership,
)
from domain.events import DomainEvent
from domain.repositories import (
    MessageRepository,
    ChatRepository,
    UserRepository,
    NotificationRepository,
    AttachmentRepository,
    OutboxRepository,
)


mapper_registry = registry()
metadata = mapper_registry.metadata


# ───────────────────────────────────────────────────────────────────────────
#  ORM  MODELS
# ───────────────────────────────────────────────────────────────────────────

@mapper_registry.mapped
class ChatModel:
    __tablename__ = "chats"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    type: Mapped[str]
    title: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime | None]

    members: Mapped[List["ChatMemberModel"]] = relationship(
        back_populates="chat", cascade="all,delete-orphan", lazy="selectin"
    )


@mapper_registry.mapped
class ChatMemberModel:
    __tablename__ = "chat_members"

    chat_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("chats.id"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    role: Mapped[str]
    joined_at: Mapped[datetime]
    muted_until: Mapped[datetime | None]

    chat: Mapped["ChatModel"] = relationship(back_populates="members")


@mapper_registry.mapped
class MessageModel:
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chats.id"))
    sender_id: Mapped[UUID]
    text: Mapped[str]
    status: Mapped[str]
    reply_to_id: Mapped[UUID | None]
    created_at: Mapped[datetime]
    edited_at: Mapped[datetime | None]
    deleted_at: Mapped[datetime | None]

    attachments: Mapped[List["AttachmentModel"]] = relationship(
        back_populates="message", cascade="all, delete-orphan", lazy="selectin"
    )


@mapper_registry.mapped
class AttachmentModel:
    __tablename__ = "attachments"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    message_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("messages.id")
    )
    type: Mapped[str]
    file_name: Mapped[str]
    url: Mapped[str]
    size: Mapped[int]
    mime_type: Mapped[str]
    width: Mapped[int | None]
    height: Mapped[int | None]
    duration_sec: Mapped[float | None]
    created_at: Mapped[datetime]
    uploaded_at: Mapped[datetime | None]

    message: Mapped[MessageModel] = relationship(back_populates="attachments")


@mapper_registry.mapped
class UserModel:
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    username: Mapped[str]
    email: Mapped[str]
    password_hash: Mapped[str]
    display_name: Mapped[str]
    avatar_url: Mapped[str | None]
    status: Mapped[str]
    created_at: Mapped[datetime]
    last_seen: Mapped[datetime]
    is_active: Mapped[bool]


@mapper_registry.mapped
class NotificationModel:
    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID]
    type: Mapped[str]
    payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime]
    read_at: Mapped[datetime | None]
    seen_at: Mapped[datetime | None]
    is_sent: Mapped[bool]


@mapper_registry.mapped
class OutboxModel:
    __tablename__ = "outbox"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    type: Mapped[str]
    payload: Mapped[dict] = mapped_column(JSONB)
    occurred_at: Mapped[datetime]
    dispatched: Mapped[bool]
    dispatched_at: Mapped[datetime | None]