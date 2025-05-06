"""
outbox_dispatch.py
──────────────────
A *pure* Outbox‑to‑Kafka dispatcher:

    • fetch_pending()   →  list[DomainEvent]
    • _publish(event)   →  kafka_producer.send(...)
    • mark_dispatched() →  flag row as sent

This file has **no** knowledge about how sessions or producers are built;
they are supplied via call‑ables injected from your bootstrap code.
"""

from __future__ import annotations

import time
from contextlib import suppress
from typing import Callable

from domain.events import DomainEvent
from application.unit_of_work import UnitOfWork    # interface, not a concrete class
from kafka import KafkaProducer


class OutboxDispatchWorker:
    """Continuously moves events from the DB outbox table to Kafka."""

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        kafka_producer: KafkaProducer,
        topic: str = "messages",
        batch: int = 100,
        idle_sleep: float = 0.2,
    ):
        self._uow_factory = uow_factory
        self._kafka = kafka_producer
        self._topic = topic
        self._limit = batch
        self._idle = idle_sleep
        self._running = True

    # ----------------------------------------------------------------- start
    def run(self) -> None:
        """Block the current thread until stop() is called."""
        while self._running:
            dispatched_any = self._cycle()
            if not dispatched_any:
                time.sleep(self._idle)

    # ----------------------------------------------------------------- stop
    def stop(self) -> None:
        self._running = False
        with suppress(Exception):
            self._kafka.flush(5)
            self._kafka.close(10)

    # ----------------------------------------------------------------- cycle
    def _cycle(self) -> bool:
        """Process a single batch; return True if anything was dispatched."""
        with self._uow_factory() as uow:
            events = uow.outbox.fetch_pending(self._limit)
            if not events:
                return False

            for ev in events:
                self._publish(ev)
                uow.outbox.mark_dispatched(ev.id)
        # flush outside the transaction
        with suppress(Exception):
            self._kafka.flush(1)
        return True

    # ---------------------------------------------------------------- publish
    def _publish(self, ev: DomainEvent) -> None:
        """Send event JSON to Kafka. Partition key = chat_id or 'system'."""
        key = getattr(ev, "chat_id", "system")
        self._kafka.send(self._topic, key=str(key), value=ev.to_dict())
