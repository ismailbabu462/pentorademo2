from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone
import uuid

from config import DATABASE_URL

# Create SQLAlchemy engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # For MySQL and other databases
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # SECURITY: Store hashed passwords
    tier = Column(String(50), default="essential")
    subscription_valid_until = Column(DateTime, nullable=True)
    last_tool_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    projects = relationship("Project", back_populates="user")
    notes = relationship("Note", back_populates="user")

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
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="projects")
    targets = relationship("Target", back_populates="project")
    notes = relationship("Note", back_populates="project")

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
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
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
    project = relationship("Project")
    user = relationship("User")

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
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    project = relationship("Project")
    user = relationship("User")

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
def init_db():
    create_tables()
    db_type = "MySQL" if DATABASE_URL.startswith("mysql") else "SQLite"
    print(f"✅ {db_type} database initialized successfully")
