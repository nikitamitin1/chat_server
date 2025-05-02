from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Optional
from uuid import UUID, uuid4


class UserStatus(Enum):
    OFFLINE = auto()
    ONLINE = auto()
    AWAY = auto()
    DND = auto()             # «Не беспокоить»


@dataclass
class User:
    id: UUID
    username: str
    email: str
    password_hash: str

    display_name: str
    avatar_url: Optional[str] = None

    created_at: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    status: UserStatus = UserStatus.OFFLINE
    is_active: bool = True


    def go_online(self) -> None:
        self._ensure_active()
        self.status = UserStatus.ONLINE
        self.last_seen = datetime.utcnow()

    def set_status(self, new_status: UserStatus) -> None:
        self._ensure_active()
        if new_status == UserStatus.OFFLINE:
            raise ValueError("Use go_offline() to set OFFLINE status")
        self.status = new_status
        self.last_seen = datetime.utcnow()

    def go_offline(self) -> None:
        self._ensure_active()
        self.status = UserStatus.OFFLINE
        self.last_seen = datetime.utcnow()

    def update_profile(self, *, display_name: Optional[str] = None,
                       avatar_url: Optional[str] = None) -> None:
        self._ensure_active()
        if display_name is not None:
            if not display_name.strip():
                raise ValueError("Display name cannot be empty")
            self.display_name = display_name
        if avatar_url is not None:
            self.avatar_url = avatar_url

    def deactivate(self) -> None:
        """GDPR-friendly user soft delete."""
        self.is_active = False
        self.status = UserStatus.OFFLINE
        self.last_seen = datetime.utcnow()

    def reactivate(self) -> None:
        self.is_active = True
        self.status = UserStatus.OFFLINE
        self.last_seen = datetime.utcnow()

    def change_password(self, new_password_hash: str) -> None:
        self._ensure_active()
        if not new_password_hash:
            raise ValueError("Password hash cannot be empty")
        self.password_hash = new_password_hash

    def seen_recently(self, *, within: timedelta = timedelta(minutes=5)) -> bool:
        return datetime.utcnow() - self.last_seen <= within


    @staticmethod
    def new(username: str, email: str, password_hash: str,
            display_name: Optional[str] = None,
            avatar_url: Optional[str] = None) -> "User":
        if not username or not password_hash or not email:
            raise ValueError("Username, email and password are required")
        return User(
            id=uuid4(),
            username=username,
            email=email,
            password_hash=password_hash,
            display_name=display_name or username,
            avatar_url=avatar_url,
        )

    def _ensure_active(self) -> None:
        if not self.is_active:
            raise ValueError("Inactive user cannot be modified")
