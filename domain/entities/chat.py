# domain/entities/chat.py
from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum, auto
from typing import List
from entities.chat_membership import ChatMembership


class ChatType(Enum):
    PRIVATE = auto()
    GROUP = auto()


@dataclass
class Chat:
    id: UUID
    type: ChatType
    title: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
    members: List[ChatMembership] = field(default_factory=list)

    def add_member(self, member: ChatMembership) -> None:
        if self.has_member(member.user_id):
            raise ValueError(f"User {member.user_id} is already in the chat")
        self.members.append(member)
        self.updated_at = datetime.utcnow()

    def remove_member(self, user_id: UUID) -> None:
        if not self.has_member(user_id):
            raise ValueError(f"User {user_id} is not in the chat")
        self.members = [m for m in self.members if m.user_id != user_id]
        self.updated_at = datetime.utcnow()

    def is_empty(self) -> bool:
        return len(self.members) == 0

    def has_member(self, user_id: UUID) -> bool:
        return any(m.user_id == user_id for m in self.members)

    def get_member(self, user_id: UUID) -> ChatMembership | None:
        return next((m for m in self.members if m.user_id == user_id), None)

    def update_title(self, new_title: str) -> None:
        if not new_title:
            raise ValueError("Chat title cannot be empty")
        self.title = new_title
        self.updated_at = datetime.utcnow()

    @staticmethod
    def new(chat_type: ChatType, title: str) -> Chat:
        if not title:
            raise ValueError("Chat title cannot be empty")
        return Chat(id=uuid4(), type=chat_type, title=title)