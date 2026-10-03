"""DB engine/session. SQLite for dev, Postgres (RDS) for prod via DATABASE_URL/PHARMX_DATABASE_URL."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

url = os.getenv("DATABASE_URL", settings.database_url)
kwargs = {"connect_args": {"check_same_thread": False}} if url.startswith("sqlite") else {}

engine = create_engine(url, **kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
