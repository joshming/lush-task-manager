from sqlalchemy import Text, Enum, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimeTracked
from app.enums import ProjectStatus


class Project(TimeTracked, Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, native_enum=False),
        default=ProjectStatus.OPEN
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
