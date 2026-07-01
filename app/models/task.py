from sqlalchemy import Enum, Text, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import TaskStatus, Priority
from app.models.base import Base, TimeTracked


class Task(TimeTracked, Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str]
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, native_enum=False),
        default=TaskStatus.TODO
    )
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, native_enum=False),
        default=Priority.MEDIUM
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    assigned_to: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
