import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Default to SQLite for fast local development, but easily configurable for PostgreSQL / Supabase
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./seo_audit.db")

# SQLite needs check_same_thread=False
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import text

def init_db():
    Base.metadata.create_all(bind=engine)
    # Ensure new columns exist on legacy SQLite/Postgres tables
    with engine.connect() as conn:
        for col_name, col_type in [
            ("observed_value", "TEXT"),
            ("evidence", "TEXT"),
            ("verification_status", "VARCHAR(50) DEFAULT 'verified'")
        ]:
            try:
                conn.execute(text(f"ALTER TABLE seo_issues ADD COLUMN {col_name} {col_type}"))
                conn.commit()
            except Exception:
                pass
