import os
from typing import Optional, List


class Settings:
    # Google Cloud & ADK
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")

    # ADK Configuration
    MODEL_NAME: str = "gemini-2.0-flash"
    EMBEDDING_MODEL: str = "gemini-embedding-001"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5433/tbc_bank")

    # Vector Database with Google Embeddings
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    EMBEDDING_DIMENSION: int = 3072  # gemini-embedding-001 default dimension

    # Session and Memory Configuration
    SESSION_TIMEOUT_HOURS: int = 24
    MAX_SESSIONS_PER_USER: int = 10
    MEMORY_RETENTION_DAYS: int = 365

    # Application
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080"
    ]

    # Feature Flags
    ENABLE_MEMORY_PERSISTENCE: bool = os.getenv("ENABLE_MEMORY_PERSISTENCE", "true").lower() == "true"
    ENABLE_RAG_SEARCH: bool = os.getenv("ENABLE_RAG_SEARCH", "true").lower() == "true"
    ENABLE_SESSION_ANALYTICS: bool = os.getenv("ENABLE_SESSION_ANALYTICS", "false").lower() == "true"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_CHAT_LOGGING: bool = os.getenv("ENABLE_CHAT_LOGGING", "true").lower() == "true"


settings = Settings()

# Validation
if not settings.GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

if not settings.DATABASE_URL:
    print("⚠️  DATABASE_URL not set, using SQLite fallback")
    settings.DATABASE_URL = "sqlite:///./tbc_bank.db"
