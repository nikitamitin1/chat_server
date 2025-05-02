from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


class NotificationType(Enum):
    NEW_MESSAGE = auto()
    INVITE      = auto()
    MENTION     = auto()
    REACTION    = auto()
    SYSTEM      = auto()


@dataclass
class Notification:
    # ─── key fields ───────────────────────────────────────────────────
    id: UUID
    user_id: UUID
    type: NotificationType
    payload: Dict[str, Any]        # (chatId, msgId, …)

    # ─── meta data ─────────────────────────────────────────────────────
    created_at: datetime = field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    seen_at: Optional[datetime] = None
    is_sent: bool = False

    # --------------------------------------------------------------------
    #                  Domain Behavior
    # --------------------------------------------------------------------

    def mark_sent(self) -> None:
        self.is_sent = True

    def mark_seen(self) -> None:
        if self.seen_at is None:
            self.seen_at = datetime.utcnow()

    def mark_read(self) -> None:
        if self.read_at is None:
            self.read_at = datetime.utcnow()

    def is_unread(self) -> bool:
        return self.read_at is None

    @staticmethod
    def new(user_id: UUID,
            notif_type: NotificationType,
            payload: Dict[str, Any]) -> "Notification":
        if not payload:
            raise ValueError("Notification payload cannot be empty")
        return Notification(
            id=uuid4(),
            user_id=user_id,
            type=notif_type,
            payload=payload,
        )
