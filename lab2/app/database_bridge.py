from datetime import datetime, timezone

from database.connection import get_database_session
from database.datamodel import Message
from sqlalchemy import delete, select


class DatabaseBridge:
    @staticmethod
    def add_message(content: str, role: str) -> None:
        """
        Adds message to the DB.
        """
        with get_database_session() as db_session:
            new_msg = Message(
                role=role,
                content=content,
                date=datetime.now(timezone.utc),
            )
            db_session.add(new_msg)

    @staticmethod
    def reset() -> None:
        """
        Remove all chat history from DB. Runs when user presses the 'reset' button.
        """
        with get_database_session() as db_session:
            db_session.execute(delete(Message))

    @staticmethod
    def get_history() -> list:
        """
        Return all history from DB.
        """
        with get_database_session() as db_session:
            result = db_session.execute(select(Message).order_by(Message.date)).scalars()
            hist = [{"role": msg.role, "content": msg.content} for msg in result]
        return hist
