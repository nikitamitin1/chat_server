"""
module: application/dtos/queries.py
Read‑side DTOs (“queries”) that travel from controllers to query‑handlers /
use‑cases.  Each class is an immutable container describing WHAT to fetch
—not HOW.  They never contain persistence logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


# ───────────────────────────────────────────────────────────────────────────
#  User / Profile / Presence
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class GetUserProfileQuery:
    user_id: UUID                     # fetch single user profile


@dataclass(frozen=True)
class SearchUsersQuery:
    search_text: str                  # by username / display name
    cursor: Optional[UUID] = None     # opaque paging cursor
    limit: int = 30


@dataclass(frozen=True)
class GetUserStatusQuery:
    user_id: UUID                     # current ONLINE / AWAY / … status


# ───────────────────────────────────────────────────────────────────────────
#  Chat list & membership
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ListChatsForUserQuery:
    user_id: UUID
    cursor: Optional[UUID] = None
    limit: int = 20                   # paginated chat list


@dataclass(frozen=True)
class GetChatDetailsQuery:
    chat_id: UUID                     # title, type, created_at, etc.


@dataclass(frozen=True)
class ListChatMembersQuery:
    chat_id: UUID
    role_filter: Optional[str] = None   # "ADMIN", "OWNER", …
    cursor: Optional[UUID] = None
    limit: int = 50


# ───────────────────────────────────────────────────────────────────────────
#  Message history & search
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class GetChatHistoryQuery:
    chat_id: UUID
    cursor: Optional[UUID] = None       # message‑id pagination
    limit: int = 50
    reverse: bool = False               # False → newest‑first


@dataclass(frozen=True)
class SearchMessagesQuery:
    chat_id: UUID
    text: str
    cursor: Optional[UUID] = None
    limit: int = 50


@dataclass(frozen=True)
class GetMessageDetailsQuery:
    message_id: UUID


# ───────────────────────────────────────────────────────────────────────────
#  Attachments & reactions
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ListAttachmentsQuery:
    message_id: UUID
    limit: int = 20
    cursor: Optional[UUID] = None


@dataclass(frozen=True)
class ListReactionsQuery:
    message_id: UUID
    cursor: Optional[UUID] = None
    limit: int = 50


# ───────────────────────────────────────────────────────────────────────────
#  Notifications
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ListNotificationsQuery:
    user_id: UUID
    unread_only: bool = False
    cursor: Optional[UUID] = None
    limit: int = 30


@dataclass(frozen=True)
class GetUnreadCountQuery:
    user_id: UUID                      # total unread notifications/messages


# ───────────────────────────────────────────────────────────────────────────
#  Presence
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ListOnlineMembersQuery:
    chat_id: UUID
    limit: int = 100                   # cap result, e.g., for very large chats
