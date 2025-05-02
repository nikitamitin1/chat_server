"""
module: domain/repositories.py
Repository *interfaces* that belong to the Domain/Application layers.
They define the contract for data access; concrete implementations
live in the Infrastructure layer (SQL, Redis, S3, …).

All methods are minimal but cover the operations we sketched earlier.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Protocol, TYPE_CHECKING
from uuid import UUID

# ──────────────────────────────────────────────────────────────────────────
# Domain entities (forward references only to avoid heavy imports here)
# ──────────────────────────────────────────────────────────────────────────
if TYPE_CHECKING:  # type‑checker only
    from domain.entities.message import Message
    from domain.entities.chat import Chat
    from domain.entities.user import User
    from domain.entities.notification import Notification
    from domain.entities.attachment import Attachment
    from domain.entities.chat_membership import ChatMembership
    from domain.events import DomainEvent


# ──────────────────────────────────────────────────────────────────────────
# Message repository
# ──────────────────────────────────────────────────────────────────────────
class MessageRepository(ABC):
    @abstractmethod
    def save(self, message: "Message") -> None: ...

    @abstractmethod
    def get_by_id(self, msg_id: UUID) -> "Message": ...

    @abstractmethod
    def delete(self, msg_id: UUID) -> None: ...

    @abstractmethod
    def update_text(self, msg_id: UUID, new_text: str) -> None: ...

    @abstractmethod
    def list_by_chat(
        self,
        chat_id: UUID,
        cursor: Optional[UUID],
        limit: int,
    ) -> List["Message"]: ...


# ──────────────────────────────────────────────────────────────────────────
# Chat repository
# ──────────────────────────────────────────────────────────────────────────
class ChatRepository(ABC):
    @abstractmethod
    def create(self, chat: "Chat") -> None: ...

    @abstractmethod
    def get_by_id(self, chat_id: UUID) -> "Chat": ...

    @abstractmethod
    def update_title(self, chat_id: UUID, title: str) -> None: ...

    @abstractmethod
    def add_user(self, chat_id: UUID, membership: "ChatMembership") -> None: ...

    @abstractmethod
    def remove_user(self, chat_id: UUID, user_id: UUID) -> None: ...

    @abstractmethod
    def list_for_user(
        self,
        user_id: UUID,
        cursor: Optional[UUID],
        limit: int,
    ) -> List["Chat"]: ...


# ──────────────────────────────────────────────────────────────────────────
# User repository
# ──────────────────────────────────────────────────────────────────────────
class UserRepository(ABC):
    @abstractmethod
    def save(self, user: "User") -> None: ...

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> "User": ...

    @abstractmethod
    def get_by_username(self, username: str) -> "User": ...

    @abstractmethod
    def update_profile(
        self,
        user_id: UUID,
        display_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> None: ...

    @abstractmethod
    def verify_credentials(self, username: str, password_hash: str) -> bool: ...


# ──────────────────────────────────────────────────────────────────────────
# Notification repository
# ──────────────────────────────────────────────────────────────────────────
class NotificationRepository(ABC):
    @abstractmethod
    def push(self, notification: "Notification") -> None: ...

    @abstractmethod
    def list_for_user(
        self,
        user_id: UUID,
        cursor: Optional[UUID],
        limit: int,
    ) -> List["Notification"]: ...

    @abstractmethod
    def mark_as_read(self, notification_id: UUID) -> None: ...


# ──────────────────────────────────────────────────────────────────────────
# Attachment repository
# ──────────────────────────────────────────────────────────────────────────
class AttachmentRepository(ABC):
    @abstractmethod
    def save(self, attachment: "Attachment") -> None: ...

    @abstractmethod
    def get_by_id(self, att_id: UUID) -> "Attachment": ...

    @abstractmethod
    def list_by_message(
        self,
        message_id: UUID,
        cursor: Optional[UUID],
        limit: int,
    ) -> List["Attachment"]: ...

    @abstractmethod
    def delete(self, att_id: UUID) -> None: ...


# ──────────────────────────────────────────────────────────────────────────
# Presence repository (online / offline / mute list)
# ──────────────────────────────────────────────────────────────────────────
class PresenceRepository(ABC):
    @abstractmethod
    def set_online(self, user_id: UUID, ttl_seconds: int) -> None: ...

    @abstractmethod
    def set_offline(self, user_id: UUID) -> None: ...

    @abstractmethod
    def is_online(self, user_id: UUID) -> bool: ...

    @abstractmethod
    def list_online_users(self, chat_id: UUID) -> List[UUID]: ...


# ──────────────────────────────────────────────────────────────────────────
# Outbox repository
# ──────────────────────────────────────────────────────────────────────────
class OutboxRepository(ABC):
    @abstractmethod
    def save(self, event: "DomainEvent") -> None: ...

    @abstractmethod
    def fetch_pending(self, limit: int) -> List["DomainEvent"]: ...

    @abstractmethod
    def mark_dispatched(self, event_id: UUID) -> None: ...



