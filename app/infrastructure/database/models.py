import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, ForeignKey, String, Text, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class ProcessingStatus(StrEnum):
    PENDING = "pending"
    ENRICHING = "enriching"
    SEARCHING = "searching"
    COMPOSING = "composing"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    queries: Mapped[list["Query"]] = relationship(back_populates="user")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255))
    text: Mapped[str] = mapped_column(Text)
    task_url: Mapped[str | None] = mapped_column(String(500))
    solution: Mapped[str | None] = mapped_column(Text)
    solution_url: Mapped[str | None] = mapped_column(String(500))
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class Query(Base):
    __tablename__ = "queries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(Text)
    response_text: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    responded_at: Mapped[datetime | None] = mapped_column()

    user: Mapped["User"] = relationship(back_populates="queries")
    similar_tasks: Mapped[list["Task"]] = relationship(
        secondary="query_similar_tasks",
    )
    processing: Mapped["QueryProcessing | None"] = relationship(
        back_populates="query",
        uselist=False,
    )


class QueryProcessing(Base):
    __tablename__ = "query_processing"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    query_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("queries.id"),
        unique=True,
    )
    original_text: Mapped[str] = mapped_column(Text)
    enriched_text: Mapped[str | None] = mapped_column(Text)
    task_context: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(50),
        default=ProcessingStatus.PENDING,
    )
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=datetime.utcnow)

    query: Mapped["Query"] = relationship(back_populates="processing")


class QuerySimilarTask(Base):
    __tablename__ = "query_similar_tasks"
    __table_args__ = (PrimaryKeyConstraint("query_id", "task_id"),)

    query_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("queries.id"))
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tasks.id"))
