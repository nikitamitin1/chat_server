from abc import ABC, abstractmethod
from domain.repositories import *


# ──────────────────────────────────────────────────────────────────────────
# Unit of Work interface
# ──────────────────────────────────────────────────────────────────────────
class UnitOfWork(ABC):
    messages: MessageRepository
    chats: ChatRepository
    users: UserRepository
    notifications: NotificationRepository
    attachments: AttachmentRepository
    outbox: OutboxRepository

    @abstractmethod
    def __enter__(self) -> "UnitOfWork": ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...