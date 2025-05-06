"""
infrastructure/persistence/sqlalchemy/mappers.py
Explicit, readable converters between domain entities (pure dataclasses)
and SQLAlchemy ORM models.
"""

from __future__ import annotations

from typing import List

from domain.entities import (
    message as ent_msg,
    attachment as ent_att,
    chat as ent_chat,
    chat_membership as ent_mem,
    user as ent_user,
    notification as ent_notif,
)
from infrastructure.persistence.sqlalchemy.repos import (
    MessageModel,
    AttachmentModel,
    ChatModel,
    ChatMemberModel,
    UserModel,
    NotificationModel,
)


# ───────────────────────────────────────────────────────────────────────────
#  Attachment
# ───────────────────────────────────────────────────────────────────────────

def attachment_to_model(a: ent_att.Attachment) -> AttachmentModel:
    return AttachmentModel(
        id=a.id,
        message_id=a.message_id,
        type=a.type_.name,
        file_name=a.file_name,
        url=str(a.url),
        size=a.size,
        mime_type=a.mime_type,
        width=a.width,
        height=a.height,
        duration_sec=a.duration_sec,
        created_at=a.created_at,
        uploaded_at=a.uploaded_at,
    )


def model_to_attachment(m: AttachmentModel) -> ent_att.Attachment:
    return ent_att.Attachment(
        id=m.id,
        message_id=m.message_id,
        type_=ent_att.AttachmentType(m.type),
        file_name=m.file_name,
        url=m.url,
        size=m.size,
        mime_type=m.mime_type,
        width=m.width,
        height=m.height,
        duration_sec=m.duration_sec,
        created_at=m.created_at,
        uploaded_at=m.uploaded_at,
    )


# ───────────────────────────────────────────────────────────────────────────
#  Message
# ───────────────────────────────────────────────────────────────────────────

def message_to_model(e: ent_msg.Message) -> MessageModel:
    m = MessageModel(
        id=e.id,
        chat_id=e.chat_id,
        sender_id=e.sender_id,
        text=e.text,
        status=e.status.name,
        reply_to_id=e.reply_to_id,
        created_at=e.created_at,
        edited_at=e.edited_at,
        deleted_at=e.deleted_at,
    )
    m.attachments = [attachment_to_model(a) for a in e.attachments]
    return m


def model_to_message(m: MessageModel) -> ent_msg.Message:
    return ent_msg.Message(
        id=m.id,
        chat_id=m.chat_id,
        sender_id=m.sender_id,
        text=m.text,
        status=ent_msg.MessageStatus(m.status),
        reply_to_id=m.reply_to_id,
        created_at=m.created_at,
        edited_at=m.edited_at,
        deleted_at=m.deleted_at,
        attachments=[model_to_attachment(a) for a in m.attachments],
    )


# ───────────────────────────────────────────────────────────────────────────
#  ChatMembership
# ───────────────────────────────────────────────────────────────────────────

def membership_to_model(mem: ent_mem.ChatMembership) -> ChatMemberModel:
    return ChatMemberModel(
        chat_id=mem.chat_id,
        user_id=mem.user_id,
        role=mem.role.name,
        joined_at=mem.joined_at,
        muted_until=mem.muted_until,
    )


def model_to_membership(m: ChatMemberModel) -> ent_mem.ChatMembership:
    return ent_mem.ChatMembership(
        chat_id=m.chat_id,
        user_id=m.user_id,
        role=ent_mem.ChatRole(m.role),
        joined_at=m.joined_at,
        muted_until=m.muted_until,
    )


# ───────────────────────────────────────────────────────────────────────────
#  Chat
# ───────────────────────────────────────────────────────────────────────────

def chat_to_model(c: ent_chat.Chat) -> ChatModel:
    model = ChatModel(
        id=c.id,
        type=c.type.name,
        title=c.title,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )
    model.members = [membership_to_model(m) for m in c.members]
    return model


def model_to_chat(m: ChatModel) -> ent_chat.Chat:
    members = [model_to_membership(cm) for cm in m.members]
    return ent_chat.Chat(
        id=m.id,
        type=ent_chat.ChatType(m.type),
        title=m.title,
        created_at=m.created_at,
        updated_at=m.updated_at,
        members=members,
    )


# ───────────────────────────────────────────────────────────────────────────
#  User
# ───────────────────────────────────────────────────────────────────────────

def user_to_model(u: ent_user.User) -> UserModel:
    return UserModel(
        id=u.id,
        username=u.username,
        email=u.email,
        password_hash=u.password_hash,
        display_name=u.display_name,
        avatar_url=u.avatar_url,
        status=u.status.name,
        created_at=u.created_at,
        last_seen=u.last_seen,
        is_active=u.is_active,
    )


def model_to_user(m: UserModel) -> ent_user.User:
    return ent_user.User(
        id=m.id,
        username=m.username,
        email=m.email,
        password_hash=m.password_hash,
        display_name=m.display_name,
        avatar_url=m.avatar_url,
        status=ent_user.UserStatus(m.status),
        created_at=m.created_at,
        last_seen=m.last_seen,
        is_active=m.is_active,
    )


# ───────────────────────────────────────────────────────────────────────────
#  Notification
# ───────────────────────────────────────────────────────────────────────────

def notification_to_model(n: ent_notif.Notification) -> NotificationModel:
    return NotificationModel(
        id=n.id,
        user_id=n.user_id,
        type=n.type.name,
        payload=n.payload,
        created_at=n.created_at,
        read_at=n.read_at,
        seen_at=n.seen_at,
        is_sent=n.is_sent,
    )


def model_to_notification(m: NotificationModel) -> ent_notif.Notification:
    return ent_notif.Notification(
        id=m.id,
        user_id=m.user_id,
        type=ent_notif.NotificationType(m.type),
        payload=m.payload,
        created_at=m.created_at,
        read_at=m.read_at,
        seen_at=m.seen_at,
        is_sent=m.is_sent,
    )
