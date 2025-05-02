"""
module: domain/events.py
All domain‑level events for the messenger, gathered in one place.
Events are immutable dataclasses that live in the Domain layer and
can be persisted to the Outbox table for reliable publication.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


# ──────────────────────────────────────────────────────────────────────────
# Base event
# ──────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Common base: each event has a unique id and timestamp."""
    id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    # Small helper for (de)serialisation
    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.__class__.__name__, **asdict(self)}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainEvent":  # noqa: ANN401
        ev_type = data.pop("type")
        # Dynamic import is possible; here we assume same module
        return globals()[ev_type](**data)  # type: ignore[arg-type]


# ──────────────────────────────────────────────────────────────────────────
# Chat‑level events
# ──────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class ChatCreated(DomainEvent):
    chat_id: UUID
    creator_id: UUID
    chat_type: str  # "PRIVATE" | "GROUP"


@dataclass(frozen=True, slots=True)
class ChatTitleUpdated(DomainEvent):
    chat_id: UUID
    title: str
    updated_by: UUID


@dataclass(frozen=True, slots=True)
class ChatDeleted(DomainEvent):
    chat_id: UUID
    deleted_by: UUID


@dataclass(frozen=True, slots=True)
class UserJoinedChat(DomainEvent):
    chat_id: UUID
    user_id: UUID
    invited_by: Optional[UUID] = None


@dataclass(frozen=True, slots=True)
class UserLeftChat(DomainEvent):
    chat_id: UUID
    user_id: UUID


@dataclass(frozen=True, slots=True)
class UserRemovedFromChat(DomainEvent):
    chat_id: UUID
    user_id: UUID
    removed_by: UUID


@dataclass(frozen=True, slots=True)
class UserMutedInChat(DomainEvent):
    chat_id: UUID
    user_id: UUID
    muted_until: datetime
    muted_by: UUID


@dataclass(frozen=True, slots=True)
class UserUnmutedInChat(DomainEvent):
    chat_id: UUID
    user_id: UUID
    unmuted_by: UUID


# ──────────────────────────────────────────────────────────────────────────
# Message‑level events
# ──────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class MessageSent(DomainEvent):
    message_id: UUID
    chat_id: UUID
    sender_id: UUID


@dataclass(frozen=True, slots=True)
class MessageEdited(DomainEvent):
    message_id: UUID
    chat_id: UUID
    editor_id: UUID


@dataclass(frozen=True, slots=True)
class MessageDeleted(DomainEvent):
    message_id: UUID
    chat_id: UUID
    deleted_by: UUID


@dataclass(frozen=True, slots=True)
class MessageDelivered(DomainEvent):
    message_id: UUID
    recipient_id: UUID


@dataclass(frozen=True, slots=True)
class MessageRead(DomainEvent):
    message_id: UUID
    reader_id: UUID


# ──────────────────────────────────────────────────────────────────────────
# Attachment / reaction events
# ──────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class AttachmentAdded(DomainEvent):
    attachment_id: UUID
    message_id: UUID
    uploader_id: UUID
    mime_type: str


@dataclass(frozen=True, slots=True)
class AttachmentRemoved(DomainEvent):
    attachment_id: UUID
    message_id: UUID
    removed_by: UUID


@dataclass(frozen=True, slots=True)
class ReactionAdded(DomainEvent):
    message_id: UUID
    chat_id: UUID
    user_id: UUID
    emoji: str


@dataclass(frozen=True, slots=True)
class ReactionRemoved(DomainEvent):
    message_id: UUID
    chat_id: UUID
    user_id: UUID
    emoji: str


# ──────────────────────────────────────────────────────────────────────────
# Notification / presence events
# ──────────────────────────────────────────────────────────────────────────

class UserStatus(Enum):
    OFFLINE = auto()
    ONLINE = auto()
    AWAY = auto()
    DND = auto()


@dataclass(frozen=True, slots=True)
class NotificationCreated(DomainEvent):
    notification_id: UUID
    user_id: UUID
    notif_type: str  # e.g. "NEW_MESSAGE", "INVITE"


@dataclass(frozen=True, slots=True)
class NotificationRead(DomainEvent):
    notification_id: UUID
    user_id: UUID


@dataclass(frozen=True, slots=True)
class UserStatusChanged(DomainEvent):
    user_id: UUID
    old_status: UserStatus
    new_status: UserStatus
