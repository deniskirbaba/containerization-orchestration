import json
import os
from contextlib import contextmanager

from database.datamodel import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

dbschema = "public"
engine = create_engine(
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}",
    connect_args={
        "options": f"-csearch_path={dbschema}"
        # The parameters below have been proposed to try to eliminate `dead` sessions
        + " -c statement_timeout=60s"
        + " -c lock_timeout=60s"
        + " -c idle_in_transaction_session_timeout=60s"
        + " -c idle_session_timeout=60s"
    },
    json_serializer=lambda x: json.dumps(x, ensure_ascii=False),
    pool_pre_ping=True,
    pool_recycle=60,  # prevent the pool from using a particular connection that has passed a certain age (in sec)
)

Session = sessionmaker(engine)


@contextmanager
def get_database_session():
    """
    Provide a transactional scope around a series of operations.
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """
    Create all tables in the database based on the data models.
    """
    Base.metadata.create_all(engine, checkfirst=True)


if __name__ == "__main__":
    init_db()
