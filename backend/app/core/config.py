import os
from typing import List, Optional
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "LibraSync - Intelligent RFID-Enabled ILMS"
    API_V1_STR: str = "/api/v1"
    
    # Security & JWT
    SECRET_KEY: str = "librasync-enterprise-grade-secret-key-super-secure-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12  # 12 hours
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # Database Configuration (PostgreSQL primary, SQLite fallback for dev)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgrespassword"
    POSTGRES_DB: str = "librasync"
    DATABASE_URL: Optional[str] = None
    
    # RFID & Gate Configuration
    RFID_READER_TIMEOUT_SEC: float = 3.0
    GATE_ALARM_AUTO_DISARM_SEC: int = 15
    DEFAULT_BORROW_DAYS: int = 14
    MAX_BOOKS_PER_MEMBER: int = 4
    FINE_PER_DAY: float = 2.0
    MAX_OVERDUE_FINE_LIMIT: float = 100.0  # Member blocked if total fines exceed this
    
    # ILMS Boundary (Strict read-only/documented adapter mode)
    ILMS_ADAPTER_TYPE: str = "mock"  # "mock", "ncip", "sip2"
    ILMS_ENDPOINT_URL: str = "http://ilms.local:8080/ncip"

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="allow")


settings = Settings()

