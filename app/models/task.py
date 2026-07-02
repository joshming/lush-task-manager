from sqlalchemy import Enum, Text, ForeignKey, BigInteger, UniqueConstraint, Index, text, func
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
    version: Mapped[int] = mapped_column(server_default="1")
    normalized_title: Mapped[str] = mapped_column(nullable=True)

    __mapper_args__ = {
        "version_id_col": version,
        "version_id_generator": lambda v: 1 if not v else v + 1,
    }

    __table_args__ = (
        UniqueConstraint("normalized_title", "project_id"),
    )