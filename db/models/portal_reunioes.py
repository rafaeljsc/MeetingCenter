from __future__ import annotations

from sqlalchemy import JSON, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from db.base import UUIDAuditBase


class PortalReunioes(UUIDAuditBase):
    __tablename__ = "portal_reunioes"

    call_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True, unique=True)
    call_title: Mapped[str] = mapped_column(String(255), nullable=True)
    start_date: Mapped[str] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[str] = mapped_column(DateTime, nullable=False)
    call_duration_min: Mapped[int] = mapped_column(Integer, nullable=True)
    organizer: Mapped[str] = mapped_column(String(255), nullable=True, index=True)

    participants_count: Mapped[int] = mapped_column(Integer, nullable=True)
    participants_name: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    participants_mail: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)

    invites_count: Mapped[int] = mapped_column(Integer, nullable=True)
    invites_name: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    invites_mail: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)

    companies: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=True)
    goal: Mapped[str] = mapped_column(Text, nullable=True)
    raw_transcript: Mapped[list[dict]] = mapped_column(JSON, nullable=False)

    topics: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    tasks: Mapped[list[dict]] = mapped_column(JSON, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<PortalReunioes call_id={self.call_id}>"
