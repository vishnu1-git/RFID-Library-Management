import os
import socket
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger("librasync.db")


def is_postgres_port_open(host: str, port: int) -> bool:
    """Fast non-blocking probe to verify if PostgreSQL service/container is listening."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)
        res = sock.connect_ex((host, port))
        sock.close()
        return res == 0
    except Exception:
        return False


def get_database_url() -> str:
    # 1. Direct explicit env var
    if settings.DATABASE_URL:
        return settings.DATABASE_URL
    
    # 2. Check if PostgreSQL container/service is running
    pg_url = f"postgresql+psycopg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    
    if is_postgres_port_open(settings.POSTGRES_SERVER, settings.POSTGRES_PORT):
        try:
            test_engine = create_engine(pg_url)
            with test_engine.connect():
                logger.info("Successfully connected to primary PostgreSQL database.")
                return pg_url
        except Exception as exc:
            logger.warning(f"PostgreSQL port open but connection failed ({exc}). Using SQLite fallback.")
    else:
        logger.info(
            f"PostgreSQL on {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT} is not currently running. "
            "Using local development SQLite database (librasync.db). Start Docker Desktop to use PostgreSQL 16."
        )

    # 3. Fallback SQLite
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "librasync.db")
    return f"sqlite:///{db_path}"


DATABASE_URL = get_database_url()

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
