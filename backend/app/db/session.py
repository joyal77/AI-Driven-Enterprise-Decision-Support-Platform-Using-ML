import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load .env if present
try:
    from dotenv import load_dotenv
    _bdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    _proot = os.path.dirname(_bdir)
    load_dotenv(os.path.join(_bdir, ".env"))
    load_dotenv(os.path.join(_proot, ".env"))
    load_dotenv()
except ImportError:
    pass

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
default_sqlite_path = os.path.join(backend_dir, "ecommerce_churn.db")

raw_db_url = os.getenv("DATABASE_URL")

if raw_db_url:
    # Standardize Supabase / PostgreSQL URLs for psycopg v3 and SQLAlchemy 2.0+
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif raw_db_url.startswith("postgresql://") and not raw_db_url.startswith("postgresql+"):
        raw_db_url = raw_db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    DATABASE_URL = raw_db_url
else:
    # Legacy fallback: construct connection from individual DB_* environment variables if provided
    db_host = os.getenv("DB_HOST")
    if db_host and db_host != "localhost":
        db_user = os.getenv("DB_USER", "postgres")
        db_pass = os.getenv("DB_PASSWORD", "")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "postgres")
        DATABASE_URL = f"postgresql+psycopg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    else:
        DATABASE_URL = f"sqlite:///{default_sqlite_path}"

# Initialize engine with dialect-specific connection arguments
try:
    if "sqlite" in DATABASE_URL:
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    elif "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
        engine = create_engine(
            DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_recycle=300,
            pool_pre_ping=True
        )
        with engine.connect() as conn:
            pass
        safe_host = DATABASE_URL.split("@")[-1].split("/")[0] if "@" in DATABASE_URL else "PostgreSQL"
        print(f"[Database] Successfully connected to Supabase PostgreSQL ({safe_host}).")
    else:
        engine = create_engine(
            DATABASE_URL,
            pool_recycle=3600,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5}
        )
        with engine.connect() as conn:
            pass
except Exception as e:
    safe_db_desc = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
    print(f"[Database Warning] Connection to {safe_db_desc} failed ({e}). Falling back to local database.")
    DATABASE_URL = f"sqlite:///{default_sqlite_path}"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
