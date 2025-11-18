"""
Database models and connection management for the AI Assistant.

This module defines SQLAlchemy models for users, tool connections, workflows,
workflow executions, and conversations. It also provides database initialization
and session management for FastAPI.
"""

import logging
from datetime import datetime
from typing import Optional, Generator

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Index,
    JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

Base = declarative_base()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    default_local_model: str = "llama3.1"

    # Database
    database_url: str = "sqlite:///./ai_assistant.db"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # OAuth (optional for MVP)
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: Optional[str] = None

    salesforce_client_id: Optional[str] = None
    salesforce_client_secret: Optional[str] = None
    salesforce_redirect_uri: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()


# Create database engine
# For SQLite, we need to enable check_same_thread=False for FastAPI
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=False,  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class User(Base):
    """
    User model for multi-user support (future-proofing).

    Attributes:
        id: Primary key
        email: User's email address (unique)
        created_at: Account creation timestamp
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    tool_connections = relationship("ToolConnection", back_populates="user", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"


class ToolConnection(Base):
    """
    OAuth connections to external tools (Gmail, Calendar, Salesforce).

    Attributes:
        id: Primary key
        user_id: Foreign key to User
        service_name: Tool identifier (gmail/calendar/salesforce)
        display_name: Human-readable name for this connection
        is_connected: Whether the connection is active
        auth_data: Encrypted JSON containing OAuth tokens and metadata
        last_connected: Last successful connection timestamp
        created_at: Connection creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "tool_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    service_name = Column(String, nullable=False, index=True)  # gmail, calendar, salesforce
    display_name = Column(String, nullable=False)
    is_connected = Column(Boolean, default=False, nullable=False)
    auth_data = Column(Text, nullable=True)  # Encrypted JSON for OAuth tokens
    last_connected = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="tool_connections")

    # Indexes
    __table_args__ = (
        Index("idx_tool_user_service", "user_id", "service_name"),
    )

    def __repr__(self) -> str:
        return f"<ToolConnection(id={self.id}, service='{self.service_name}', connected={self.is_connected})>"


class Workflow(Base):
    """
    User-defined workflows for automation.

    Attributes:
        id: Primary key
        user_id: Foreign key to User
        name: Workflow name
        description: Human-readable description
        trigger: JSON defining when to run (schedule/manual/event)
        actions: JSON array of actions to execute
        is_active: Whether the workflow is enabled
        use_local_llm: Whether to use local LLM for this workflow
        created_at: Creation timestamp
        updated_at: Last update timestamp
        last_run: Last execution timestamp
    """

    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    trigger = Column(JSON, nullable=False)  # {type: "schedule/manual/event", config: {...}}
    actions = Column(JSON, nullable=False)  # [{tool: "gmail", action: "send", params: {...}}, ...]
    is_active = Column(Boolean, default=True, nullable=False)
    use_local_llm = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_run = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="workflows")
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_workflow_user_active", "user_id", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Workflow(id={self.id}, name='{self.name}', active={self.is_active})>"


class WorkflowExecution(Base):
    """
    Log of workflow execution history.

    Attributes:
        id: Primary key
        workflow_id: Foreign key to Workflow
        status: Execution status (pending/running/success/failed)
        started_at: Execution start timestamp
        completed_at: Execution completion timestamp
        actions_executed: JSON array of executed actions
        results: JSON containing execution results
        error_message: Error message if execution failed
        model_used: LLM model used for this execution
        tokens_used: Token count for LLM calls
    """

    __tablename__ = "workflow_executions"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False, index=True)
    status = Column(String, nullable=False, index=True)  # pending, running, success, failed
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    actions_executed = Column(JSON, nullable=True)  # [{action: "...", status: "...", result: "..."}, ...]
    results = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    model_used = Column(String, nullable=True)
    tokens_used = Column(Integer, nullable=True)

    # Relationships
    workflow = relationship("Workflow", back_populates="executions")

    # Indexes
    __table_args__ = (
        Index("idx_execution_workflow_status", "workflow_id", "status"),
        Index("idx_execution_started", "started_at"),
    )

    def __repr__(self) -> str:
        return f"<WorkflowExecution(id={self.id}, workflow_id={self.workflow_id}, status='{self.status}')>"


class Conversation(Base):
    """
    Chat conversation history with the AI assistant.

    Attributes:
        id: Primary key
        user_id: Foreign key to User
        conversation_id: Unique conversation identifier
        messages: JSON array of messages in this conversation
        created_at: Conversation start timestamp
        updated_at: Last message timestamp
    """

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    conversation_id = Column(String, unique=True, index=True, nullable=False)
    messages = Column(JSON, nullable=False, default=list)  # [{role: "user/assistant", content: "...", timestamp: "..."}, ...]
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="conversations")

    # Indexes
    __table_args__ = (
        Index("idx_conversation_user", "user_id"),
        Index("idx_conversation_updated", "updated_at"),
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, conversation_id='{self.conversation_id}')>"


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This function should be called on application startup to ensure
    all database tables exist.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_create_user(db: Session, email: str = "default@local") -> User:
    """
    Get or create the default user for MVP (single-user mode).

    Args:
        db: Database session
        email: User email (defaults to local user)

    Returns:
        User: The user instance
    """
    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created default user: {email}")

    return user
