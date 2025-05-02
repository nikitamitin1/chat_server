"""
module: application/dtos/commands.py
Pure‑data DTOs (no logic) that travel from transport‑layer
controllers to use‑cases.  Each represents *one* user scenario.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID


# ───────────────────────────────────────────────────────────────────────────
#  User / Auth
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class RegisterUserCommand:
    username: str
    email: str
    password_hash: str                       # already hashed on client/edge

@dataclass(frozen=True)
class AuthenticateUserCommand:
    username: str
    password_hash: str

@dataclass(frozen=True)
class RefreshTokenCommand:
    refresh_token: str

@dataclass(frozen=True)
class UpdateUserProfileCommand:
    user_id: UUID
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None

@dataclass(frozen=True)
class ChangePasswordCommand:
    user_id: UUID
    new_password_hash: str


# ───────────────────────────────────────────────────────────────────────────
#  Chat & Membership
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class CreateChatCommand:
    creator_id: UUID
    chat_type: str                  # "PRIVATE" | "GROUP"
    title: str
    initial_member_ids: Optional[List[UUID]] = None  # for group creation

@dataclass(frozen=True)
class UpdateChatTitleCommand:
    chat_id: UUID
    updater_id: UUID
    new_title: str

@dataclass(frozen=True)
class DeleteChatCommand:
    chat_id: UUID
    deleter_id: UUID

@dataclass(frozen=True)
class InviteUsersCommand:
    chat_id: UUID
    inviter_id: UUID
    users_to_invite: List[UUID]

@dataclass(frozen=True)
class RemoveUserFromChatCommand:
    chat_id: UUID
    remover_id: UUID
    user_id: UUID

@dataclass(frozen=True)
class LeaveChatCommand:
    chat_id: UUID
    leaver_id: UUID

@dataclass(frozen=True)
class PromoteMemberCommand:
    chat_id: UUID
    promoter_id: UUID
    member_id: UUID

@dataclass(frozen=True)
class DemoteMemberCommand:
    chat_id: UUID
    demoter_id: UUID
    member_id: UUID

@dataclass(frozen=True)
class MuteMemberCommand:
    chat_id: UUID
    muter_id: UUID
    member_id: UUID
    muted_until: datetime

@dataclass(frozen=True)
class UnmuteMemberCommand:
    chat_id: UUID
    unmuter_id: UUID
    member_id: UUID


# ───────────────────────────────────────────────────────────────────────────
#  Messages
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SendMessageCommand:
    chat_id: UUID
    sender_id: UUID
    text: str
    reply_to_id: Optional[UUID] = None

@dataclass(frozen=True)
class EditMessageCommand:
    message_id: UUID
    editor_id: UUID
    new_text: str

@dataclass(frozen=True)
class DeleteMessageCommand:
    message_id: UUID
    deleter_id: UUID

@dataclass(frozen=True)
class MarkMessageDeliveredCommand:
    message_id: UUID
    recipient_id: UUID

@dataclass(frozen=True)
class MarkMessageReadCommand:
    message_id: UUID
    reader_id: UUID


# ───────────────────────────────────────────────────────────────────────────
#  Attachments
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AddAttachmentCommand:
    message_id: UUID
    uploader_id: UUID
    file_name: str
    size: int
    mime_type: str
    type_: str                        # "IMAGE" | "VIDEO" | "AUDIO" | "FILE"
    width: Optional[int] = None
    height: Optional[int] = None
    duration_sec: Optional[float] = None

@dataclass(frozen=True)
class RemoveAttachmentCommand:
    attachment_id: UUID
    remover_id: UUID


# ───────────────────────────────────────────────────────────────────────────
#  Reactions
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AddReactionCommand:
    message_id: UUID
    chat_id: UUID
    user_id: UUID
    emoji: str

@dataclass(frozen=True)
class RemoveReactionCommand:
    message_id: UUID
    chat_id: UUID
    user_id: UUID
    emoji: str


# ───────────────────────────────────────────────────────────────────────────
#  Notifications
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class CreateNotificationCommand:
    user_id: UUID
    notif_type: str                   # "NEW_MESSAGE", "INVITE", ...
    payload: dict

@dataclass(frozen=True)
class MarkNotificationReadCommand:
    notification_id: UUID
    user_id: UUID


# ───────────────────────────────────────────────────────────────────────────
#  Presence / Status
# ───────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class UpdateUserStatusCommand:
    user_id: UUID
    new_status: str                   # "ONLINE" | "AWAY" | "DND" | "OFFLINE"
