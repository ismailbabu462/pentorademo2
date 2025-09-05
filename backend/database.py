import logging
import time
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from config import DATABASE_URL

logger = logging.getLogger(__name__)


def create_database_engine():
    """Create database engine with retry mechanism"""
    max_retries = 30  # 30 retries
    retry_delay = 2  # 2 seconds between retries

    for attempt in range(max_retries):
        try:
            if DATABASE_URL.startswith("sqlite"):
                return create_engine(
                    DATABASE_URL, connect_args={"check_same_thread": False}
                )
            else:
                # For MySQL and other databases - with connection pool settings from config
                from config import DATABASE_POOL_CONFIG

                engine = create_engine(
                    DATABASE_URL,
                    **DATABASE_POOL_CONFIG,
                    echo=False,  # Disable SQL logging for production
                    echo_pool=False,  # Disable pool logging
                )

                # Test the connection with timeout
                with engine.connect() as conn:
                    from sqlalchemy import text

                    conn.execute(text("SELECT 1"))

                logger.info("✅ Database connection established successfully")
                return engine

        except OperationalError as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"⚠️ Database connection failed (attempt {attempt + 1}/{max_retries}): {e}"
                )
                logger.info(f"🔄 Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(
                    f"❌ Failed to connect to database after {max_retries} attempts: {e}"
                )
                raise
        except Exception as e:
            logger.error(f"❌ Unexpected error during database connection: {e}")
            raise


# Create SQLAlchemy engine with retry mechanism
engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(
        String(255), nullable=True
    )  # SECURITY: Store hashed passwords
    tier = Column(String(50), default="essential")
    subscription_valid_until = Column(DateTime, nullable=True)
    last_tool_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    projects = relationship("Project", back_populates="user")
    notes = relationship("Note", back_populates="user")
    tool_outputs = relationship("ToolOutput", back_populates="user")
    vulnerabilities = relationship("Vulnerability", back_populates="user")
    devices = relationship("Device", back_populates="user")


class Device(Base):
    __tablename__ = "devices"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = Column(
        String(36), unique=True, nullable=False
    )  # Unique device identifier
    device_name = Column(String(100), nullable=True)  # User-friendly device name
    device_type = Column(String(50), nullable=True)  # web, mobile, desktop
    jwt_secret_key = Column(String(255), nullable=False)  # Device-specific JWT secret
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="devices")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="planning")
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    team_members = Column(Text, nullable=True)  # JSON string
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="projects")
    targets = relationship("Target", back_populates="project")
    notes = relationship("Note", back_populates="project")
    tool_outputs = relationship("ToolOutput", back_populates="project")
    vulnerabilities = relationship("Vulnerability", back_populates="project")


class Target(Base):
    __tablename__ = "targets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    target_type = Column(String(50), nullable=False)  # domain, ip, cidr, url
    value = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    is_in_scope = Column(Boolean, default=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    project = relationship("Project", back_populates="targets")


class Note(Base):
    __tablename__ = "notes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(Text, nullable=True)  # JSON string
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    project = relationship("Project", back_populates="notes")
    user = relationship("User", back_populates="notes")


class LicenseKey(Base):
    __tablename__ = "license_keys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key_hash = Column(String(255), unique=True, nullable=False)
    raw_key = Column(String(255), nullable=True)
    tier = Column(String(50), nullable=False)
    duration_days = Column(Integer, nullable=False)
    is_used = Column(Boolean, default=False)
    used_by_user_id = Column(String(36), nullable=True)
    used_at = Column(DateTime, nullable=True)
    created_for_user_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ToolOutput(Base):
    __tablename__ = "tool_outputs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tool_name = Column(String(100), nullable=False)
    target = Column(String(500), nullable=False)
    output = Column(Text, nullable=False)
    status = Column(String(50), default="completed")
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    project = relationship("Project", back_populates="tool_outputs")
    user = relationship("User", back_populates="tool_outputs")


class Vulnerability(Base):
    __tablename__ = "vulnerabilities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    payload = Column(Text, nullable=False)
    how_it_works = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False)  # critical, high, medium, low
    ai_analysis = Column(Text, nullable=True)  # AI-generated analysis
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    project = relationship("Project", back_populates="vulnerabilities")
    user = relationship("User", back_populates="vulnerabilities")


# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)


# Dependency to get database session
def get_db():
    # Lazy database initialization
    try:
        # Try to create tables if they don't exist
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning(f"⚠️ Database tables creation failed: {e}")
        # Continue anyway, tables might already exist

    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"❌ Database session error: {e}")
        try:
            db.rollback()
        except:
            pass
        raise
    finally:
        try:
            db.close()
        except Exception as e:
            logger.warning(f"⚠️ Error closing database session: {e}")


# Database context manager for safe operations
class DatabaseContext:
    def __init__(self):
        self.db = None

    def __enter__(self):
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            try:
                if exc_type:
                    self.db.rollback()
                else:
                    self.db.commit()
            except Exception as e:
                logger.error(f"❌ Error in database context: {e}")
                self.db.rollback()
            finally:
                try:
                    self.db.close()
                except Exception as e:
                    logger.warning(f"⚠️ Error closing database session: {e}")


# Initialize database
def init_db():
    try:
        create_tables()
        db_type = "MySQL" if DATABASE_URL.startswith("mysql") else "SQLite"
        logger.info(f"✅ {db_type} database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
