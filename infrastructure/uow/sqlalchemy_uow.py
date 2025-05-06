# infrastructure/uow/sqlalchemy_uow.py
from __future__ import annotations

from datetime import datetime
from typing import Callable
from uuid import uuid4

from sqlalchemy.orm import Session

from application.unit_of_work import UnitOfWork
from domain.repositories import (
    MessageRepository,
    ChatRepository,
    UserRepository,
    NotificationRepository,
    AttachmentRepository,
    OutboxRepository,
)
from infrastructure.persistence.sqlalchemy import (
    message_repo,
    chat_repo,
    user_repo,
    notification_repo,
    attachment_repo,
    outbox_repo,
)

class SqlAlchemyUnitOfWork(UnitOfWork):
    """
    Wraps one SQLAlchemy session.  All repository instances share that session,
    therefore their work is committed / rolled back as a single DB transaction.
    """

    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory
        self.session: Session

        # repos will be set in __enter__
        self.messages: MessageRepository
        self.chats: ChatRepository
        self.users: UserRepository
        self.notifications: NotificationRepository
        self.attachments: AttachmentRepository
        self.outbox: OutboxRepository

    # ------------------------------------------------------------------ context
    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self._session_factory()

        # concrete repo implementations
        self.messages = message_repo.SqlMessageRepository(self.session)
        self.chats = chat_repo.SqlChatRepository(self.session)
        self.users = user_repo.SqlUserRepository(self.session)
        self.notifications = notification_repo.SqlNotificationRepository(self.session)
        self.attachments = attachment_repo.SqlAttachmentRepository(self.session)
        self.outbox = outbox_repo.SqlOutboxRepository(self.session)

        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.session.close()

    # ------------------------------------------------------------------ helpers
    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
