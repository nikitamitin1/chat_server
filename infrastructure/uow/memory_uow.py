# infrastructure/uow/memory_uow.py
from collections import defaultdict

from application.unit_of_work import UnitOfWork
from domain.repositories import (
    MessageRepository,
    ChatRepository,
    UserRepository,
    NotificationRepository,
    AttachmentRepository,
    OutboxRepository,
)
from infrastructure.persistence.memory import (
    message_repo,
    chat_repo,
    user_repo,
    notification_repo,
    attachment_repo,
    outbox_repo,
)


class InMemoryUnitOfWork(UnitOfWork):
    """
    Keeps plain‑Python dicts in memory; no transaction semantics needed,
    but we keep the same interface so that tests work exactly like prod code.
    """

    def __init__(self):
        self._store = defaultdict(dict)

        self.messages: MessageRepository = message_repo.InMemoryMessageRepository(
            self._store
        )
        self.chats: ChatRepository = chat_repo.InMemoryChatRepository(self._store)
        self.users: UserRepository = user_repo.InMemoryUserRepository(self._store)
        self.notifications: NotificationRepository = (
            notification_repo.InMemoryNotificationRepository(self._store)
        )
        self.attachments: AttachmentRepository = (
            attachment_repo.InMemoryAttachmentRepository(self._store)
        )
        self.outbox: OutboxRepository = outbox_repo.InMemoryOutboxRepository(self._store)

    # context manager does nothing but preserve the same API
    def __enter__(self) -> "InMemoryUnitOfWork":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        # no rollback/commit logic needed – simply drop in‑memory changes on test teardown
        pass

    def commit(self) -> None: ...
    def rollback(self) -> None: ...