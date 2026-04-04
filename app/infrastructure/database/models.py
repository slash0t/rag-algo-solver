import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    queries: Mapped[list["QueryModel"]] = relationship(back_populates="user")


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255))
    text: Mapped[str] = mapped_column(Text)
    task_url: Mapped[str | None] = mapped_column(String(500))
    solution: Mapped[str | None] = mapped_column(Text)
    solution_url: Mapped[str | None] = mapped_column(String(500))
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class QueryModel(Base):
    __tablename__ = "queries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(Text)
    response_text: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    responded_at: Mapped[datetime | None] = mapped_column()

    user: Mapped["UserModel"] = relationship(back_populates="queries")
    similar_tasks: Mapped[list["TaskModel"]] = relationship(
        secondary="query_similar_tasks",
    )


class QuerySimilarTaskModel(Base):
    __tablename__ = "query_similar_tasks"
    __table_args__ = (
        PrimaryKeyConstraint("query_id", "task_id"),
    )

    query_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("queries.id"))
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tasks.id"))
