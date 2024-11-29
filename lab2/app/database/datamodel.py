from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Message(Base):
    __tablename__ = "message"
    __table_args__ = {"comment": "Table to store chat history"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="Unique message ID")
    role: Mapped[str] = mapped_column(
        String, nullable=False, comment="Role defining message ownership, possible: {human, assistant}."
    )
    content: Mapped[str] = mapped_column(String, nullable=False, comment="Message content")
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, comment="Datetime when the message was published"
    )

    def __repr__(self) -> str:
        return f"Message(id={self.id!r}, role={self.role!r}, content={self.content!r}, date={self.date!r})"
