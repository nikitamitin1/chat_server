from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Optional
from uuid import UUID


class ChatRole(Enum):
    OWNER = auto()
    ADMIN = auto()
    MEMBER = auto()


@dataclass
class ChatMembership:
    """
    Represents the relationship between a user and a chat.
    Lives inside the Chat aggregate.
    """
    chat_id: UUID
    user_id: UUID
    role: ChatRole = ChatRole.MEMBER
    joined_at: datetime = field(default_factory=datetime.utcnow)
    muted_until: Optional[datetime] = None         # if the user is muted

    # ── domain behaviour ────────────────────────────────────────────────
    def promote_to_admin(self) -> None:
        """Upgrade role to ADMIN (only an OWNER can do this in the use-case)."""
        if self.role is ChatRole.ADMIN:
            return
        if self.role is ChatRole.OWNER:
            raise ValueError("Owner already has highest privileges")
        self.role = ChatRole.ADMIN

    def demote_to_member(self) -> None:
        """Downgrade role to MEMBER (cannot demote OWNER)."""
        if self.role is ChatRole.OWNER:
            raise ValueError("Cannot demote the chat owner")
        self.role = ChatRole.MEMBER

    # ― mute / un-mute ― --------------------------------------------------
    def mute(self, duration: timedelta) -> None:
        """Mute the member for a given duration."""
        if duration.total_seconds() <= 0:
            raise ValueError("Mute duration must be positive")
        self.muted_until = datetime.utcnow() + duration

    def unmute(self) -> None:
        """Remove any active mute."""
        self.muted_until = None

    def is_muted(self, now: datetime | None = None) -> bool:
        """Returns True if the member is currently muted."""
        if self.muted_until is None:
            return False
        now = now or datetime.utcnow()
        return now < self.muted_until

    # ― helper predicates ― ----------------------------------------------
    def is_owner(self) -> bool:
        return self.role is ChatRole.OWNER

    def is_admin(self) -> bool:
        return self.role is ChatRole.ADMIN

    def can_invite_users(self) -> bool:
        """Simple rule: OWNER and ADMIN can invite others."""
        return self.role in {ChatRole.OWNER, ChatRole.ADMIN}
