# domain/entities/attachment.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import PurePosixPath
from typing import Optional
from uuid import UUID, uuid4


class AttachmentType(Enum):
    IMAGE = auto()
    VIDEO = auto()
    AUDIO = auto()
    FILE  = auto()          # any other file type (PDF, ZIP, etc.)


_MAX_SIZE_BYTES = 25 * 1024 * 1024           # 25 MB system-wide limit


@dataclass
class Attachment:
    # ── core fields ──────────────────────────────────────────────────────
    id: UUID
    message_id: UUID
    type: AttachmentType
    file_name: str                            # name without path
    url: PurePosixPath                        # path/URL in object storage
    size: int                                 # bytes
    mime_type: str

    # ── metadata ─────────────────────────────────────────────────────────
    created_at: datetime = field(default_factory=datetime.utcnow)
    uploaded_at: Optional[datetime] = None
    width: Optional[int] = None              # for IMAGE/VIDEO
    height: Optional[int] = None
    duration_sec: Optional[float] = None     # for AUDIO/VIDEO

    # ── domain behavior ─────────────────────────────────────────────────
    def mark_uploaded(self, url: str) -> None:
        """Mark the file as uploaded and store the public URL."""
        if self.uploaded_at is not None:
            raise ValueError("Attachment already uploaded")
        self.url = PurePosixPath(url)
        self.uploaded_at = datetime.utcnow()

    # — helper predicates ——————————————————————————————
    def is_image(self) -> bool:
        return self.type is AttachmentType.IMAGE

    def is_audio(self) -> bool:
        return self.type is AttachmentType.AUDIO

    def is_video(self) -> bool:
        return self.type is AttachmentType.VIDEO

    def is_previewable(self) -> bool:
        """True if the chat UI can show an inline preview."""
        return self.type in {AttachmentType.IMAGE, AttachmentType.VIDEO}

    def validate_size(self, max_bytes: int = _MAX_SIZE_BYTES) -> None:
        """Ensure the file does not exceed the configured limit."""
        if self.size > max_bytes:
            raise ValueError(
                f"Attachment size {self.size} exceeds limit {max_bytes}"
            )

    # ── factory ─────────────────────────────────────────────────────────
    @staticmethod
    def new(
        message_id: UUID,
        type_: AttachmentType,
        file_name: str,
        size: int,
        mime_type: str,
        *,
        width: int | None = None,
        height: int | None = None,
        duration_sec: float | None = None,
    ) -> "Attachment":
        if not file_name:
            raise ValueError("file_name cannot be empty")
        if size <= 0:
            raise ValueError("size must be positive")

        att = Attachment(
            id=uuid4(),
            message_id=message_id,
            type=type_,
            file_name=file_name,
            url=PurePosixPath("/upload/pending"),  # temp placeholder
            size=size,
            mime_type=mime_type,
            width=width,
            height=height,
            duration_sec=duration_sec,
        )
        att.validate_size()  # early size validation
        return att
