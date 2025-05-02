"""
module: application/dtos/views.py
Flat “view” / response DTOs returned by read use‑cases.
All fields are JSON‑serialisable scalars (str, int, bool, lists).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID


# ───────────────────────────────────────────────────────────────────────────
#  User / Profile / Presence
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class UserProfileView:
    id: UUID
    username: str
    display_name: str
    avatar_url: Optional[str]
    created_at: str                 # ISO‑8601
    status: str                     # "ONLINE" | "AWAY" | "OFFLINE" | "DND"


@dataclass(frozen=True)
class UserStatusView:
    user_id: UUID
    status: str                     # same enum as above
    last_seen: str                  # ISO‑8601


# ───────────────────────────────────────────────────────────────────────────
#  Chat list & details
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ChatSummaryView:
    id: UUID
    title: str
    chat_type: str                  # "PRIVATE" | "GROUP"
    unread_count: int
    last_message_preview: Optional[str]
    last_activity_at: str           # ISO‑8601


@dataclass(frozen=True)
class ChatDetailsView:
    id: UUID
    title: str
    chat_type: str
    created_at: str
    member_count: int
    admins: List[UUID]              # list of user IDs


@dataclass(frozen=True)
class ChatMemberView:
    user_id: UUID
    role: str                       # "OWNER" | "ADMIN" | "MEMBER"
    joined_at: str
    muted_until: Optional[str]


# ───────────────────────────────────────────────────────────────────────────
#  Messages
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class MessageView:
    id: UUID
    chat_id: UUID
    sender_id: UUID
    text: str
    created_at: str                 # ISO‑8601
    edited_at: Optional[str]
    status: str                     # "SENT" | "DELIVERED" | "READ" | "DELETED"
    reply_to_id: Optional[UUID]
    attachments: List["AttachmentView"]
    reactions: List["ReactionView"]


# ───────────────────────────────────────────────────────────────────────────
#  Attachments & reactions
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AttachmentView:
    id: UUID
    type: str                       # "IMAGE" | "VIDEO" | ...
    file_name: str
    url: str
    size: int
    mime_type: str
    width: Optional[int]
    height: Optional[int]
    duration_sec: Optional[float]


@dataclass(frozen=True)
class ReactionView:
    user_id: UUID
    emoji: str
    added_at: str


# ───────────────────────────────────────────────────────────────────────────
#  Notifications
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class NotificationView:
    id: UUID
    type: str                       # "NEW_MESSAGE", "INVITE", ...
    payload: dict
    created_at: str
    read_at: Optional[str]
    seen_at: Optional[str]


# ───────────────────────────────────────────────────────────────────────────
#  Presence
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class OnlineMemberView:
    user_id: UUID
    status: str                     # "ONLINE", "AWAY", "DND"
