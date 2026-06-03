from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool

from app.config import settings

DATABASE_URL = settings.database_url

if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL.replace("+aiosqlite", "").replace("asyncpg", "psycopg2"),
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
        poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
        echo=settings.debug,
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
        echo=settings.debug,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
