"""DB engine/session. Postgres 17 + pgvector locally; same URL scheme for RDS.

SQLite remains a zero-dependency fallback when DATABASE_URL is unset.
"""
import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

url = os.getenv("DATABASE_URL", settings.database_url)
IS_PG = url.startswith("postgresql")
kwargs = {"connect_args": {"check_same_thread": False}} if url.startswith("sqlite") else {}

engine = create_engine(url, **kwargs)

if IS_PG:
    @event.listens_for(engine, "connect")
    def _enable_vector(dbapi_conn, _rec):
        with dbapi_conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
