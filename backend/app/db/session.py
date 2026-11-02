import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load local .env if present (only applies when running locally)
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

# Detect runtime environment
is_render = bool(os.getenv("RENDER"))
is_production = is_render or os.getenv("ENV") in ("production", "prod") or os.getenv("ENVIRONMENT") in ("production", "prod")

# Support standard PostgreSQL environment variable names
raw_db_url = (
    os.getenv("DATABASE_URL")
    or os.getenv("TARGET_DATABASE_URL")
    or os.getenv("SUPABASE_DATABASE_URL")
    or os.getenv("POSTGRES_URL")
)

def normalize_database_url(url: str) -> str:
    """Sanitizes and normalizes database URLs for SQLAlchemy 2.0 and Psycopg 3."""
    if not url:
        return url
    
    # Strip any leading/trailing whitespace, newlines, and surrounding quotes
    url = url.strip().strip("'\"").strip()
    
    # Normalize PostgreSQL URL scheme to use psycopg v3 driver
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql+psycopg2://"):
        url = "postgresql+psycopg://" + url[len("postgresql+psycopg2://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    
    # Ensure sslmode=require for remote Supabase connections if not explicitly set
    if "postgresql" in url and ("supabase.com" in url or "pooler.supabase.com" in url):
        if "sslmode=" not in url:
            delimiter = "&" if "?" in url else "?"
            url = f"{url}{delimiter}sslmode=require"
            
    return url

DATABASE_URL = normalize_database_url(raw_db_url) if raw_db_url else None

# Fallback to individual DB_* parameters if DATABASE_URL was not directly passed
if not DATABASE_URL:
    db_host = os.getenv("DB_HOST")
    if db_host and db_host != "localhost":
        db_user = os.getenv("DB_USER", "postgres")
        db_pass = os.getenv("DB_PASSWORD", "")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "postgres")
        DATABASE_URL = f"postgresql+psycopg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}?sslmode=require"

# Check if PostgreSQL was intended
is_postgres_intended = bool(DATABASE_URL and ("postgresql" in DATABASE_URL or "postgres" in DATABASE_URL))

if not is_postgres_intended:
    if is_production:
        print("[Database Warning] Running in production/Render without a PostgreSQL connection URL. Falling back to local SQLite.")
    DATABASE_URL = f"sqlite:///{default_sqlite_path}"

# Initialize engine with dialect-specific connection arguments
connect_args = {}
engine_kwargs = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

if "sqlite" in DATABASE_URL:
    connect_args["check_same_thread"] = False
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    print(f"[Database] Connected to local SQLite database ({default_sqlite_path}).")
else:
    # PostgreSQL / Supabase Configuration
    connect_args["prepare_threshold"] = None  # Crucial for Supabase transaction & session poolers (PgBouncer/Supavisor)
    connect_args["connect_timeout"] = 15
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    
    try:
        engine = create_engine(DATABASE_URL, connect_args=connect_args, **engine_kwargs)
        # Verify active connection
        with engine.connect() as conn:
            pass
        safe_host = DATABASE_URL.split("@")[-1].split("/")[0] if "@" in DATABASE_URL else "PostgreSQL"
        print(f"[Database] Successfully connected to Supabase PostgreSQL ({safe_host}).")
    except Exception as e:
        safe_db_desc = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "PostgreSQL"
        print(f"[Database Error] Connection to {safe_db_desc} failed: {e}")
        
        # NEVER silently fall back to SQLite in production (Render) or when PostgreSQL was explicitly configured!
        if is_production or is_postgres_intended:
            raise RuntimeError(
                f"Failed to connect to configured PostgreSQL database ({safe_db_desc}): {e}. "
                "Silent fallback to SQLite is disabled in production to protect data integrity."
            )
        else:
            print("[Database Warning] Local development fallback to SQLite.")
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
