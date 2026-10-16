import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

def get_engine():
    # Attempt to connect to configured DATABASE_URL (e.g. Postgres)
    try:
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3} if "postgresql" in settings.DATABASE_URL else {}
        )
        with engine.connect() as conn:
            logger.info("Successfully connected to primary database: %s", settings.DATABASE_URL)
        return engine
    except Exception as e:
        logger.warning(
            "Primary database connection (%s) failed: %s. Falling back to SQLite: %s",
            settings.DATABASE_URL, e, settings.SQLITE_FALLBACK_URL
        )
        sqlite_engine = create_engine(
            settings.SQLITE_FALLBACK_URL,
            connect_args={"check_same_thread": False}
        )
        return sqlite_engine

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
