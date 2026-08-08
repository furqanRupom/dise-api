from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# pool_pre_ping: checks a connection is still alive before handing it out.
# Without it, a connection Postgres silently dropped (idle timeout, restart,
# etc.) surfaces as an OperationalError on first use instead of being
# detected and transparently replaced.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """Single source of truth for the ORM registry - every model imports
    Base from here, never redefines it elsewhere. Using the SQLAlchemy 2.0
    class-based style (instead of the legacy declarative_base() factory)
    to match the typed Mapped[...] / mapped_column() style used throughout
    every model.
    """


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables in the database.

    Dev/test bootstrapping only. If Alembic migrations are in use anywhere
    (e.g. for the btree_gist extension the ExcludeConstraints need), don't
    call this against an environment Alembic also manages - the two can
    drift out of sync with each other.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all tables in the database"""
    Base.metadata.drop_all(bind=engine)
